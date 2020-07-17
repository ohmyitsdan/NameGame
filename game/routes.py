import random
import time
import threading
import json
from game import app, db
from flask import (render_template, redirect, url_for, flash, request, 
    make_response, jsonify, Response, render_template_string, 
    stream_with_context)
from game.largetemplates import timerTemplate
from game.forms import JoinGame, CreateGame, AddNames, Player, Teams
from game.models import User, Room, Names, Colours
from game.utils import (genRoomCode, getColours, teamColours, sendRoomCode,
    getUsernameFromCookie, userLookupFromCookie, roomFromCode, roomIdFromUserCookie,
    namesRemaining, rndScore, initPlayOrder, getNamefromId, getUserFromId,
    getNextPlayer, totalScore)




@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    form = JoinGame()
    if form.validate_on_submit():
        room = Room.query.filter_by(room_code=form.roomcode.data).first()
        if not room:
            flash(f'That is not a valid room code.', 'danger')
        else:
            username = form.username.data
            client = User(username=username, room_id=room.id, team=0, 
                play_order=0, in_play=0)
            db.session.add(client)
            db.session.commit()

            # Sets Cookie for User
            resp = make_response(redirect(url_for('addnames', roomCode=form.roomcode.data)))
            resp.set_cookie('user_id', str(client.id))
            return resp

    return render_template('home.html', form=form, legend='Name Game')

@app.route('/create', methods=['GET','POST'])
def create():
    form = CreateGame()
    if form.validate_on_submit():
        print(form.errors)
        noguess = form.guess_num.data
        username = form.username.data
        timeRem = form.timerem.data

        roomCode = genRoomCode()
        roomInst = Room(room_code=roomCode, num_teams=2, scorecard=False,
                full_time=timeRem,
                time_remaining=timeRem, names_per=noguess,
                roundNo=0, ct=0, timer_started=0, game_started=0)
        db.session.add(roomInst)
        db.session.commit()
        room = Room.query.filter_by(room_code=roomCode).first()

        client = User(username=username, room_id=room.id, team=0,
                play_order=0, in_play=0)
        db.session.add(client)
        db.session.commit()

        user = User.query.filter_by(username=username, room_id=room.id).first()
        # getColours(form.teams_num.data)       # WILL ADD AT LATER DATE

        # Sets Cookie for User
        resp = make_response(redirect(url_for('addnames', roomCode=roomCode)))
        resp.set_cookie('user_id', str(user.id))
        return resp

    return render_template('create.html', legend='Create a New Game', form=form)

@app.route('/<string:roomCode>', methods=['GET','POST'])
def teams(roomCode):
    currentRoom = roomFromCode(roomCode)
    # num_teams = currentRoom.num_teams
    # users = User.query.filter_by(room_id=currentRoom.id).all()
    currentUser = userLookupFromCookie()
    form = Teams()
    return render_template('teams.html', form=form, legend=roomCode, roomCode=roomCode,
            teamColours=teamColours, currentUser=currentUser)

@app.route('/addnames/<string:roomCode>', methods=['GET','POST'])
def addnames(roomCode):
    form = AddNames()
    currentRoom = roomFromCode(roomCode)
    form.names_required = currentRoom.names_per
    if form.validate_on_submit():
        names = request.form.getlist('guess_name[]')
        user_id = request.cookies.get('user_id')
        for name in names:
            x = Names(name=name, added_by=user_id, in_room=currentRoom.id,
                rnd1=0, rnd2=0, rnd3=0)
            db.session.add(x)
        db.session.commit()
        return redirect(url_for('teams', roomCode=roomCode))
        
    return render_template('addnames.html', form=form, legend=roomCode, names_per=currentRoom.names_per)

@app.route('/setTeam/<string:team>', methods=['GET','POST'])
def setTeam(team):
    userID = request.cookies.get('user_id')
    user = User.query.filter_by(id=userID).first()
    user.team = int(team)
    db.session.commit()
    return {
        "success": True
    }

@app.route('/initPlay/<string:roomCode>', methods=['GET','POST'])
def initPlay(roomCode):
    roomId = roomIdFromUserCookie()
    room = Room.query.filter_by(id=roomId).first()
    ct = 1
    for x in room.users:
        user = User.query.filter_by(id=x.id).first()
        if user.play_order != 0:
            break
        else:
            playOrder = initPlayOrder(roomId)
            for x in playOrder:
                user = User.query.filter_by(id=x).first()
                user.play_order = ct
                if ct == 1:
                    user.in_play = True
                ct += 1
                db.session.commit()
    room.game_started = True
    room.roundNo = 'rnd1'
    db.session.commit()

    resp = {
        "success": True
    }
    resp["roomCode"] = sendRoomCode()

    return resp

@app.route('/poll', methods=['GET','POST'])
def poll():
    roomId = roomIdFromUserCookie()
    room = Room.query.filter_by(id=roomId).first()
    if room.game_started == "1":
        # gameStartTimer(roomId)     
        resp = {}
        resp["current_state"] = "starting"
        resp["timer"] = room.game_started
        if room.game_started == "1":
            resp["current_state"] = "go"
            resp["timer"] = "0"
    else:
        usersInRoom = User.query.filter_by(room_id=roomId).all()
        noTeam = []
        team1 = []
        team2 = []
        ct = 0
        for x in usersInRoom:
            if usersInRoom[ct].team == 1:
                team1.append(usersInRoom[ct].username)
            elif usersInRoom[ct].team == 2:
                team2.append(usersInRoom[ct].username)
            else:
                noTeam.append(usersInRoom[ct].username)
            ct += 1
        resp = {
        "no_team": noTeam,
        "team_one": team1,
        "team_two": team2,
        "current_state": "ready"
        }
        room = Room.query.filter_by(id=roomId).first()
        resp['roomCode'] = sendRoomCode()
        for x in usersInRoom:
            if x.team == 0:
                resp["current_state"] = "not-ready"   
    
    return jsonify(resp)

