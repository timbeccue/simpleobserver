

from app import app, db, core1_redis
from flask import Flask, render_template, request, Response, redirect, jsonify, url_for, flash, send_from_directory
import re, datetime, time, json, redis
import datetime

from app.state import ptr_state
from app.commands import *
from flask_login import current_user, login_user, logout_user, login_required

# from sqlalchemy-datatables example
from datatables import ColumnDT, DataTables
from app.models import User, Dso, Hygdatum

expire_time = 120 #seconds
live_commands = True

####################################################################################

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DecimalField, SelectField
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
    time = DecimalField('Exposure Time', validators=[DataRequired()])
    count = IntegerField('Count', default=1, validators=[DataRequired(), NumberRange(min=1)])
    delay = DecimalField('Delay', default=0)
    dither = SelectField('Dithering', default='off', choices=[('off','off'), ('on','on'), ('random','random')])
    bin = SelectField('Binning', default='1', choices=[('1','1'), ('2','2'), ('4','4')])
    filter = SelectField('Filter', default='c', choices=[('c','Clear'), ('r','Red'), ('g','Green'), ('b','Blue')])
    capture = SubmitField(' Capture')

####################################################################################

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

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', state=ptr_state, loginform=LoginForm(), cameraform=CameraForm())

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

    #if category == 'enclosure':
        #device = request.form['command']
        #checked = request.form['checked']
        #on_off = 'on' if checked=='true' else 'off'
        #open_close = 'open' if checked=='true' else 'close'
        #if device == 'lamp':
            #cmd = cmd_lamp(on_off)
            #logtext = f"Light {on_off}"
            #send(cmd)
        #if device == 'ir-lamp':
            #cmd = cmd_ir(on_off)
            #logtext = f"IR Lamp {on_off}"
            #send(cmd)
        #if device == 'roof':
            #cmd = cmd_roof(open_close)
            #logtext = f"{open_close} roof"
            #send(cmd)

    if category == 'goto':
        text = request.form['goto-box']
        logtext = 'goto: ' + text
        coordinates = parse_goto_input(text)
        cmd = cmd_slew(coordinates)
        print('from /command')
        print(cmd)
        send(cmd)

    ##TODO: finish camera command
    #if category == 'camerasettings':
        ## initialize with default values
        #number_images = 1
        #between_images = 0
        #start_delay = 0
        #bin = 1
        ## get form values
        #time = request.form['exposure-time']
        #filter = request.form['filter']
        #number_images = request.form['number-of-images']
        #between_images = request.form['time-between-images']
        #start_delay = request.form['start-delay']
        #bin = request.form['camera-binning']
#
        #cmd = cmd_expose(time, number_images, bin, start_delay, between_images, filter)
        #logtext = f"Exposure: {time}s, {filter} filter, {number_images}x."
        #send(cmd)




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
            bin = form.bin.data
            filter = form.filter.data
            cmd = cmd_expose(time,count,bin,delay,filter,dither)
            send(cmd)

    if msg == 'lamp': send(cmd_parking(request.form['command']))
    if msg == 'ir-lamp': send(cmd_ir(request.form['command']))
    if msg == 'roof': send(cmd_roof(request.form['command']))
    if msg == 'parking': send(cmd_parking(request.form['command']))

    return jsonify(requested="requested")

@app.route('/tablelookup')
def tablelookup():
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
