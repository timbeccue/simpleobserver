from flask import Flask, render_template, request, Response, redirect, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import redis

from configparser import ConfigParser
config_file = ConfigParser()
config_file.read('config.ini')

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

redis_host = config_file['NETWORK']['redis_host']
redis_port = config_file['NETWORK']['redis_port']
core1_redis = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

site_attributes = {
    'lat': config_file['SITE']['lat'],
    'lon': config_file['SITE']['lon'],
    'dome-camera': config_file['NETWORK']['dome_camera']
}

#migrate = Migrate(app, db)

from app import routes, models, weather_logging
