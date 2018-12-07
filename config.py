import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = 'NOT_SECURE'

    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(basedir, 'hygdata.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
        'astro': 'sqlite:///'+os.path.join(basedir, 'hygdata.db'),
        'users': 'sqlite:///'+os.path.join(basedir, 'users.db'),
        'bindkey_testDB': 'sqlite:///'+os.path.join(basedir, 'testDB.db')
    }

class Site:
    def __init__(self):
        self.name = 'ptr'
        self.enclosures = {'enc1':1}
        self.mounts = {'mnt1': 1}
        self.otas = {'ota1':1}
        self.focusers = {'foc1':1}
        self.rotators = {'rot1':1}
        self.filterwheels = {'fil1':1}
        self.cameras = {'cam1':1, 'cam2':2}
        self.lamps = {'lamp1':1}

    def get_site(self):
        return (self.__dict__)
