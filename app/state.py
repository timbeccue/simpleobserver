from app import core1_redis, site_attributes
from configparser import ConfigParser
import ephem, datetime, json
    # need something to hold status states: telescope ra, dec, altitude, action, dome, sidereal time, etc.
    # class for: observatory, enclosure/dome, ota, rotator, focuser, guider, filter, camera

class State:

    lat = site_attributes['lat']
    lon = site_attributes['lon']

    def __init__(self):
        self.ra = 14 
        self.de = 10 
        self.telescope_action = "-"
        self.dome = "-"
        self.lmst = self.sidereal_time()
        self.lat = State.lat
        self.lon = State.lon
        self.mount = []
       # self.enclosures = []
       # self.mounts = []
       # self.otas = []
       # self.focusers = []
       # self.rotators = []
       # self.filterwheels = []
       # self.cameras = []
       # self.lamps = []
        
    
    def sidereal_time(self):
        site = ephem.Observer()
        site.lon, site.lat = str(State.lon), str(State.lat)
        site.date = datetime.datetime.utcnow()
        lmst = site.sidereal_time() * 12 / 3.1415927
        return round(lmst, 3)

    def get_state(self): 
        self.lmst = self.sidereal_time()
        return (self.__dict__)

    def set_coordinate_selection(self, ra, de):
        self.ra_selected = ra
        self.de_selected = de

    def new_mount(self, mount_id):
        self.mount = Mount(mount_id)

    
            
class Mount:

    def __init__(self, id):
        self.id = id

    def set_from_redis(self, var):
        for key, value in var.items():
            setattr(self,key,value)
    def set_state(self):
        key = '<ptr-enc1-mnt'+str(self.id)+'_state'
        state = json.loads(core1_redis.get(key))
        if state:
            self.__dict__.update(state)
    def get_state(self):
        self.set_state()
        return (self.__dict__)


ptr_state = State()