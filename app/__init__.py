from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

from app.blueprints.api import api, user_bp
migrate = Migrate(app, db)
app.register_blueprint(api)
app.register_blueprint(user_bp)

from . import models
