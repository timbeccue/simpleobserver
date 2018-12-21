import numpy as np
import json, threading, time, redis

# Note: serialize numpy matrix to send over redis:
#   l,w = A.shape
#   A2 = A.ravel().tostring()

# Retrieve from redis:
#   B = fromstring(A2).reshape(int(l), int(w))
#       or if number of entries (rows) is unknown:
#   B = fromstring(A2).reshape(-1, int(w))

# Unique redis server because decode_responses must be turned off.
redis_wx = redis.StrictRedis(host='10.15.0.15', port=6379, db=0, decode_responses=True)
core1_redis = redis.StrictRedis(host='10.15.0.15', port=6379, db=0, decode_responses=True)

def save_weather():
    wx_size = len(json.loads(core1_redis.get('<ptr-wx-1_state')))
    print(f'wx_size: {wx_size}')

    while(True):
        print('************************************************')
        # Get most recent weather status
        fresh_wx = json.loads(core1_redis.get('<ptr-wx-1_state'))
        keys = list(fresh_wx.keys())
        vals = list(fresh_wx.values())

        if 'weather_log_24hr' not in list(core1_redis.keys()):
            weather_log = [vals]
            weather_log_tosend = json.dumps(weather_log)
            redis_wx.set('weather_log_24hr', weather_log_tosend)

        # Get current log from redis_wx
        weather_log = json.loads(redis_wx.get('weather_log_24hr'))

        # Update weather log with new status
        print('checking for values')
        if weather_log[-1] != vals:
            print('adding values')
            weather_log.append(vals)

        # Delete row in log if timestamp is older than 24hrs.
        current_time = time.time()
        while ((current_time - float(weather_log[0][6])) > 86400):
            weather_log.pop(0)

        # Repost weather log to redis_wx
        weather_log_tosend = json.dumps(weather_log)
        redis_wx.set('weather_log_24hr', weather_log_tosend)

        # Wait for next weather status
        time.sleep(50)

def get_weather_log():
    return json.loads(redis_wx.get('weather_log_24hr'))



def main():
    threading.Thread(target=save_weather()).start()

if __name__=='__main__':
    main()



""" 
1545261660.5361636 at 3:31
1545262500.9408398 at 3:36
apscheduler for running this in the background automatically: https://stackoverflow.com/a/46738061

Notes:

Saving weather data for display in chart form has been solved by weather sites already (but reversed).

Recent past has lots of data saved (all data for past 1 week, 30/hr * 24hr * 7 = 5040). 
Previous month has some of the data saved (eg one datapoint each hour; 24*30 = 720).
Previous year has even less data saved (eg one datapoint every 12 hours; 2*365 = 730).

Save the three categories seperately:
W (week): filename should include oldest entry timestamp. when current time is 7 days and 1 hour past 
    the oldest entry, create a new file with everything except for the oldest hour. This way, there is 
    always a minimum of a full week of data. 
M (month): same design as W data, but with longer timescale. HOW TO ADD DATA? (avg, median, on the hour...)
Y (year): same design as M data. If recent data works well with >5000 records, might as well never delete old 
    records here. 


"""