@app.route('/play/<string:roomCode>', methods=['GET','POST'])
def play(roomCode):
    return render_template('play.html')

@app.route('/point/<nameId>/<rnd>', methods=['GET','POST'])
def point(nameId, rnd):
    currentUser = userLookupFromCookie()
    currentName = getNamefromId(nameId)
    if rnd == 'rnd1':
        Names.query.get(currentName.id).rnd1 = currentUser.team
    elif rnd == 'rnd2':
        Names.query.get(currentName.id).rnd2 = currentUser.team
    elif rnd == 'rnd3':
        Names.query.get(currentName.id).rnd3 = currentUser.team
    else:
        return {"Point_success": False}
    db.session.commit()
    return {
        "Point_success": True
    }

@app.route('/nextPlayer', methods = ['GET'])
def nextPlayer(*args):
    if not args:     # Enables the optional passing of a roomId
        roomId = roomIdFromUserCookie()
    else:
        roomId = args[0]
    playerOne, playerTwo = getNextPlayer(roomId)
    User.query.get(playerOne.id).in_play = False
    User.query.get(playerTwo.id).in_play = True
    db.session.commit()
    return {"success":True,"newPlayer":True}

@app.route('/getNewName/<rndNo>', methods=['GET'])
def getNewName(rndNo):
    roomId = roomIdFromUserCookie()
    namesToGuess = []
    kwargs = {"in_room":roomId, rndNo:0}
    names = Names.query.filter_by(**kwargs).all()
    resp = {}
    if len(names) <= 0:
        resp["newRound"] = True
        scorecard(roomId)
        return resp
    while len(namesToGuess) < 1:
        randName = random.choice(names)
        newNameId = randName.id
        newName = randName.name
        newNameAdded = User.query.filter_by(id=randName.added_by).first()
        if [newNameId, newName, newNameAdded.username] not in namesToGuess:
            namesToGuess.append([newNameId, newName, newNameAdded.username])
    resp["newRound"] = False
    resp["namesToGuess"] = namesToGuess

    return resp

def resetTimer(roomId):
    print('Timer Reset')
    Room.query.get(roomId).timer_started = False
    fullTime = Room.query.get(roomId).full_time
    Room.query.get(roomId).time_remaining = fullTime
    db.session.commit()

class actualTimer:
    def __init__(self):
        self._running = True

    def stop(self):
        print('Stop Called')
        self._running = False

    def run(self, secs, roomId):
        while self._running:
            Room.query.get(roomId).timer_started = True
            db.session.commit()
            for i in range(secs):                
                # This updates the time remaining in db.
                # Has to be called differently due to threading
                # not being able to update in scope.
                print('Thread Running: ', i)
                Room.query.get(roomId).time_remaining = secs - i
                db.session.commit()
                time.sleep(1)
                if secs - i == 1:
                    nextPlayer(roomId)
                    Room.query.get(roomId).time_remaining = 0
                    db.session.commit()
                    time.sleep(1)
                    Room.query.get(roomId).timer_started = False
            break
        resetTimer(roomId)


@app.route('/startTimer', methods = ['GET'])
def startTimer(*args):
    roomId = roomIdFromUserCookie()
    room = Room.query.filter_by(id=roomId).first()
    secs = room.time_remaining
    resetTimer(roomId)    

    timer = actualTimer()
    thr = threading.Thread(target=timer.run,args=(secs, roomId, ))
    thr.start()
    return {"Timer": "Started"}

def scorecard(roomId):
    T = actualTimer()
    T.stop()
    Room.query.get(roomId).scorecard = True
    db.session.commit()
    def scoreTimer():
        time.sleep(5)
        Room.query.get(roomId).scorecard = False
        db.session.commit()
        rnd(roomId)
        print("scoreThread has finished")

    print("scoreThread has started")
    scoreThread = threading.Thread(target=scoreTimer)
    scoreThread.start()

def rnd(roomId):
    room = Room.query.filter_by(id=roomId).first()
    nextRound = room.roundNo[0:3] + str(int(room.roundNo[3])+1)
    if nextRound == 'rnd4':
        nextRound = 'End'
    room.roundNo = nextRound
    db.session.commit()
    return { "rnd_success":True }

@app.route('/response', methods=['GET','POST'])
def response():
    roomId = roomIdFromUserCookie()
    room = Room.query.filter_by(id=roomId).first()
    resp = {}
    resp['roomCode'] = sendRoomCode()
    resp['rndNo'] = room.roundNo
    currentGuesser = User.query.filter_by(room_id=roomId, in_play=1).first()
    resp['currentPlayer'] = [currentGuesser.id, currentGuesser.username]
    resp['timerStarted'] = room.timer_started
    resp['Time'] = room.time_remaining
    if room.time_remaining == 0:
        resp['newPlayer'] = True
    if room.scorecard == True:
        resp['scorecard'] = True
        t1, t2 = rndScore(roomId, room.roundNo)
        resp['scores'] = [t1,t2]        
    
    return jsonify(resp)

@app.route('/gameOver/<roomCode>', methods=['GET','POST'])
def gameOver(roomCode):
    room = roomFromCode(roomCode)
    resetTimer(room.id)
    scores = totalScore(room.id)
    roomId = roomIdFromUserCookie()
    return render_template('gameover.html', scores=scores)
