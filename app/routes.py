# app/routes.py

from app import app, db, core1_redis
from flask import Flask, render_template, request, Response, redirect, jsonify, url_for, flash, send_from_directory

import re, datetime, time, json, redis
import datetime

from app.state import ptr_state
from app.commands import *
from flask_login import current_user, login_user, logout_user, login_required

# from sqlalchemy-datatables example
from datatables import ColumnDT, DataTables
from app.models import User, Dso, ThingsInSpace
# Import forms:
from app.models import LoginForm, RegistrationForm, CameraForm, ObjectFilter, TestAddForm

expire_time = 120 #seconds
live_commands = True



####################################################################################
from app.weather_logging import weatherlogger
from apscheduler.schedulers.background import BackgroundScheduler

weather_logger = BackgroundScheduler(daemon=True)
weather_logger.add_job(weatherlogger.log_everything, 'interval', seconds=55)
weather_logger.start()
####################################################################################



# AJAX Routes
from app import weather_plots
@app.route('/plot_weather/<logtype>', methods=['GET', 'POST'])
def plot_weather(logtype):
    return(weather_plots.create_plot(logtype))

from configparser import ConfigParser
@app.route('/getinfo/<item>', methods=['GET', 'POST'])
# The variable 'item' is a string of config items to get, delimited by a dash (-)
def get_info(item):
    config = ConfigParser()
    config.read('config.ini')
    item_list = item.split("-")
    values = {}
    for val in item_list:
        values[val] = config['DEFAULT'][val]
    return jsonify(values)    

from astroquery.simbad import Simbad
@app.route('/simbadquery', methods=['GET', 'POST'])
def simbadquery():
    ''' 
    Should return JSON with status=success or fail. 
    If status=fail, json should include content="error message".
    If status=success, content should contain a string that is already coded in json format.
    '''

    args = request.form['query-args']
    wildcard = request.form['haswildcards']

    if not args or not wildcard: #ensure nonempty fields
        return jsonify(status='fail', content="error: no search argument given.")

    try:
        raw_result = Simbad.query_object(args, wildcard=False)
    except Exception as ex:
        print(ex)
        return jsonify(status='fail', content="error: simbad did not respond to request.")
    
    result_b = raw_result.to_pandas()
    result = result_b.to_json()
    print(result)
    return jsonify(status="success", content=result)

    

# User Login Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('home'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return redirect(url_for('register'))
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    loginform = LoginForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('home'))
    return render_template('register.html', form=form, loginform = loginform)




def send(cmd):
    if live_commands==True:
        send_command = core1_redis.set(cmd[0], json.dumps(cmd[1]), ex=expire_time)
        print(send_command)
    else:
        print("Commands are offline right now.")

def event_stream(state_key, refresh_frequency):
    while True:
        state_dict = core1_redis.get(state_key)
        yield 'data: {}\n\n'.format(state_dict)
        time.sleep(refresh_frequency)

# Push telescope_state to the client.
@app.route('/status/<device>/<id>', methods=['GET', 'POST'])
def stream(device,id):
    state_key = f"<ptr-{device}-{id}_state"
    refresh_frequency = .8

    sse = event_stream(state_key, refresh_frequency)
    return Response(sse, mimetype="text/event-stream")



#############################################
# TESTPAGE STUFF ############################
#############################################


from app.reference import object_types, seasons, constellations

from flask import session
@app.route('/testpage')
@login_required
def testpage():
    database = db.session.query(ThingsInSpace).all()
    return render_template('testpage.html', dbform=TestAddForm(), filter=ObjectFilter(), database=database)

@app.route('/addtodatabase', methods=['POST', 'GET'])
@login_required
def addtodatabase():
    dbform = TestAddForm()
    if request.method == 'POST':
        obj_data = {
            'type': dbform.type.data,  # or request.dbform['name']
            'magnitude': dbform.magnitude.data,
            'size_large': dbform.size_large.data,
            'size_small': dbform.size_small.data,
            'distance_ly': dbform.distance_ly.data,
            'ra_decimal': dbform.ra_decimal.data,
            'de_decimal': dbform.de_decimal.data,
            'season': dbform.season.data,
            'constellation': dbform.constellation.data,
            'names': dbform.names.data
        }

        object_to_add = ThingsInSpace(**obj_data)
        db.session.add(object_to_add)
        db.session.commit()
        return redirect(url_for('testpage'))

