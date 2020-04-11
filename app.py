import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:////Users/jadetao/Documents/sqlalchemy-challenge/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station= Base.classes.station

#date of one year beforelast_date of this dataset
last_date=dt.date(2017, 8, 23)
oneyear_date = last_date - dt.timedelta(days=365)

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
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"-Query the dates and temperature of the most active station since the last year "
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"-Type in a start date(YYYY-MM-DD), to get the MIN/AVG/MAX temperature since the start date<br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"-Type in a start and end Date(YYYY-MM-DD/YYYY-MM-DD), to get MIN/AVG/MAX temperature between the start and end date<br/>"
        f"/api/v1.0/<start>/<end>"
        
    )


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all sttaions
    all_stattions = []
    for station, name, lat, lng,elev in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = lng
        station_dict["elevation"] = elev
        all_stattions.append(station_dict)

    return jsonify(all_stattions)


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates with prcp"""
    # Query precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

        # Create a dictionary from the row data and append to a list of all sttaions
    prcp_dict = []
    for date, prcp in results:
        station_dict = {}
        station_dict[date] = prcp
        prcp_dict.append(station_dict)
    session.close()

    return jsonify(prcp_dict)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates with tobs"""
    # Query the last 12 months of temperature observation data for this most active tation
    topT_station = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station=='USC00519397').\
            filter(Measurement.date >= oneyear_date).\
            filter(Measurement.date < last_date).all()
         
    # Create a dictionary from the row data and append to a list of all sttaions
    topT_dict = {}
    for date, temp in topT_station:
        topT_dict["Date"] = date
        topT_dict["Temp"] = temp

    session.close()

    return jsonify(topT_dict)


@app.route("/api/v1.0/<start>")
def startDateOnly(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates with tobs"""
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
    # When given the start only, calculate TMIN, TAVG, and TMAX since the start date.
    sel=[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    results=session.query(*sel).filter(Measurement.date >= start).all()

     # Create a dictionary from the row data and append to a list of all sttaions
    temp_dict = {}
    for Tmin, Tmax, Tavg in results:
        temp_dict["Min Temp"] = Tmin
        temp_dict["Max Temp"] = Tmax
        temp_dict["Average Temp"] = Tavg

    session.close()

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def startandend(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates with tobs"""
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
    # When given the start only, calculate TMIN, TAVG, and TMAX between the start and end date.
    sel = [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]

    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date < end).all()

    #  # Create a dictionary from the row data and append to a list of all sttaions
    temp_dict = []
    for Tmin, Tmax, Tavg in results:
        station_dict = {}
        station_dict["Min Temp"] = Tmin
        station_dict["Max Temp"] = Tmax
        station_dict["Average Temp"] = Tavg
        temp_dict.append(station_dict)

    session.close()

    return jsonify(temp_dict)
    

if __name__ == '__main__':
    app.run(debug=True)
