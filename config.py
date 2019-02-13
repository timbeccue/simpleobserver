from configparser import ConfigParser
import os

basedir = os.path.abspath(os.path.dirname(__file__))

config_parser = ConfigParser()
config_parser.read('config.ini')

class Config(object):

    SECRET_KEY = config_parser['FLASK']['secret_key']

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if config_parser['DATABASE']['uselocaldatabase'] == 'yes':
        skyobjects_name = config_parser['DATABASE']['skyobjects_database']
        users_name = config_parser['DATABASE']['users_database']
        SQLALCHEMY_BINDS = {
            'things_in_space': 'sqlite:///'+os.path.join(basedir, 'databases/', skyobjects_name),
            'users': 'sqlite:///'+os.path.join(basedir, 'databases/', users_name)
        }
    else:
        SQLALCHEMY_BINDS = {
            'things_in_space': 'mysql+pymysql://testdb11:testdb11@ptr-db.cyuke35resta.us-west-1.rds.amazonaws.com:3306/things_in_space',
            'users': 'mysql+pymysql://testdb11:testdb11@ptr-db.cyuke35resta.us-west-1.rds.amazonaws.com:3306/users' 
        }


