from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from game.config import Config

# from flask_login import LoginManager   #maybe?

app = Flask(__name__)
app.config.from_object(Config)


db = SQLAlchemy(app)
db.init_app(app)

# login_manager = LoginManager()

from game import routes