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

expire_time = 120 #seconds
live_commands = True

####################################################################################

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, SelectField, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), ])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CameraForm(FlaskForm):
    time = FloatField('Exposure Time', validators=[DataRequired()])
    count = IntegerField('Count', default=1, validators=[DataRequired(), NumberRange(min=1)])
    delay = FloatField('Delay (s)', default=0)
    dither = SelectField('Dithering', default='off', choices=[('off','off'), ('on','on'), ('random','random')])
    bin = SelectField('Binning', default='1', choices=[('1','1'), ('2','2'), ('4','4')])
    filter_choices = [('PL', 'Clear'), ('PR', 'Red'), ('PG', 'Green'), ('PB', 'Blue'), ('S2', 'S2'), ('HA', 'H\u03B1'),
                      ('O3', 'O3'), ('N2', 'N2')]
    filter = SelectField('Filter', default='c', choices=filter_choices)
    capture = SubmitField(' Capture')

    autofocus = BooleanField('Autofocus', default=1)

    position_angle = FloatField('Position Angle', default=0, validators=[DataRequired(),
                                NumberRange(min=0, max=360, message="Please enter a value between 0 and 360.")])

class ObjectFilter(FlaskForm):
    open_clusters = BooleanField('open clusters', default=1)
    globular_clusters = BooleanField('globular clusters', default=1)
    galaxies = BooleanField('galaxies', default=1)
    nebula = BooleanField('nebula', default=1)

    stars = BooleanField('stars', default=1)
    double_stars = BooleanField('double stars', default=1)

    dso_magnitude_min = FloatField('DSOs no brighter than: ')
    dso_magnitude_max = FloatField('DSOs no fainter than: ')
    star_magnitude_min = FloatField('Stars no brighter than: ')
    star_magnitude_max = FloatField('Stars no fainter than: ', default=2.5)

    everything_else = BooleanField('everything else', default=1)

####################################################################################


####################################################################################
from app.weather_logging import weatherlogger
from apscheduler.schedulers.background import BackgroundScheduler

weather_logger = BackgroundScheduler(daemon=True)
weather_logger.add_job(weatherlogger.log_everything, 'interval', seconds=55)
weather_logger.start()

####################################################################################

import pandas as pd
@app.route('/plot_weather/<logtype>', methods=['GET', 'POST'])
def plot_weather(logtype):
    weather_log = weatherlogger.check_for_logs(logtype)
    print(weather_log)
    w_data = pd.read_csv(weather_log)

    # Select every 10th datapoint from the last day, giving ~70 datapoints.
    timestamps = list(map(lambda x: x * 1000, list(w_data['timestamp'][-600::])))
    temperatures = list(w_data['amb_temp C'][-600::])
    print(timestamps)
    print(temperatures)
    
    #x_time = [1,2,3,4,5]
    #y_temp = [2,9,8,1,0]
    to_plot = {
        "x": timestamps, 
        "y": temperatures 
    }
    return jsonify(to_plot)


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

from flask import session

object_types = [
    ('As', 'Asterism'),
    ('Ds', 'Double Star'),
    ('MW', 'Milky Way Patch'),
    ('Oc', 'Open Cluster'),
    ('Gc', 'Globular Cluster'),
    ('Pl', 'Planetary Nebula'),
    ('Di', 'Diffuse nebula'),
    ('Bn', 'Bright Nebula'),
    ('Dn', 'Dark Nebula'),
    ('Sn', 'Supernova Remnant'),
    ('Cg', 'Clustered Galaxies'),
    ('Sp', 'Spiral Galaxy'),
    ('Ba', 'Barred Galaxy'),
    ('Ir', 'Irregular Galaxy'),
    ('El', 'Elliptical Galaxy'),
    ('Ln', 'Lenticular Galaxy'),
    ('Px', 'Perculiar Galaxy'),
    ('Sx', 'Seyfert Galaxy')
    ]

