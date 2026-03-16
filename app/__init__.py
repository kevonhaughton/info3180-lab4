from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app.models import UserProfile

@login_manager.user_loader
def load_user(user_id):
    return UserProfile.query.get(int(user_id))

# allow migrations to see models
from app import models

from app import views