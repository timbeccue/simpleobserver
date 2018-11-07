from flask import Flask, render_template, request, Response, redirect, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import redis


app = Flask(__name__)
app.config.from_object(Config)
app.config['DEBUG'] = True
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

core1_redis = redis.StrictRedis(host='10.15.0.15', port=6379, db=0, decode_responses=True)

#migrate = Migrate(app, db)

from app import routes, models
