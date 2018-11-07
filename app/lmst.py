import ephem, datetime, configparser

def sidereal_time(lat, lon):
    config = configparser.ConfigParser()
    config.read('../config.ini')
    site = ephem.Observer()
    site.lon, site.lat = str(lon), str(lat)
    site.date = datetime.datetime.utcnow()
    return site.sidereal_time() 