from app import app, db, core1_redis
from app.models import User, Dso, testDB, Hygdatum



@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'testDB':testDB, 'Dso':Dso, 'Hygdatum':Hygdatum, 'redis':core1_redis}
