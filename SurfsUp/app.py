# importing dependencies
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta

# setting up the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflecting an existing database into a new model
Base = automap_base()

# reflecting the tables
Base.prepare(engine, reflect=True)

# saving the reference to the tables
measurement = Base.classes.measurement
station = Base.classes.station

# setting up Flask
app = Flask(__name__)

# Flask routes - starting at homepage and listing all available routes
@app.route("/")
def home():
    return(
        f"(Abraham's SQLAlchemy Challenge). <br><br>"
        f"Available Routes: <br>"

        f"/api/v1.0/precipitation<br/>"
        f"Returns dates and temperature from the last year in data set. <br><br>"

        f"/api/v1.0/stations<br/>"
        f"Returns a list of stations. <br><br>"

        f"/api/v1.0/tobs<br/>"
        f"Returns list of Temperature Observations for last year in data set. <br><br>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"Returns an Average, Max, and Min temperatures for a given start date.<br><br>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"Returns an Average, Max, and Min temperatures for a given date range."
   ) 
    
    # Query_date to consider 12 months from the last entry in the database
query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return a list of precipitation data including the date, prcp of each precipitation"""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all precipitation
    # Perform a query to retrieve the date and precipitation scores
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= query_date).\
        order_by(measurement.date.desc()).all()

    # Closing the session
    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)
        
    return jsonify(all_precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    result2 = session.query(station.station).distinct().all()
    session.close()

    station_list = list(np.ravel(result2))
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    results = session.query(station.name, measurement.date, measurement.tobs).\
        filter(measurement.date >= "2016-08-24", measurement.date <= "2017-08-23").\
        all()
    tobs_list = []
    for result in results:
        row = {}
        row["Station"] = result[0]
        row["Date"] = result[1]
        row["Temp"] = int(result[2])
        tobs_list.append(row)
    session.close()
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def between_dates(start, end = None):
    # create session
    session = Session(engine)

# For a given start, calculate TMIN, TAVG, and TMAX for all the 
# dates greater than or equal to the start date.
    if end is None:
        end = session.query(func.max(measurement.date)).first()[0]

# For a given start date and end date, calculate TMIN, TAVG, and TMAX 
# for the start date to the end date included
    q_tobs = session.query(
        measurement.date, 
        measurement.tobs
        ).filter(measurement.date >= start
        ).filter(measurement.date <= end)
 
    tobs_df = pd.DataFrame(q_tobs, columns=['date', 'tobs'])

    # close session
    session.close()

    return f"The temperature analysis between the dates {start} are {end}: \n\
        Minimum: {tobs_df['tobs'].min()} F, \n\
        Maximum: {tobs_df['tobs'].max()} F, \n\
        Average: {tobs_df['tobs'].mean()} F."


if __name__ == '__main__':
    app.run(debug=True)