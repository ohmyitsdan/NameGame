import random
from game import db

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(4), unique=True, nullable=False)
    num_teams = db.Column(db.Integer)
    names_per = db.Column(db.Integer)
    users = db.relationship('User', backref='user', lazy=True)
    names_in_bowl = db.relationship('Names', backref='bowlnames', lazy=True)
    roundNo = db.Column(db.Integer)
    ct = db.Column(db.Integer)
    full_time = db.Column(db.Integer, nullable=False)
    time_remaining = db.Column(db.Integer, nullable=False)
    timer_started = db.Column(db.Boolean, nullable=False)
    game_started = db.Column(db.String(4), nullable=False)
    scorecard = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'{self.room_code}, {self.users}'

class Names(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    in_room = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    # These show which team scored a point on the name
    rnd1 = db.Column(db.Integer)
    rnd2 = db.Column(db.Integer)
    rnd3 = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    team = db.Column(db.Integer)
    namesadded = db.relationship('Names', backref='names', lazy=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    play_order = db.Column(db.Integer)
    in_play = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'{self.username}, {self.team}, {self.room_id}'


Colours = [
['Red','#FF0000'],
['Lime','#00FF00'],
['Blue','#0000FF'],
['Yellow','#FFFF00'],
['Cyan','#00FFFF'],
['Maroon','#800000'],
['Navy','#000080'],
['Green','#008000'],
['Orange','#FFA500']
]
