import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

# db setup and error check
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False}, echo = True)

# reflect an existing db into a new model
base = automap_base()

# reflect the tables 
base.prepare(engine,reflect=True)

# Save references to each table
measurements = base.classes.measurement
stations = base.classes.station

# session link
session = Session(engine)

# Flask
app = Flask(__name__)

# Flask Routes
#List all routes that are available
@app.route("/")
def Home():

     return (
         f"/api/v1.0/precipitation<br/>"
         f"/api/v1.0/stations<br/>"
         f"/api/v1.0/temperatures<br/>"
         f"/api/v1.0/<start><br/>"
         f"/api/v1.0/<start>/<end><br/>"
     )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database
    date_last_year = session.data(measurements.date).order_by(measurements.date.desc()).first()[0]

    #find date 12 months before
    prior_year = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    data = session.data(measurements.date, measurements.prcp).\
        filter(measurements.date >= prior_year).all()

    precip_score = []
    for i, prcp in data:
        data = {}
        data['date'] = i
        data['prcp'] = prcp
        precip_score.append(data)

    return jsonify(precip_score)


@app.route("/api/v1.0/stations")
def stations():
    
    data = session.data(stations.name, stations.stations, stations.elevation).all()

    #create dictionary for JSON
    stations_list = []
    for i in data:
        row = {}
        row['name'] = i[0]
        row['stations'] = i[1]
        row['elevation'] = i[2]
        stations_list.append(row)
    return jsonify(stations_list)

@app.route("/api/v1.0/temperatures")
def temperature_temperatures():
    data = session.data(stations.name, measurements.date, measurements.temperatures).\
        filter(measurements.date >= "2017-01-01", measurements.date <= "2018-01-01").\
        all()

    #use dictionary, create json
    temps_list = []
    for i in data:
        row = {}
        row["Date"] = i[1]
        row["stations"] = i[0]
        row["Temperature"] = int(i[2])
        temps_list.append(row)

    return jsonify(temps_list)


@app.route("/api/v1.0/<start>")
def start(start=None):
    
    from_start = session.data(measurements.date, func.min(measurements.temperatures), func.avg(measurements.temperatures),
                               func.max(measurements.temperatures)).filter(measurements.date >= start).group_by(
        measurements.date).all()
    from_start_list = list(from_start)
    return jsonify(from_start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    ranges = session.data(measurements.date, func.min(measurements.temperatures), func.avg(measurements.temperatures),
                                  func.max(measurements.temperatures)).filter(measurements.date >= start).filter(
        measurements.date <= end).group_by(measurements.date).all()
    ranges_list = list(ranges)
    return jsonify(ranges_list)

if __name__ == "__main__":
    app.run(debug=False)