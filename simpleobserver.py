from app import app, db, core1_redis
from app.models import User, Dso, ThingsInSpace, Hygdatum



@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'TIS':ThingsInSpace, 'Dso':Dso, 'Hygdatum':Hygdatum, 'redis':core1_redis}
