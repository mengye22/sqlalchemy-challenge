import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Home page with all routes print out
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitaion for the latest year in the database in json format
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Get the latest date
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    # Access the one year before the latest date in order to access the year
    latest_year = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
    latest_year = latest_year.strftime("%Y-%m-%d")
    # Get the precipitatio for the latest year
    precipitation_date = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= latest_year).\
        order_by(Measurement.date).all()
        
    session.close()
    # Print out the data in dictionary format in the list
    prcp_list = []
    for date,prcp in precipitation_date:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    # Return the list in json
    return jsonify(prcp_list)


# Print out all station id with count of stations
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    station_sum = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    session.close()

    station_list = []
    for stat_id,stat_count in station_sum:
        station_dict = {}
        station_dict["station id"] = stat_id
        station_dict["station count"] = stat_count
        station_list.append(station_dict)

    # Print out list in json format
    return jsonify(station_list)

# Print out the min,max,avg temperature for the highest number for station id
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    station_sum = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    sel = [Measurement.station,
      func.min(Measurement.tobs),
      func.max(Measurement.tobs),
      func.avg(Measurement.tobs)]
    
    temp = session.query(*sel).filter(Measurement.station == station_sum[0][0]).all()

    session.close()

    tobs_list = []
    tobs_list.append({'station id':temp[0][0],
    'TMIN':temp[0][1],
    'TMAX':temp[0][2],
    'TAVG':temp[0][3]})

    return jsonify(tobs_list)

# Return the min,avg,max temperature for input start day to the latest day on the datebase
@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)

    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    start_trip = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    trip_temp = []
    trip_temp.append({
        'start_date':start,
        'end_date':latest_date,
        'TMIN':start_trip[0][0],
        'TAVG':start_trip[0][1],
        'TMAX':start_trip[0][2]
    })
    
    return jsonify(trip_temp)

# Return the min,avg,max temperature for input start and end trip date
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)

    startEnd = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    trip_temp = []
    trip_temp.append({'start_date':start, 
    'end_date':end,
    'TMIN':startEnd[0][0],
    'TAVG':startEnd[0][1],
    'TMAX':startEnd[0][2]})
    
    return jsonify(trip_temp)


if __name__ == '__main__':
    app.run(debug=True)

