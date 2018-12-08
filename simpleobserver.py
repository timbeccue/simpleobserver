from app import app, db, core1_redis
from app.models import User, Dso, ThingsInSpace, Hygdatum
from app.add_messier import MessierToDatabase



@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'TIS':ThingsInSpace, 'Dso':Dso, 'Hygdatum':Hygdatum, 'm2d':MessierToDatabase, 'redis':core1_redis}
