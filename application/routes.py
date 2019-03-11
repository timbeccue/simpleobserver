# application/routes.py

from application import application, db, core1_redis, site_attributes, boto_credentials
from flask import Flask, render_template, request, Response, redirect 
from flask import jsonify, url_for, flash, send_from_directory, session
from flask_login import current_user, login_user, logout_user, login_required

import re, datetime, time, json, redis, datetime, os

from application.commands import *
from application.models import LoginForm, RegistrationForm, CameraForm, ObjectFilter, TestAddForm
from application.models import User, Dso, ThingsInSpace


####################################################################################
from application.weather_logging import weatherlogger
from apscheduler.schedulers.background import BackgroundScheduler

weather_logger = BackgroundScheduler(daemon=True)
weather_logger.add_job(weatherlogger.log_everything, 'interval', seconds=55)
weather_logger.start()
####################################################################################
from application.auth_helper import auth_required



@application.route('/commands/<type>', methods=['POST'])
@auth_required
def commands(type):

    content = request.get_json()
    cmd = []

    if type == "focus":
        try: cmd = cmd_focus(content["command"], content["position"])
        except: cmd = cmd_focus(content["command"])

    if type == "rotate": 
        try: cmd = cmd_position_angle(content["command"], content["angle"])
        except: cmd = cmd_position_angle(content["command"])

    if type == "park":
        cmd = cmd_parking(content["command"])

    if type == "lamp":
        cmd = cmd_lamp(content["command"])

    if type == "ir-lamp":
        cmd = cmd_ir(content["command"])

    if type == "roof":
        cmd = cmd_roof(content["command"])

    if type == "flatscreen":
        try: cmd = cmd_flatscreen(content["command"], content["value"])
        except: cmd = cmd_flatscreen(content["command"])

    if type == "cover":
        try: cmd = cmd_cover(content["command"], content["value"])
        except: cmd = cmd_cover(content["command"])

    if type == "slew": 
        cmd = cmd_slew([content["ra"], content["dec"]])

    if type == "camera":
        cmd = cmd_expose(
            content["time"],
            content["count"],
            content["bin"],
            content["dither"],
            content["autofocus"],
            content["hint"],
            site_attributes["site_abbreviation"],
            content["size"],
            content["delay"],
            content["filter"],
        )
    
    print(cmd)
    send(cmd)
    result = jsonify(cmd)
    return result




@application.route('/api/test/button', methods=['GET', 'POST'])
def testbutton():
    if request.method == 'GET':
        time.sleep(3)
        return "delayed button test return"
    return "button test return"

from application.auth_helper import auth_required
@application.route('/api/test', methods=['GET', 'POST'])
def apitest():
    # Get jwt from header, then decode and verify it. 
    #jwt = request.headers.get('Authorization')
    #result = decode_verify_jwt(jwt) # returns json token claims if verified, otherwise returns False.
    return "test api success"

@application.route('/api/loginrequired', methods=['GET', 'POST'])
@auth_required
def apirestricted():
    return("protected api success")

@application.route('/api/parkoff', methods=['GET', 'POST'])
@auth_required
def parkingtest():
    content = request.get_json()
    value = content['command']
    #value="park"
    response = f"Telescope is {value}ing."
    cmd = cmd_parking(value)
    send(cmd)
    processed = cmd[1] if (len(cmd)>0) else ''
    data = jsonify(response=response, requested="requested", processed=processed, live=live_commands)
    return data


@application.route('/testlogexists', methods=['GET', 'POST'])
def testlogexists():
    print(str(weatherlogger.log_exists('W')))
    return ("testlogexists ran successfully")

import boto3
@application.route('/getrecentimages', methods=['GET', 'POST'])
def gettestimage():
    ''' Get all objects from dynamodb (name and url of objects in s3 postage).
        Return a list of urls sorted by the objects' creation dates. '''

    urls = []
    dynamodb = boto3.resource(
        'dynamodb', 
        aws_access_key_id=boto_credentials['access_key_id'],
        aws_secret_access_key=boto_credentials['secret_access_key'],
        region_name=boto_credentials['region']
    )
    table = dynamodb.Table('wmd_postage')

    # Put all dynamodb rows (dicts) in a list.
    response = table.scan()
    for i in response['Items']:
        urls.append(i)
        
    # Define sort order from earliest to latest last-modified-time.
    date_sort = lambda obj: ''.join(s for s in obj['capture_time'] if s.isdigit())

    # Sort items by date, then reduce to a list of date-sorted urls only.
    urls.sort(key=date_sort) 
    urls = [item['url'] for item in urls]
    
    return json.dumps(urls)

# AJAX Routes
from application import weather_plots
@application.route('/plot_weather/<logtype>', methods=['GET', 'POST'])
def plot_weather(logtype):
    if not weatherlogger.log_exists('W'):
        return("no log found")
    return(weather_plots.create_plot(logtype))


@application.route('/dome-cam-url', methods=['GET', 'POST'])
def dome_cam():
    return jsonify(url=site_attributes['dome-camera'])


# User Login Routes
@application.route('/login', methods=['GET', 'POST'])
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

@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
@application.route('/register', methods=['GET', 'POST'])
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
    return render_template('register.html', form=form, loginform = loginform, site=site_attributes)


def event_stream(refresh_frequency=1):
    while True:
        state_dict = compile_state_to_send()
        yield 'data: {}\n\n'.format(state_dict)
        time.sleep(refresh_frequency)
def compile_state_to_send():
    ''' Get various state information from redis and publish to SSE broadcast combined in a single JSON object '''

    state_keys = ['mnt-1', 'foc1', 'rot1', 'wx-1']
    compiled_state = {} 
    
    for key in state_keys:
        raw = {key: "empty"}
        if core1_redis.get(f'<ptr-{key}_state') is not None:
            raw = json.loads(core1_redis.get(f'<ptr-{key}_state')) 
        compiled_state[key] = raw

    return json.dumps(compiled_state)
