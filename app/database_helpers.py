# app/database_helpers.py

from app import app, db
from app.reference import all_dsos, all_stars, double_stars, nebula, galaxies, globular_clusters
from app.reference import open_clusters, everything_else, object_types, seasons, constellations
from app.models import User, Dso, ThingsInSpace, TestAddForm, ObjectFilter

import re, json

from datatables import ColumnDT, DataTables
from flask import session, request, redirect, url_for, jsonify


def oneplusone():
    return jsonify(one=1, two=2)

def add_to_database():
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



# Filter the display of objects by type.
# This route takes users selection and saves it in a session, to be read by tablelookup when the table is redrawn.
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



# Dumps all data into a json file (geojson format) for use in the d3celestial sky chart.
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