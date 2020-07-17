import random
from flask import request
from game.models import User, Room, Names

teamColours = [
['Red','#FF0000'],
['Green','#008000']
]

def genRoomCode():
        code = ""
        for i in range(4):
            r = random.randint(0,25)
            c = chr(65+r)
            code += c
        return code

# @app.context_processor
def getColours(teams):
    global teamColours
    teamColours = []
    while len(teamColours) < teams:
        colour = random.choice(Colours)
        if colour not in teamColours:
            teamColours.append(colour)

def getUserFromId(user_id):
    return User.query.filter_by(id=user_id).first()

def getUsernameFromCookie(user_id):
    userID = request.cookies.get('user_id')
    user = User.query.filter_by(id=userID).first()
    return user.username

def userLookupFromCookie():
    user_id = request.cookies.get('user_id')
    currentUser = User.query.filter_by(id=user_id).first()
    return currentUser

def roomIdFromUserCookie():
    user = userLookupFromCookie()
    return user.room_id

def roomFromCode(room):
    return Room.query.filter_by(room_code=room).first()

def getAllNames(room):
    return Names.query.filter_by(in_room=room).all()

def getNamefromId(ID):
    return Names.query.filter_by(id=ID).first()

def namesRemaining(room, rndNo):
    kwargs = {'in_room': room, rndNo: None}
    notAssigned = Names.query.filter_by(**kwargs).all()
    resp = []
    for x in notAssigned:
        nameId = x.id
        name = x.name
        user = User.query.filter_by(id=x.added_by).first()
        resp.append([name, user.username, nameId])
    return resp

def getNextPlayer(roomId):
    allPlayers = Room.query.get(roomId).users
    currentPlayer = User.query.filter_by(room_id=roomId, in_play=True).first()
    order = currentPlayer.play_order
    if order >= len(allPlayers):
        order = 0
    nextPlayer = User.query.filter_by(room_id=roomId, play_order=order+1).first()
    return currentPlayer, nextPlayer

def rndScore(room, rndNo):
    kwargs = {'in_room': room, rndNo: 1}
    team1Score = len(Names.query.filter_by(**kwargs).all())
    kwargs = {'in_room': room, rndNo: 2}
    team2Score = len(Names.query.filter_by(**kwargs).all())
    return team1Score, team2Score

def totalScore(roomId):
    kwargs = {'in_room': roomId, 'rnd1': 1}
    team1Score = len(Names.query.filter_by(**kwargs).all())
    kwargs = {'in_room': roomId, 'rnd1': 2}
    team2Score = len(Names.query.filter_by(**kwargs).all())

    kwargs = {'in_room': roomId, 'rnd2': 1}
    team1Score += len(Names.query.filter_by(**kwargs).all())
    kwargs = {'in_room': roomId, 'rnd2': 2}
    team2Score += len(Names.query.filter_by(**kwargs).all())

    kwargs = {'in_room': roomId, 'rnd3': 1}
    team1Score += len(Names.query.filter_by(**kwargs).all())
    kwargs = {'in_room': roomId, 'rnd3': 2}
    team2Score += len(Names.query.filter_by(**kwargs).all())
    return team1Score, team2Score


def initPlayOrder(roomId):
    currentRoom = Room.query.filter_by(id=roomId).first()
    players = currentRoom.users
    firstTeam = random.randint(1,2)
    team1 = []
    team2 = []
    playOrder = []
    ct = 1
    for x in players:
        if x.team == 1:
            team1.append(x.id)
        else:
            team2.append(x.id)
    for i in range(len(team1 + team2)):
        if firstTeam == 1:
            t1 = random.choice(team1)
            if t1 not in playOrder:
                playOrder.append(t1)
            t2 = random.choice(team2)
            if t2 not in playOrder:
                playOrder.append(t2)
        else:
            t2 = random.choice(team2)
            if t2 not in playOrder:
                playOrder.append(t2)
            t1 = random.choice(team1)
            if t1 not in playOrder:
                playOrder.append(t1)
    return playOrder

def sendRoomCode():
    currentRoomId = roomIdFromUserCookie()
    room = Room.query.filter_by(id=currentRoomId).first()
    return room.room_code

