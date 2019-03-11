from flask import Flask, render_template, request, Response, redirect, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
import redis

from configparser import ConfigParser
config_file = ConfigParser()
config_file.read('config.ini')

application = Flask(__name__)
application.config.from_object(Config)


db = SQLAlchemy(application)
migrate = Migrate(application, db)
login = LoginManager(application)
login.login_view = 'login'

cors = CORS(application, resources={r"/*": {"origins": "*"}})


redis_host = config_file['NETWORK']['redis_host']
redis_port = config_file['NETWORK']['redis_port']
core1_redis = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

site_attributes = {
    'observatory_name': config_file['SITE']['observatory_name'],
    'city': config_file['SITE']['city'],
    'state': config_file['SITE']['state'],
    'country': config_file['SITE']['country'],
    'site_abbreviation': config_file['SITE']['site_abbreviation'],
    'lat': config_file['SITE']['lat'],
    'lon': config_file['SITE']['lon'],
    'has-dome-camera': config_file['NETWORK']['has_dome_camera'],
    'dome-camera': config_file['NETWORK']['dome_camera']
}
boto_credentials = {
    'access_key_id': config_file['AWS']['aws_access_key_id'],
    'secret_access_key': config_file['AWS']['aws_secret_access_key'],
    'region': config_file['AWS']['region']
}

#migrate = Migrate(app, db)

from application import routes, models, weather_logging
