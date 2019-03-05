# app/reference.py
# This is a place to store useful information referenced thorughout the app.

all_dsos = {'As','MW','Oc','Gc','Pl','Di','Bn','Dn','Sn','Cg','Sp','Ba','Ir','El','Ln','Px','Sx'}
all_stars = {'star', '**', 'Ds'}
double_stars = {'Ds', '**'}
nebula = {'Pl','Di','Bn','Dn', 'Sn'}
galaxies = {'Cg','Sp','Ba','Ir','El','Ln','Px','Sx'}
globular_clusters = {'Gc'}
open_clusters = {'Oc'}
everything_else = {'As','MW'} # Asterisms, Milky Way

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



common_filters = ['u', 'U', 'B', 'PB', 'g', 'V', 'PG', 'r', 'R', 'PR', 'i', 'I', 'z', 'zs', 'L', 'PL', 'w', \
                  'W', 'HA', 'OIII', 'o3', 'SII', 's2', 'Silica', 'Si', 'si', 'Clr', 'clr', 'clear', 'air', \
                  'Air', 'AIR']
other_filters =  ['cR', 'Y', 'NIR', 'EXO', 'NII', 'N2', 'HB', 'HBC', 'DAO72', 'SM', 'RS', 'Dif1', 'Dif2', \
                  'Dif3', 'su', 'sb', 'sv', 'sy']


# Used in CameraForm to populate the filter selection box.
filter_choices = [
    ('LUMINANCE', 'LUMINANCE'),
    ('RED', 'RED'), 
    ('GREEN', 'GREEN'), 
    ('BLUE', 'BLUE'), 
    ('O3', 'O3'), 
    ('HA', 'HA'), 
    ('S2', 'S2'), 
    ('N2', 'N2'), 
    ('CONTINUUM', 'CONTINUUM'),
    ('LRGB', 'LRGB'), 
    ('w', 'w'), 
    ('u', 'u'), 
    ('g', 'g'), 
    ('r', 'r'), 
    ('i', 'i'), 
    ('zs', 'zs'), 
    ('wgri', 'wgri'), 
    ('DARK', 'DARK'), 
    ('AIR', 'AIR')
    ]