# Import the dependencies.
import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


# Define function to find previous year
def past_year():
    session = Session(engine)
    # Starting from the most recent data point in the database. 
    # Calculate the date one year from the last date in data set.
    # https://docs.python.org/3/library/datetime.html
    latest_date = session.query(func.max(Measurement.date)).first()[0]
    past_year = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)
    session.close()
    return(past_year)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/precipitation<br/>"
    )


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.name).all()
    session.close()
    all_names = list(np.ravel(stations))
    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    temp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date>=past_year()).all()
    session.close()
    past_year_tobs = []
    for date, tobs in temp_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        past_year_tobs.append(tobs_dict)

    return jsonify(past_year_tobs)


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=past_year()).all()                   
    session.close()
    precipitation_list = []
    for date, prcp in precipitation_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation_list.append(prcp_dict)

    return jsonify(precipitation_list)



if __name__ == '__main__':
    app.run(debug=True)


 