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
    return json.loads(redis_wx.set('weather_log_24hr'))

def main():
    threading.Thread(target=save_weather()).start()

if __name__=='__main__':
    main()
