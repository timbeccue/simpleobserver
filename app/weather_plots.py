
import pandas as pd
import json
import plotly 
from datetime import datetime, date, time, timedelta

from app.weather_logging import weatherlogger


def create_plot(logtype):

    # Get filename of current log and open as pandas dataframe.
    weather_log = weatherlogger.check_for_logs(logtype)
    weather_data = pd.read_csv(weather_log)

    minutes = 0 # Number of data points (1 per minute)
    interval = 40   # Plot one point for every [interval] points in log 

    # x-axis is time
    times = list(weather_data['timestamp'][minutes::interval])
    times = list(map(lambda x: 1000*x, times)) # Convert timestamp to miliseconds (for plotly.js dates)
    
    # y-axis from weather data
    temperatures = list(weather_data['amb_temp C'][minutes::interval])
    dewpoints = list(weather_data['dewpoint C'][minutes::interval])

    # Specify plot layout settings.
    layout = dict(
        title = 'Temperature',
        xaxis = dict(
            #title = 'time',
            type = 'date',
            range = [datetime.now()-timedelta(days=1), datetime.now()],
            dtick = 3600 * 3 * 1000, # 3 hours in milliseconds
            linecolor = '#333',
            linewidth = 2,
            gridcolor = '#444',
            gridwidth = 1
        ),
        yaxis = dict(
            title = 'temperature [deg C]',
            linecolor = '#333',
            linewidth = 2,
            gridcolor = '#444',
            gridwidth = 1
        ),
        legend = dict(
            x = 0,
            y = 1.2
        ),
        margin = plotly.graph_objs.layout.Margin(
            l=50,
            r=0,
            t=100,
            b=50
        ),
        paper_bgcolor = 'rgba(0,0,0,0)', 
        plot_bgcolor = 'rgba(0,0,0,0)', 
        font = dict(color = 'aaa')
    )

    # Specify the various plots:
    temperatures_data = dict(
        name = 'Ambient Temp',
        x =times,
        y = temperatures,
        mode = 'lines+markers',
        line = dict(
            width = 0.5,
            shape = 'spline'
        )
    )
    dewpoints_data = dict(
        name = 'Dewpoint Temp',
        x = times,
        y = dewpoints,
        mode = 'lines+markers',
        line = dict(
            width = 0.5,
            shape = 'spline'
        )
    )

    graphs = [
        dict(
            data = [temperatures_data, dewpoints_data],
            layout = layout
        )
    ]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