seasons = [
    ('summer', 'Summer'),
    ('autumn', 'Autumn'),
    ('winter', 'Winter'),
    ('spring', 'Spring')
    ]

constellations = [
    ('And', 'Andromeda'),
    ('Ant', 'Antlia'),
    ('Aps', 'Apus'),
    ]

class TestAddForm(FlaskForm):
    type = SelectField('Type', choices=object_types)
    magnitude = FloatField('Magnitude', validators=[NumberRange(min=-30, max=100), DataRequired()])
    size_large = FloatField('Size-Large')
    size_small = FloatField('Size-Small')
    distance_ly = FloatField('Distance [ly]')
    ra_decimal = FloatField('Right Ascension', validators=[NumberRange(min=0, max=24), DataRequired()])
    de_decimal = FloatField('Declination', validators=[NumberRange(min=0, max=90), DataRequired()])
    season = SelectField('Season', choices=seasons)
    constellation = SelectField('Constellation', choices=constellations)
    names = StringField('Object Name(s)')


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

all_dsos = {'As','MW','Oc','Gc','Pl','Di','Bn','Dn','Sn','Cg','Sp','Ba','Ir','El','Ln','Px','Sx'}
all_stars = {'star', '**', 'Ds'}
double_stars = {'Ds', '**'}
nebula = {'Pl','Di','Bn','Dn', 'Sn'}
galaxies = {'Cg','Sp','Ba','Ir','El','Ln','Px','Sx'}
globular_clusters = {'Gc'}
open_clusters = {'Oc'}
everything_else = {'As','MW'} # Asterisms, Milky Way

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
#############################################
#############################################




@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', state=ptr_state, loginform=LoginForm(), cameraform=CameraForm(), filter=ObjectFilter())

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

@app.route('/command', methods=['POST'])
@login_required
def command():
    print("form dict: "+str(request.form.to_dict()))
   # print("button val: "+str(request.form['roof']))
    category = request.form['category']

    text = str(request.form.to_dict())
    cmd = ['','']
    logtext = ''

    if category == 'goto':
        text = request.form['goto-box']
        logtext = 'goto: ' + text
        coordinates = parse_goto_input(text)
        cmd = cmd_slew(coordinates)
        print('from /command')
        print(cmd)
        send(cmd)

    requested = str(datetime.datetime.now()).split('.')[0]+": . . . . . \t"+logtext
    processed = cmd[1] if (len(cmd)>0) else ''
    return jsonify(requested=requested, processed=processed, live=live_commands)

@app.route('/command/<msg>', methods=['POST'])
def command1(msg):
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
            return jsonify(requested="requested", processed=cmd[1], live=live_commands)
        return jsonify(errors=form.errors)

    if msg == 'lamp': send(cmd_parking(request.form['command']))
    if msg == 'ir-lamp': send(cmd_ir(request.form['command']))
    if msg == 'roof': send(cmd_roof(request.form['command']))
    if msg == 'parking': send(cmd_parking(request.form['command']))

    processed = cmd[1] if (len(cmd)>0) else ''
    return jsonify(requested="requested", processed=processed, live=live_commands, errors=form.errors)

@app.route('/tablelookup1')
def tablelookup1():
    """Return server side data for object table"""
    columns = [
        ColumnDT(Dso.PrimaryCatalogName),
        ColumnDT(Dso.PrimaryNumberID),
        ColumnDT(Dso.Magnitude),
        ColumnDT(Dso.RightAscension),
        ColumnDT(Dso.Declination),
        ColumnDT(Dso.NGCType)
    ]

    # define the initial query
    query = db.session.query().filter(Dso.Magnitude < 25)

    # GET parameters
    params = request.args.to_dict()

    # instantiating a DataTable for the query and table
    rowTable = DataTables(params, query, columns)

    # returns data to DataTable
    return jsonify(rowTable.output_result())

if __name__=='__main__':
    app.run(host='10.15.0.15')
