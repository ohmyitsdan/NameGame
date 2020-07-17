from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FieldList
from wtforms.validators import InputRequired, ValidationError, Length

class JoinGame(FlaskForm):
    username = StringField('Name', validators=[InputRequired()])
    roomcode = StringField('Room Code', validators=[InputRequired(), Length(min=4)])
    submit = SubmitField('Play')

class CreateGame(FlaskForm):  
    username = StringField('Name', validators=[InputRequired()])
    guess_num = IntegerField('Names per person', validators=[InputRequired()])
    # teams_num = IntegerField('Number of teams', validators=[InputRequired()])
    timerem = IntegerField('Time Per Person', validators=[InputRequired()])
    # pass_num = IntegerField('Number of passes allowed', validators=[InputRequired()])
    submit = SubmitField('Create Game')

class AddNames(FlaskForm):
    submit = SubmitField('Add Names')

class Player(FlaskForm):
    username = StringField('Name', validators=[InputRequired()])

class Teams(FlaskForm):
    submit = SubmitField('Join Team')
