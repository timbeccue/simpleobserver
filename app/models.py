
# coding: utf-8
from sqlalchemy import Column, Float, Integer, Table, Text
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base
from app import db

Base = declarative_base()
metadata = Base.metadata

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Forms

from app.reference import object_types, seasons, constellations

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




class ThingsInSpace(db.Model):
    __bind_key__ = 'things_in_space'

    id = db.Column(db.Integer, primary_key=True)
    messier = db.Column(db.Integer, unique=True)
    ngc = db.Column(db.String)
    bayer = db.Column(db.String)
    type = db.Column(db.String, nullable=False)
    magnitude = db.Column(db.Float)
    magnitude2 = db.Column(db.Float)
    size_large = db.Column(db.Float)
    size_small = db.Column(db.Float)
    distance_ly = db.Column(db.Integer)
    ra_decimal = db.Column(db.Float, nullable=False)
    de_decimal = db.Column(db.Float, nullable=False)
    position_anble = db.Column(db.Float)
    separation_angle = db.Column(db.Float)
    spectral_class = db.Column(db.String)
    season = db.Column(db.String)
    constellation = db.Column(db.String)
    names = db.Column(db.String)
    data_origin = db.Column(db.String)



    def __init__(self, **kwargs):
        for attr in ('messier', 'ngc', 'bayer', 'type', 'magnitude', 'magnitude2', 'size_large', 'size_small', 'distance_ly', 'ra_decimal',
                     'de_decimal', 'position_angle', 'separation_angle', 'spectral_class', 'season', 'constellation', 'names', 'data_origin'):
            setattr(self, attr, kwargs.get(attr))

    def __repr__(self):
        return f'<ID:{self.id}, M{self.messier}, {self.type}, {self.magnitude}>'

class User(UserMixin, db.Model):
    __bind_key__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Dso(db.Model):
    __bind_key__ = 'astro'
    __tablename__ = 'dso'

    RightAscension = db.Column(Float)
    Declination = db.Column(Float)
    NGCType = db.Column(Text)
    Constellation = db.Column(Text)
    Magnitude = db.Column(Float)
    CommonName = db.Column(Text)
    RARadians = db.Column(Float)
    DecRadians = db.Column(Float)
    id = db.Column(Integer, primary_key=True)
    SemiMajorAxes = db.Column(Float)
    SemiMinorAxes = db.Column(Float)
    PositionAngle = db.Column(Float)
    dso_source = db.Column(Integer)
    PrimaryNumberID = db.Column(Integer)
    PrimaryCatalogName = db.Column(Text)
    AdditionalNumberID = db.Column(Integer)
    AdditionalCatalogName = db.Column(Text)
    DuplicateNumberID = db.Column(Integer)
    DuplicateCatalogName = db.Column(Text)
    DisplayMagnitude = db.Column(Float)

class Hygdatum(db.Model):
    __tablename__ = 'hygdata'

    id = db.Column(Integer, primary_key=True)
    HipparcosID = db.Column(Text)
    HenryDraperID = db.Column(Text)
    HarvardRevisedID = db.Column(Text)
    GlieseID = db.Column(Text)
    BayerFlamsteed = db.Column(Text)
    ProperName = db.Column(Text)
    RightAscension = db.Column(Float)
    Declination = db.Column(Float)
    DistanceInParsecs = db.Column(Float)
    ProperMotionRA = db.Column(Float)
    ProperMotionDec = db.Column(Float)
    RadialVelocity = db.Column(Float)
    Magnitude = db.Column(Float)
    AbsoluteMagnitude = db.Column(Float)
    SpectralType = db.Column(Text)
    ColorIndex = db.Column(Text)
    CartesianX = db.Column(Float)
    CartesianY = db.Column(Float)
    CartesianZ = db.Column(Float)
    CartesianVelocityX = db.Column(Float)
    CartesianVelocityY = db.Column(Float)
    CartesianVelocityZ = db.Column(Float)
    RARadians = db.Column(Float)
    DecRadians = db.Column(Float)
    ProperMotionRARadians = db.Column(Float)
    ProperMotionDecRadians = db.Column(Float)
    Bayer = db.Column(Text)
    Flamsteed = db.Column(Text)
    Constellation = db.Column(Text)
    CompanionID = db.Column(Text)
    CompanionPrimary = db.Column(Text)
    MultiStarCatalogID = db.Column(Text)
    Luminosity = db.Column(Float)
    VariableDesignation = db.Column(Text)
    VariableMinimum = db.Column(Float)
    VariableMaximum = db.Column(Float)

class Constellation(db.Model):
    __tablename__ = 'constellation'

    Code = db.Column(Text, primary_key=True)
    FullName = db.Column(Text)
