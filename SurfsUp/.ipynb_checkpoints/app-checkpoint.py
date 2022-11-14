# Import Dependencies
import numpy as np
import sqlachemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


import datetime as dt
from dateutil.relativedelta import relativedelta


# Database Setup and creating an engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the table
measurement = base.classes.measurement
station = base.classes.station

# App Setup
app = Flask(__name__)


# Create home page route
@app.route("/")
def main():
    return (
        f"Welcome to the Climate App Home Page!<br>"
        f"Available Routes Below:<br>"
        f"Precipitation measurement over the last 12 months: /api/v1.0/precipitation<br>"
        f"A list of stations and their respective station numbers: /api/v1.0/stations<br>"
        f"Temperature observations at the most active stations over the previous 12 months: /api/v1.0/tobs<br>"
        f"Enter a start date (yyyy-mm--dd) to retrieve the minimum, maximum, and average temperatures for all dates after the specified date: /api/v1.0/<start><br>
        f"Enter both a start and end date (yyyy-mm-dd) to retrieve the minimum, maximum, and average temperatures for that date range: /api/v1.0/<start>/<end><br>
    )


# Create Precipitation route of the last 12 months of precipitation data
@app.route("api/v1.0/precipitation")
def precip():
    
    recent_prcp = session.query(str(measurement.date).measurement.prcp)\
    .filter(measurement.date > '2016-08-22')\
    .filter(measurement.date <= '2017-08-23')\
    .order_by(measurement.date).all()
    
    # Convert results to a dictionary with date as key and pcrp as value 
    prcp_dict = dict(prcp_dict)
    
    # Return json list of dict   
    return jsonify(prcp_dict)

# Create station route of a list of the stations in the dataset
@app.route("api/v1.0/precipitation")
def stations():
    
    stations = session.query(station.name, station.station).all()
    
    # Convert the results to dict
    station_dict = dict(stations)
    
    # Return json list of dict
    return jsonify(station_dict)

# Create tobs route of temp observations for most active station over last 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    
    tobs_station = session.query(str(measurement.date), measurement.tobs).filter\
    (measurement.date > '2016-08-23').filter(measurement.date <= '2017-08-23')\
    .filter(measurement.station == "USC00519281").order_by(measurement.date).all()
    
    # Convert results to dict
    tobs_dict = dict(tobs_station)
    
    # Return Json list of dict
    return jsonify(tobs_dict)

# Create start/end route and calculate min, max and average temps for a given date
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_date(start, end=None):
    
    q = session.query(str(func.min(measurement.tobs)), str(func.max(measurement.tobs)), str(func.avg(measurement.tobs))))
    
    if start:
        q = q.filter(measurement.date >= start)
        
    if end:
        q = q.filter(measurement.date <= end)
        
        
    # Convert results into dict
    
    results = q.all()[0]
    
    keys = ["Min Temp", "Max Temp", "Avg Temp"]
    
    temp_dict = {keys[i]: results[i] for i in range(len(keys))}
    
    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)