
import pandas as pd

def MessierToDatabase():
    data = pd.read_csv('app/static/mapdata/messier.csv')
    mdict = {col: list(data[col]) for col in data.columns}

    obj_columns = ['type','magnitude','size_large','size_small','distance_ly','ra_decimal','de_decimal','season','constellation','names']


    object_types = {
        'Asterism':'As',
        'Double Star':'Ds',
        'Milky Way Patch':'MW',
        'Open Cluster':'Oc',
        'Globular Cluster':'Gc',
        'Planetary Nebula':'Pl',
        'Diffuse Nebula':'Di',
        'Bright Nebula':'Bn',
        'Dark Nebula':'Dn',
        'Supernova Remnant':'Sn',
        'Clustered Galaxies':'Cg',
        'Spiral Galaxy':'Sp',
        'Barred Galaxy':'Ba',
        'Irregular Galaxy':'Ir',
        'Elliptical Galaxy':'El',
        'Lenticular Galaxy':'Ln',
        'Perculiar Galaxy':'Px',
        'Seyfert Galaxy':'Sx',
        'Binary Star':'**'
        }

    ready = []

    for i in range(110):

        obj = {}
        obj['messier'] = int(mdict['Object'][i].split('|')[0][1:])
        obj['ngc'] = mdict['NGC#'][i]
        obj['type'] = object_types[mdict['Detailed Type'][i]]
        obj['magnitude'] = float(mdict['Magnitude'][i])
        obj['size_large'] = float(mdict['Size (arcminutes)'][i])
        obj['ra_decimal'] = float(mdict['RA (h)'][i])
        obj['de_decimal'] = float(mdict['DEC (deg)'][i])
        obj['constellation'] = mdict['Constellation'][i]
        obj['names'] = mdict['Common Name'][i]

        ready.append(obj)

    return ready

#    Make sure db doesn't contain the objects about to add 
#
#    in flask shell with database = TIS and m2d = MessierToDatabase:
#    messiers = m2d()
#    for o in messiers:
#        obj = TIS(**o)
#        db.session.add(obj)
#        db.session.commit()
