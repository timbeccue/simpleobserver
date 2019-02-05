
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



Assuming file exists:
    get oldest time from filename
    get newest time from top line
    if oldest-newest < 1 week, 1hr: 
        append to top
    if oldest:
        write new file with timestamp of 1 week ago 
        read each line in old file, if date < 1 week old, write to new file. 
"""


import json, time, os, csv, glob
from application import core1_redis as redis


class WeatherLogger():

    def __init__(self):
        self.redis = redis
        self.site = "PTR"
        self.timestamp_index = 9
        self.folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "weatherlogs")
        self.filebase = "_weather_" + self.site + "_"
        self.log_size = {"W":60480000, "M": 2592000, "Y": 315360000} # seconds: 7 days, 30 days, 10 years 
        self.log_buffer = {"W":3600, "M": 86400, "Y": 315360000} # seconds: 1 hour, 1 day, 10 years

    def current_data(self):
        """ Return the most recent weather data from redis as a dictionary """
        if self.redis.exists('<ptr-wx-1_state'):
            return json.loads(self.redis.get('<ptr-wx-1_state'))
        else:
            return False
    
    def _init_log(self, logtype):
        """ logtype is either "W", "M", or "Y". """
        if logtype == None: 
            print("Error: no logtype given")
            return -1
        data = self.current_data()
        filename = os.path.join(self.folder, logtype + self.filebase + str(int(float(data["timestamp"]))) + ".csv") 
        self._write_data(logtype, filename, data)
        return filename
    
    def _write_data(self, logtype, filename, data):
        with open(filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, data.keys())
            if f.tell() == 0:
                writer.writeheader()
                writer.writerow(data)
            else: 
                last_entry = self._get_newest_timestamp(filename)
                # Don't rewrite the same data
                if data['timestamp'] != last_entry:
                    writer.writerow(data)

    def _get_newest_timestamp(self, filename):
        """ Return a string containing the timestamp from the most recent log entry """
        lines = []
        N = 10
        with open(filename) as f:
            for line in csv.reader(f):
                lines.append(line)
                if len(lines) > N:
                    lines.pop(0)
        return lines[-1][self.timestamp_index]

    def _get_oldest_timestamp(self, filename):
        """ Return a string containing the timestamp of the oldest log entry (from the filename).
            This timestamp has been rounded to the nearest second to avoid decimals in the filename. 
            Expects format of '*##########.csv' where # is an int (10 in a row). """
        return  filename[-14:-4]

    def _is_expired(self, logtype, timestamp):
        """ Return true if given timestamp of given logtype has expired. """
        max_diff = self.log_size[logtype]
        now = time.time()
        if now - int(timestamp) > max_diff:
            return True 
        return False

    def check_for_logs(self, logtype):
        """ Returns filename of most recent log of type in ["W", "M", "Y"].
            Checks if an active log exists.
            If not, it creates a new log with recent data.
            If multiple logs exist, return the newest log after deleting all others. """ 

        searchname = os.path.join(self.folder, logtype + self.filebase + '*.csv')
        timestamps = [self._get_oldest_timestamp(name) for name in glob.glob(searchname) if os.path.isfile(name)]

        # If no existing log: create a new one
        if len(timestamps) == 0: return self._init_log(logtype)

        # Delete all logs that are not newest. 
        timestamps.sort(key=int)
        for t in timestamps[:-1]:
            os.remove(os.path.join(self.folder, logtype + self.filebase + t + ".csv"))
        return os.path.join(self.folder, logtype + self.filebase + timestamps[-1] + ".csv")

    def _remove_expired_data(self, logtype, log):
        """ With the given log, copy the header and all non-expired entries to a new file, with a new
            filename reflecting the new "oldest timestamp". """

        data = self.current_data()
        data_time = int(float(data['timestamp']))

        with open(log, 'r') as old_log:
            # Read lines from newest to oldest. Save the previous line's timestamp. 
            # If the current line's timestamp is older than the expiration timeframe, then 
            # take all the more recent lines and read them into a new file, and use the oldest
            # time from the new file in the file's filename.
            oldest_valid_timestamp = data_time
            old_log.readline() # Skip the header row
            for line in csv.reader(old_log):
                if data_time - int(float(line[self.timestamp_index])) < self.log_size[logtype]:
                    print(f"Broke on {int(float(line[self.timestamp_index]))}")
                    oldest_valid_timestamp = int(float(line[self.timestamp_index]))
                    break

        new_filename = os.path.join(self.folder, logtype + self.filebase + str(oldest_valid_timestamp) + ".csv")
        with open(log) as old_log, open(new_filename, 'w', newline="") as new_log:
            writer = csv.writer(new_log, delimiter=",")
            linecounter = 0
            for line in csv.reader(old_log):
                if linecounter == 0 or int(float(line[self.timestamp_index])) >= oldest_valid_timestamp:
                    writer.writerow(line)
                    print(line[self.timestamp_index])
                linecounter += 1
            writer.writerow

        return new_filename

    def update_log(self, logtype):

        log = self.check_for_logs(logtype)
        data = self.current_data()
        if data is False:
            print(f"{int(time.time())} - Unable to retrieve weather data from redis.")
            return "Failure"
        oldest_log_time = int(self._get_oldest_timestamp(log))
        data_time = int(float(data['timestamp']))

        if data_time - oldest_log_time > self.log_size[logtype] + self.log_buffer[logtype]:
            log = self._remove_expired_data(logtype, log)

        self._write_data(logtype, log, data)
        return "Success"

    def weather_is_broadcasting(self):
        if self.redis.exists('<ptr-wx-1_state'): return True
        else: 
            print("Weather Logger: Unable to retrieve weather information.")
            return False

    def log_exists(self, logtype):
        searchname = os.path.join(self.folder, logtype + self.filebase + '*.csv')
        return len(glob.glob(searchname)) > 0
                
    def log_everything(self):
        if self.weather_is_broadcasting():
            self.update_log("W")
            
weatherlogger = WeatherLogger()


                










    