@application.route('/status/all', methods=['GET', 'POST'])
def stream():
    refresh_frequency = .8

    sse = event_stream(refresh_frequency)
    resp = Response(sse, mimetype="text/event-stream")
   
    # Disable cache and buffering on SSE. 
    # Since SSEs are unending connections, buffering (from nginx) severly slows site performance.
    #resp.headers["Cache-Control"] = 'no-cache'
    #resp.headers["X-Accel-Buffering"] = 'no'
    return resp


import application.database_helpers as database

from application.helpers import utilities
@application.route('/altitude')
def alt():
    print(utilities.getAlt(3,89))
    return(jsonify(alt=utilities.getAlt(3,89)))

@application.route('/addtodatabase', methods=['POST', 'GET'])
@login_required
def addtodatabase():
    return database.add_to_database()
# Filter the display of objects by type.
# This route takes users selection and saves it in a session, to be read by tablelookup when the table is redrawn.
@application.route('/apply_table_filters', methods=['POST', 'GET'])
def apply_table_filters():
    return database.apply_table_filters()
# Dumps all data into a json file (geojson format) for use in the d3celestial sky chart.
@application.route('/database_to_json')
@login_required
def database_to_json():
    return database.database_to_json()
@application.route('/recreate_database')
@login_required
def recreate_database():
    return database.recreate_database()
@application.route('/merge_geojson')
@login_required
def merge_geojson():
    return database.merge_geojson()


@application.route('/', methods=['GET', 'POST'])
def home():
    return render_template('base.html', loginform=LoginForm(), cameraform=CameraForm(), filter=ObjectFilter(), site=site_attributes)


@application.route('/command/<msg>', methods=['POST'])
@login_required
def command(msg):

    cmd = []

    if msg == 'focus':
        button = request.form['command']
        cmd = cmd_focus(button)
        response = f"Focusing: {button}"
        return jsonify(response=response, requested="requested", processed=cmd[1], live=live_commands)
    if msg == 'focus-specific':
        print(request.form)
        val = request.form['focus_val']
        cmd = cmd_focus("value", val)
        response = f"Focusing to {val}."
        return jsonify(response=response, requested="requested", processed=cmd[1], live=live_commands)
    if msg == 'rotate':
        button = request.form['command']
        cmd = cmd_position_angle(button)
        response = f"Rotating: {button}"
        return jsonify(response=response, requested="requested", processed=cmd[1], live=live_commands)
    if msg == 'rotate-specific':
        print(request.form)
        val = request.form['pa_val']
        cmd = cmd_position_angle("angle", val)
        response = f"Rotating to {val} degrees."
        return jsonify(response=response, requested="requested", processed=cmd[1], live=live_commands)



    # Camera/Imaging Commands
    if msg == 'camera':
        form = CameraForm()
        print(form.time.data)
        print(form.count.data)
        print(form.delay.data)
        print(form.dither.data)
        print(form.autofocus.data)
        print(form.bin.data)
        print(form.filename_hint.data)
        print(form.size.data)
        print(form.filter.data)

        if form.validate_on_submit():
            time = form.time.data
            count = form.count.data
            delay = form.delay.data
            dither = form.dither.data
            autofocus = form.autofocus.data
            position_angle = form.position_angle.data
            filename_hint = form.filename_hint.data
            sitename = site_attributes['site_abbreviation']
            size = form.size.data
            bin = form.bin.data
            filter = form.filter.data
            cmd = cmd_expose(time, count, bin, dither, autofocus, filename_hint, sitename, size, delay, filter)
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
        cmd = cmd_ir(value)
    if msg == 'roof': 
        value = request.form['command']
        response = f"Enclosure roof is {value[:4]}ing."
        cmd = cmd_roof(value)
    if msg == 'parking': 
        value = request.form['command']
        response = f"Telescope is {value}ing."
        cmd = cmd_parking(value)
    if msg == 'flatscreen':
        value = request.form['command']
        param = request.form['param']
        response = f"Flat screen turned {value}."
        cmd = cmd_flatscreen(value, param)
    if msg == 'cover':
        value = request.form['command']
        param = request.form['param']
        response = f"Telescope cover set to {value}."
        cmd = cmd_cover(value, param)
    send(cmd)
    processed = cmd[1] if (len(cmd)>0) else ''
    return jsonify(response=response, requested="requested", processed=processed, live=live_commands)



from application.reference import all_dsos, all_stars, double_stars, nebula, galaxies, globular_clusters
from application.reference import open_clusters, everything_else
from sqlalchemy import and_, or_
from datatables import ColumnDT, DataTables
@application.route('/tablelookup')
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
    except: pass

    stellar_magnitudes = [-50,2.5] # default
    try:
        stellar_magnitudes = session['stellar_magnitudes']
    except: pass

    dso_types = all_dsos # default
    try:
        dso_types = session['dso_type_filter']
    except: pass

    dso_magnitudes = [-50,50] # default
    try:
        dso_magnitudes = session['dso_magnitudes']
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
@application.route('/starparty', methods=['GET', 'POST'])
def starparty():
    return render_template('starparty.html', filter=ObjectFilter())
#-------------------------------------------------------------------------------------------------------------#
@application.route('/testpage')
@login_required
def testpage():
    database = db.session.query(ThingsInSpace).all()
    return render_template('testpage.html', dbform=TestAddForm(), filter=ObjectFilter(), database=database)
#-------------------------------------------------------------------------------------------------------------#




#if __name__=='__main__':
#    application.run(host='10.15.0.15')
