import datetime, configparser
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u


class Utilities:

    def __init__(self):
       config = configparser.ConfigParser()
       config.read('../config.ini')
       self.lat = 34
       self.lon = -119 
       self.location = EarthLocation(lat=self.lat*u.deg, lon=self.lon*u.deg)

    def getAlt(self, ra, dec):
        time = Time.now() 
        c_eq = SkyCoord(ra, dec, unit=(u.hourangle, u.deg)) 
        c_aa = c_eq.transform_to(AltAz(obstime=time, location=self.location)) 
        return float(c_aa.alt.deg)

utilities = Utilities()



#import ephem
#def sidereal_time(lat, lon):
#    config = configparser.ConfigParser()
#    config.read('../config.ini')
#    site = ephem.Observer()
#    site.lon, site.lat = str(lon), str(lat)
#    site.date = datetime.datetime.utcnow()
#    return site.sidereal_time() 
