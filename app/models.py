
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

class User(UserMixin, db.Model):
    __bind_key__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)    

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
#
#t_ngc = Table(
#    'ngc', metadata,
#    db.Column('Abbrev', Text),
#    db.Column('Description', Text)
#)
#
#
#t_sqlite_stat1 = Table(
#    'sqlite_stat1', metadata,
#    db.Column('tbl', NullType),
#    db.Column('idx', NullType),
#    db.Column('stat', NullType)
#)
#
#
#t_sqlite_stat4 = Table(
#    'sqlite_stat4', metadata,
#    db.Column('tbl', NullType),
#    db.Column('idx', NullType),
#    db.Column('neq', NullType),
#    db.Column('nlt', NullType),
#    db.Column('ndlt', NullType),
#    db.Column('sample', NullType)
#)