from app.reference import all_dsos, all_stars, double_stars, nebula, galaxies, globular_clusters
from app.reference import open_clusters, everything_else


# Filter the display of objects by type.
# This route takes users selection and saves it in a session, to be read by tablelookup when the table is redrawn.
@app.route('/apply_table_filters', methods=['POST', 'GET'])
def apply_table_filters():

    filter = ObjectFilter()

    if request.method == 'POST':

        # Reset to show nothing, then add selected objects with set union: (a | b).
        show_these_stars = set([])
        if filter.stars.data is True:
            show_these_stars |= {'star'}
        if filter.double_stars.data is True:
            show_these_stars |= double_stars
        visible_stars = list(show_these_stars)
        session['star_type_filter'] = visible_stars

        stellar_magnitudes = [-50,50]
        if filter.star_magnitude_min.data is not None:
            stellar_magnitudes[0] = filter.star_magnitude_min.data
        if filter.star_magnitude_max.data is not None:
            stellar_magnitudes[1] = filter.star_magnitude_max.data
        session['stellar_magnitudes'] = stellar_magnitudes

        # DSOs
        show_these_dsos = set([])
        if filter.nebula.data is True:
            show_these_dsos |= nebula
        if filter.galaxies.data is True:
            show_these_dsos |= galaxies
        if filter.open_clusters.data is True:
            show_these_dsos |= open_clusters
        if filter.globular_clusters.data is True:
            show_these_dsos |= globular_clusters
        if filter.everything_else.data is True:
            show_these_dsos |= everything_else
        visible_dsos = list(show_these_dsos)
        session['dso_type_filter'] = visible_dsos;

        dso_magnitudes = [-50,50]
        if filter.dso_magnitude_min.data is not None:
            dso_magnitudes[0] = filter.dso_magnitude_min.data
        if filter.dso_magnitude_max.data is not None:
            dso_magnitudes[1] = filter.dso_magnitude_max.data
        session['dso_magnitudes'] = dso_magnitudes


    return jsonify(
            visible_stars=visible_stars,
            stellar_magnitudes=stellar_magnitudes,
            visible_dsos=visible_dsos,
            dso_magnitudes=dso_magnitudes)


from sqlalchemy import and_, or_
@app.route('/tablelookup')
def tablelookup():
    """Return server side data for object table"""

    columns = [
        ColumnDT(ThingsInSpace.messier),
        ColumnDT(ThingsInSpace.type),
        ColumnDT(ThingsInSpace.magnitude),
        ColumnDT(ThingsInSpace.ra_decimal),
        ColumnDT(ThingsInSpace.de_decimal),
        ColumnDT(ThingsInSpace.names),
    ]

    star_types = all_stars # default
    try:
        star_types = session['star_type_filter']
        print(star_types)
    except: pass

    stellar_magnitudes = [-50,2.5] # default
    try:
        stellar_magnitudes = session['stellar_magnitudes']
        print(stellar_magnitudes)
    except: pass

    dso_types = all_dsos # default
    try:
        dso_types = session['dso_type_filter']
        print(dso_types)
    except: pass

    dso_magnitudes = [-50,50] # default
    try:
        dso_magnitudes = session['dso_magnitudes']
        print(dso_magnitudes)
    except: pass


    # define the initial query
    star_query = and_(ThingsInSpace.type.in_(list(star_types)),
                     ThingsInSpace.magnitude >= stellar_magnitudes[0],
                     ThingsInSpace.magnitude <= stellar_magnitudes[1]).self_group()
    dso_query = and_(ThingsInSpace.type.in_(list(dso_types)),
                     ThingsInSpace.magnitude >= dso_magnitudes[0],
                     ThingsInSpace.magnitude <= dso_magnitudes[1]).self_group()
    clause_args = [star_query, dso_query]
    or_clauses = or_(*clause_args).self_group()

    query = db.session.query().filter(or_clauses)


    # GET parameters
    params = request.args.to_dict()

    # instantiating a DataTable for the query and table
    rowTable = DataTables(params, query, columns)

    # returns data to DataTable
    forTable = jsonify(rowTable.output_result())
    return(forTable)

