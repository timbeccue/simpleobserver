# app/routes.py

from app import app, db, core1_redis, site_attributes
from flask import Flask, render_template, request, Response, redirect 
from flask import jsonify, url_for, flash, send_from_directory, session
from flask_login import current_user, login_user, logout_user, login_required

import re, datetime, time, json, redis, datetime

from app.commands import *
from app.models import LoginForm, RegistrationForm, CameraForm, ObjectFilter, TestAddForm
from app.models import User, Dso, ThingsInSpace


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

@app.route('/getinfo/<item>', methods=['GET', 'POST'])
# The variable 'item' is a string of config items to get, delimited by a dash (-)
def get_info(item):
    items = item.split('-')
    data = {}
    try:
        for val in items:
            data[val] = site_attributes[val]
        return jsonify(status="success", data=data)
    except:
        return jsonify(status="fail")

@app.route('/dome-cam-url', methods=['GET', 'POST'])
def dome_cam():
    return jsonify(url=site_attributes['dome-camera'])



from astroquery.simbad import Simbad
from astropy.table import Table, vstack
@app.route('/simbadquery', methods=['GET', 'POST'])
def simbadquery():
    ''' 
    Should return JSON with status=success or fail. 
    If status=fail, json should include content="error message".
    If status=success, content should contain a string that is already coded in json format.
    '''

    search_args = request.form['query-args'].split(",")
    print(search_args)
    wildcard = True#request.form['haswildcards']

    if not search_args or not wildcard: #ensure nonempty fields
        return jsonify(status='fail', content="error: no search argument given.")

    # Customize fields returned by Simbad
    cSimbad = Simbad()
    cSimbad.add_votable_fields('main_id', 'id(m)', 'id(ngc)','ra(d)', 'dec(d)', 'ubv', 'flux(V)', 'id(name)', 'dim_majaxis')
    cSimbad.remove_votable_fields('coordinates', 'main_id')

    # Comma separated queries return multiple tables that are combined into one.
    def objects(*args): 
        def gen(*args):
            for arg in args:
                yield cSimbad.query_objects(arg, wildcard=True)
        return vstack(list(gen(*args)))


    raw_result = objects(search_args)
    try:
        result_b = raw_result.to_pandas()
    except Exception as ex:
        print(ex)
        return jsonify(status='fail', content="error: simbad did not respond to request.")
    
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


def send(cmd, expire=expire_time):
    if live_commands==True:
        send_command = core1_redis.set(cmd[0], json.dumps(cmd[1]), ex=expire)
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

altitudes = []
import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
def make_altitude_lut():
    time = Time.now()
    location = EarthLocation(lat=34*u.degree, lon=-119*u.degree)
    # How many points to precalculate for ra and dec.
    num_ra = 360
    num_dec = 180
    # Line up each ra and dec value 
    ra = np.repeat(np.arange(num_ra), num_dec)
    dec = np.tile(np.arange(num_dec), num_ra) - 90
    
    eq = SkyCoord(ra, dec, unit=u.degree)
    aa = eq.transform_to(AltAz(obstime=time, location=location)).alt.deg
    altitudes = np.ndarray.tolist(aa.astype(int))
    return altitudes

def altitude_lut():
    while True:
        altitudes = make_altitude_lut()
        yield 'data: {}\n\n'.format(json.dumps(altitudes))
        time.sleep(30000) # Not in use, so no need for fast refresh.

@app.route('/get_altitude_lut', methods=['GET', 'POST'])
def stream_altitude_lut():
    sse = altitude_lut()
    return Response(sse, mimetype="text/event-stream")





import app.database_helpers as database

from app.helpers import utilities
@app.route('/altitude')
def alt():
    print(utilities.getAlt(3,89))
    return(jsonify(alt=utilities.getAlt(3,89)))

@app.route('/addtodatabase', methods=['POST', 'GET'])
@login_required
def addtodatabase():
    return database.add_to_database()

# Filter the display of objects by type.
# This route takes users selection and saves it in a session, to be read by tablelookup when the table is redrawn.
@app.route('/apply_table_filters', methods=['POST', 'GET'])
def apply_table_filters():
    return database.apply_table_filters()


# Dumps all data into a json file (geojson format) for use in the d3celestial sky chart.
@app.route('/database_to_json')
@login_required
def database_to_json():
    return database.database_to_json()

@app.route('/recreate_database')
@login_required
def recreate_database():
    return database.recreate_database()

@app.route('/merge_geojson')
@login_required
def merge_geojson():
    return database.merge_geojson()


#############################################
# END TESTPAGE STUFF ########################
#############################################


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('base.html', loginform=LoginForm(), cameraform=CameraForm(), filter=ObjectFilter())


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
        print(form.time.data)
        print(form.count.data)
        print(form.delay.data)
        print(form.dither.data)
        print(form.autofocus.data)
        print(form.bin.data)
        print(form.filter.data)

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
            print(response)
            return jsonify(response=response, requested="requested", processed=cmd[1], live=live_commands)
        return jsonify(errors=form.errors)

    if msg == 'batch-camera':
        # Fields in each row: time, count, delay, filter, bin, dither.
        time = []
        count = [] 
        delay = [] 
        filter = []
        bin = []
        dither = []
        cmds = []

        # Get field values for each row submited.
        rowid = 0
        while True:
            try:
                time.append(request.form[f"time-{rowid}"])
                count.append(request.form[f"count-{rowid}"])
                delay.append(request.form[f"delay-{rowid}"])
                filter.append(request.form[f"filter-{rowid}"])
                bin.append(request.form[f"bin-{rowid}"])
                dither.append(request.form[f"dither-{rowid}"])
            except:
                break
            rowid += 1
        
        autofocus = request.form['autofocus']
        position_angle = request.form['position-angle']
        
        num_rows = len(time)

        for row in range(num_rows):
            one_row = cmd_expose(time[row],
                                 count[row],
                                 bin[row],
                                 dither[row], 
                                 autofocus, 
                                 position_angle, 
                                 delay[row], 
                                 filter[row])
            cmds.append(one_row)
        

        

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


from app.reference import all_dsos, all_stars, double_stars, nebula, galaxies, globular_clusters
from app.reference import open_clusters, everything_else
from sqlalchemy import and_, or_
from datatables import ColumnDT, DataTables
@app.route('/tablelookup')
def tablelookup():
    """Return server side data for object table"""

    columns = [
        ColumnDT(ThingsInSpace.messier),
        ColumnDT(ThingsInSpace.type),
        ColumnDT(ThingsInSpace.magnitude),
        ColumnDT(ThingsInSpace.ra_decimal),
        ColumnDT(ThingsInSpace.de_decimal),
        ColumnDT(ThingsInSpace.names)
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


#-------------------------------------------------------------------------------------------------------------#
@app.route('/starparty', methods=['GET', 'POST'])
def starparty():
    return render_template('starparty.html', filter=ObjectFilter())
#-------------------------------------------------------------------------------------------------------------#
@app.route('/testpage')
@login_required
def testpage():
    database = db.session.query(ThingsInSpace).all()
    return render_template('testpage.html', dbform=TestAddForm(), filter=ObjectFilter(), database=database)
#-------------------------------------------------------------------------------------------------------------#




#if __name__=='__main__':
#    app.run(host='10.15.0.15')
