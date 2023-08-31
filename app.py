from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import pandas as pd

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
session = Session(bind=engine)
Base = automap_base()
Base.prepare(autoload_with=engine)
station = Base.classes.station
measurement = Base.classes.measurement
session = Session(bind=engine)
most_recent_date = session.query(func.max(measurement.date)).scalar()
one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Initialise Flask app
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    return(
        "Hello!<br/>"
        "Available routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
       "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )
# /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    date_prcp = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).\
        filter(measurement.prcp.isnot(None)).all() 
    precipitation_dict = {date: prcp for date, prcp in date_prcp}

    return jsonify(precipitation_dict)

#/api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(station.station, station.name).all()
    stations = [{"Station": station, "Name": name} for station, name in station_list]
    return jsonify(stations)

# /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    last_year_temp = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == "USC00519281", measurement.date >= one_year_ago).all()
    temp_data = [{"date": date, "tobs": tobs} for date, tobs in last_year_temp]
    return jsonify(temp_data)

#/api/v1.0/<start>
@app.route("/api/v1.0/<start>")
def temperature_start(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    # Calculate temperature statistics from start_date to the end of the dataset
    temperature_stats = session.query(
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs)
    ).filter(measurement.date >= start_date).all()

    stats = {
        "start_date": start_date.date(),
        "min_temperature": temperature_stats[0][0],
        "avg_temperature": temperature_stats[0][1],
        "max_temperature": temperature_stats[0][2]
    }

    return jsonify(stats)

#/api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    # Calculate temperature statistics from start_date to end_date (inclusive)
    temperature_stats = session.query(
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs)
    ).filter(measurement.date >= start_date, measurement.date <= end_date).all()

    stats = {
        "start_date": start_date.date(),
        "end_date": end_date.date(),
        "min_temperature": temperature_stats[0][0],
        "avg_temperature": temperature_stats[0][1],
        "max_temperature": temperature_stats[0][2]
    }

    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True)
