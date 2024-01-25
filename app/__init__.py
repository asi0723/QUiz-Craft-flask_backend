from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db = SQLAlchemy(app)

from app.blueprints.api import api, user_bp, analyize
migrate = Migrate(app, db)
app.register_blueprint(api)
app.register_blueprint(user_bp)
app.register_blueprint(analyize)

from . import models
