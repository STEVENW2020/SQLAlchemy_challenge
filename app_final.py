# import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
# Formating from app.py in activity "10-ins_flask_with_ORM"
#################################################
# Database Setup
################################################## Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#Set date variables
session = Session(engine)

# last date in the db
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
yearago_date = dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate Page<br/> "
        f"These are the available routes:<br/>"
        f"<br/>"  
        f"The list of precipitation data with dates:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"The list of stations and names:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"The list of temperature observations occuring in the last year of the DB at the most active station (USC00519281):<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Min, max. and avg. temperatures for given start date: (please use 'yyyy-mm-dd' format):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"<br/>"
        f"Min. max. and avg. temperatures for given start and end date: (please use 'yyyy-mm-dd'/'yyyy-mm-dd' format for start and end values):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<br/>"
    )

# create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return date and precipitation info"""
    # Query precipitation and date values 
    results = session.query(Measurement.date, Measurement.prcp).all()
        
    session.close()
    
    # Create a dictionary as date the key and prcp as the value
    precipitation = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation )

#################################################################

# create stations route    
@app.route("/api/v1.0/stations")
def stations():
    # Create the session link
    session = Session(engine)
    
    """Return a JSON list of stations from the dataset."""
    # Query data to get stations list
    results = session.query(Station.station, Station.name).all()
    
    session.close()

    # Convert list of tuples into list of dictionaries for each station and name
    station_list = []
    for station, name in results:
        station_dict = {}
        station_dict["station"]= station
        station_dict["name"] = name
        station_list.append(station_dict)
    
    # jsonify the list
    return jsonify(station_list)

##################################################################

# create temperatures route
@app.route("/api/v1.0/tobs")
def tobs():
    # create session link
    session = Session(engine)
    
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # query tempratures from a year from the last data point at most active station (USC00519281). 
    station_counts = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Create top station variable from tuple
    top_station = (station_counts[0])
    top_station = (top_station[0])
    
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date >= yearago_date ).filter(Measurement.station == top_station).all()

    session.close()

    # convert list of tuples to show date and temperature values
    tobs_list = []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["date"] = date
        tobs_dict["temperature"] = tobs
        tobs_list.append(tobs_dict)

    # jsonify the list
    return jsonify(tobs_list)

######################################################################

# create temp route with start date
@app.route("/api/v1.0/min_max_avg/<start>")
def start(start):
    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # take any date and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()

    session.close()

    # Create a list to hold results
    # more streamlined code for this part
    temp_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        temp_list.append(r)

    # jsonify the result
    return jsonify(temp_list)

##################################################################
@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end dates."""

    # take start and end dates and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt)

    session.close()

    # Create a list to hold results
    temp_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["EndDate"] = end_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        temp_list.append(r)

    # jsonify the result
    return jsonify(temp_list)

##########################################################
#run the app
if __name__ == "__main__":
    app.run(debug=True)