# Dumps all data into a json file (geojson format) for use in the d3celestial sky chart.
@app.route('/database_to_json')
@login_required
def database_to_json():

    # d3celestial sky chart expects coordinate data in degrees from -180 to +180, so this formats RA values.
    def hour2degree(ra):
        if ra > 12: return 15 * (ra - 24)
        return ra * 15

    def db_to_json():
        features = []
        for object in db.session.query(ThingsInSpace).all():
            obj = {}
            properties = {}
            geometry = {}

            properties["messier"] = object.messier
            properties["mag"] = object.magnitude
            properties["type"] = object.type

            geometry["type"] = "Point"
            geometry["coordinates"] = [hour2degree(object.ra_decimal), object.de_decimal]

            obj["type"] = "Feature"
            obj["id"] = object.id
            obj["properties"] = properties
            obj["geometry"] = geometry

            features.append(obj)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        filename = 'custom_objects.json'

        with open(filename, 'w') as f:
            json.dump(geojson, f)

    #db_to_json()
    return 'success'

@app.route('/recreate_database')
@login_required
def recreate_database():

    StatusOn = False

    if StatusOn is False: return "failure"

    print(f'Size of database: {db.session.query(ThingsInSpace).count()}')
    if StatusOn: db.session.query(ThingsInSpace).delete()
    if StatusOn: db.create_all()
    print(f'Size of database: {db.session.query(ThingsInSpace).count()}')

    def degree2hour(ra):
        return ra/15 if ra>0 else ra/15+24

    geojson_list = ['doublesGEO.json', 'threehundredstarsGEO.json', 'messierGEO.json']

    features = []

    for file in geojson_list:
        with open('app/static/mapdata/'+file, 'r') as f:
            data = json.load(f)
            features += data["features"]


    for feat in features:

        def prop(attr, location=None):
            if location is None:
                return feat.get(attr, None)
            return feat[location].get(attr, None)
        p = 'properties'
        g = 'geometry'

        obj = {
            "messier": prop('messier', p),
            "ngc": prop('ngc',p),
            "bayer": prop('bayer',p),
            'type': prop('type', p),
            'magnitude': prop('mag',p),
            'magnitude2': prop('mag2',p),
            'size_large': prop('size',p),
            'distance_ly': prop('distance',p),
            'ra_decimal': degree2hour(prop('coordinates',g)[0]),
            'de_decimal': (prop('coordinates',g))[1],
            'position_angle': prop('position_angle',g),
            'separation_angle': prop('separation',g),
            'spectral_class': prop('spectral',p),
            'season': prop('season',p),
            'constellation': prop('con',p),
            'names': prop('name',p),
            'data_origin': prop('data_origin')
        }

        db_obj = ThingsInSpace(**obj)
        #print(obj)
        if StatusOn: db.session.add(db_obj)
        if StatusOn: db.session.commit()

    print(f'Size of database: {db.session.query(ThingsInSpace).count()}')
    return 'success'

@app.route('/merge_geojson')
@login_required
def merge_geojson():
    
    files = []
    directory = 'app/static/mapdata/'
    files.append(directory+'doublesGEO.json')
    files.append(directory+'threehundredstarsGEO.json')
    files.append(directory+'messierGEO.json')

    features = []

    for f in files:
        with open(f,'r') as infile:
            data = json.load(infile)
            features += data["features"] 

    print(len(features))

    out = {
        "type": "FeatureCollection",
        "features": features
    }

    # Remove 'NaN', which is invalid json
    out_json = json.dumps(out)
    regex = re.compile(r'\bnan\b',flags=re.IGNORECASE)
    out_json = re.sub(regex, ' null ', out_json)

    with open(directory+'all_objects.json', 'w') as outfile:
        outfile.write(out_json)

    return 'success'
    


#############################################
# END TESTPAGE STUFF ########################
#############################################




@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('base.html', state=ptr_state, loginform=LoginForm(), cameraform=CameraForm(), filter=ObjectFilter())

@app.route('/starparty', methods=['GET', 'POST'])
def starparty():
    return render_template('starparty.html', state=ptr_state, filter=ObjectFilter())

