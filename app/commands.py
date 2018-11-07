
import re 
# functions here should return an array with two strings:
#    array[0] is the key string for a redis command
#    array[1] is the value for a redis command, in the form of a dictionary(?)


def parse_goto_input(text):
    valid_ra = [0,24]
    valid_de = [0,90]

    # look for two numbers separated by a comma
    text.strip().lower()
    if text[0].isdigit():
        if text.find(',') or text.find(' '):
            if not ':' in text:
                pair = re.split(', |,| ',text)
                pair = [round(float(i),4) for i in pair]
                if pair[0] >= valid_ra[0] and pair[0] <= valid_ra[1] and\
                   pair[1] >= valid_de[0] and pair[1] <= valid_de[1]:
                    print('d') 
                    return pair
            
    return[-1,-1]

def cmd_slew(eq):
    key = '>ptr-mnt-1'
    val = {
        'command': 'slew',
        'ra': eq[0],
        'dec': eq[1]
    }
    return [key,val]

# park/unpark 
def cmd_mount(cmd):
    key = '>ptr-mnt-1'
    val = {
        'command': cmd
    }
    return [key, val]

# capture image(s)
def cmd_expose(time, count, binning):
    key = '>ptr-cam-1'
    val = {
        'time': time,
        'count': count,
        'bin': binning
    }
    return [key, val]

common_filters = ['u', 'U', 'B', 'PB', 'g', 'V', 'PG', 'r', 'R', 'PR', 'i', 'I', 'z', 'zs', 'L', 'PL', 'w', \
                  'W', 'HA', 'OIII', 'o3', 'SII', 's2', 'Silica', 'Si', 'si', 'Clr', 'clr', 'clear', 'air', \
                  'Air', 'AIR']
other_filters =  ['cR', 'Y', 'NIR', 'EXO', 'NII', 'N2', 'HB', 'HBC', 'DAO72', 'SM', 'RS', 'Dif1', 'Dif2', \
                  'Dif3', 'su', 'sb', 'sv', 'sy']
def cmd_filter(filter):
    ''' filter is a case-sensitive string matching an input from the filter arrays above. '''
    key = '>ptr-fil-1'
    val = {
        'command': filter
    }
    return [key, val]

def cmd_track(track_type, ra=0, de=0):
    ''' set tracking to off, sidereal, lunar, or custom rates given by ra and de arguments. '''
    key = '>ptr-mnt-1'
    val = {
        'tracking': track_type,
        'ra': ra,
        'de': de
    }
    return [key, val]


# Open/Close the dome roof
def cmd_dome(open_or_close):
    ''' open_or_close is a string either 'open' or 'close'.'''
    key = '>ptr-enc-1'
    val = {
        'command': open_or_close 
    }
    return [key, val]

# Visible lamp inside dome
def cmd_lamp(on_or_off):
    ''' on_or_off is a string either 'on' or 'off'.'''
    key = '>ptr-lamp-1'
    val = {
        'command': on_or_off
    }
    return [key, val]

# IR lamp inside dome
def cmd_ir(on_or_off):
    ''' on_or_off is a string either 'on' or 'off'.'''
    key = '>ptr-ir-1'
    val = {
        'command': on_or_off
    } 
    return [key, val]