@app.route('/textcommand', methods=['GET', 'POST'])
@login_required
def textcommand():
    #print("form dict: "+str(request.form.to_dict()))
    command = request.form['console-text'].strip()
    cmd = ''


    first = command.split(" ")[0].lower()
    if any(word in first for word in ["slew", "go", "goto"]):
    # Space-separated coordinates (eq): "slew 11.32 74.3"
        ra = float(command.split(" ")[1])
        de = float(command.split(" ")[2])
        cmd = cmd_slew([ra, de])
        print(cmd)
        send(cmd)
    if first in ["unpark", "park"]:
    #sends command directly to mount.
        cmd = cmd_parking(first)
        print(cmd)
        send(cmd)
    if any(x in first for x in ["filter"]):
        # accepts "filter g" or "filter ha".
        fil = command.split(" ")[1]
        cmd = cmd_filter(fil)
        print(cmd)
        send(cmd)
    if any(x in first for x in ['expose', 'capture', 'take', 'start', 'image']):
        # exposure time is 30s or 30.5s, number of images is 5x, binning is 2bin or bin2
        t = re.search(r"\d+[^\sx]+",command)
        c = re.search(r"\d*x", command)
        b = re.search(r"[124]?bin[124]?", command)
        count = c.group() if c else '1'
        time = t.group() if t else '5'
        binning = b.group() if b else '1'
        count = re.sub(r"\D", "", count)
        time = re.sub(r"\D", "", time)
        binning = re.sub(r"\D", "", binning)
        cmd = cmd_expose(float(time), float(count), float(binning))
        print(cmd)
        send(cmd)
    if first == 'track' or first == 'track:':
        split = command.split(" ")
        if len(split) == 2: cmd = cmd_track(split[1])
        if len(split) == 3:
            ra = split[1]
            de = split[2]
            cmd = cmd_track('custom', ra, de)
        elif len(split) == 1: cmd = cmd_track('sidereal')
        print(cmd)
        send(cmd)




    requested = str(datetime.datetime.now()).split('.')[0]+": . . . . . \t"+command
    processed = cmd[1] if (len(cmd)>0) else ''
    return jsonify(requested=requested, processed=processed, live=live_commands)


@app.route('/command/<msg>', methods=['POST'])
@login_required
def command(msg):

    # Camera/Imaging Commands
    if msg == 'camera':
        form = CameraForm()

        if form.validate_on_submit():
            time = form.time.data
            count = form.count.data
            delay = form.delay.data
            dither = form.dither.data
            autofocus = form.autofocus.data
            position_angle = form.position_angle.data
            bin = form.bin.data
            filter = form.filter.data
            cmd = cmd_expose(time, count, bin, dither, autofocus, position_angle, delay, filter)
            send(cmd)
            print(cmd)
            response = f"Taking {count} {time} second image(s)."
            return jsonify(response=response, requested="requested", processed=cmd[1], live=live_commands)
        return jsonify(errors=form.errors)

    # Telescope GOTO Commands
    if msg == 'go':
        text = request.form['goto-box']
        coordinates = parse_goto_input(text)
        cmd = cmd_slew(coordinates)
        send(cmd)
        print(cmd)
        response = f"Slewing to {coordinates}"
        return jsonify(response=response, requested="requested", processed=cmd[1], live=live_commands)
        
    # Enclosure Button Commands
    if msg == 'lamp': 
        value = request.form['command']
        response = f"Lamp is {value}."
        cmd = cmd_lamp(value)
    if msg == 'ir-lamp': 
        value = request.form['command']
        response = f"IR lamp is {value}."
        cmd = cmd_ir(request.form['command'])
    if msg == 'roof': 
        value = request.form['command']
        response = f"Enclosure roof is {value[:4]}ing."
        cmd = cmd_roof(request.form['command'])
    if msg == 'parking': 
        value = request.form['command']
        response = f"Telescope is {value}ing."
        cmd = cmd_parking(request.form['command'])
    send(cmd)
    processed = cmd[1] if (len(cmd)>0) else ''
    return jsonify(response=response, requested="requested", processed=processed, live=live_commands)





if __name__=='__main__':
    app.run(host='10.15.0.15')
