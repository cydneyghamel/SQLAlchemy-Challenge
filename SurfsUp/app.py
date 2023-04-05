# Import the dependencies

# Import Flask
from flask import Flask, jsonify

# Import others
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import func, create_engine
import datetime as dt
import json

#################################################
# Database Setup
#################################################

# Create engine / database connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)
session

#################################################
# Flask Setup
#################################################

# Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return(f"<center><h2>Welcome to the Climate API homepage!</h2></center><br>"
            f"<center><h3>Current Routes:</h3></center><br>"
            f"<center><a href='/api/v1.0/precipitation'>Precipitation</a></center><br>"
            f"<center><a href='/api/v1.0/stations'>Stations</a></center><br>"
            f"<center><a href='/api/v1.0/tobs'>Temperature observations of most active station</a></center><br>"
            f"<center><a href='/api/v1.0/<start>'>Temperatures for specified start date</a><start></center><br>"
            f"<center><a href='/api/v1.0/<start>/<end>'>Temperatures for specified start and end date</a></center>")

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
   # return the previous year's precipitation as a json
   # Calculate the date one year from the last date in data set.
  previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

  # Perform a query to retrieve the data and precipitation scores for the last 12 months (from most recent date in Measurement table)
  last_12_mo = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()

  # Close session
  session.close()

  # Dictionary with date as key and precipitation as value
  precipitation = {date: prcp for date, prcp in last_12_mo}

  # Convert to a json
  return jsonify(precipitation)

# Stations Route
@app.route("/api/v1.0/stations")
def stations():
   
   # Perform a query to retrieve all station names
   total_stations = session.query((Station.station)).all()

   # Close session
   session.close()

   # Use numpy.ravel to convert into one-dimensional list
   station_list = list(np.ravel(total_stations))

   # Convert to json 
   return jsonify(station_list=station_list)

# Query the dates and temperature observations of the most-active station for the previous year of data
@app.route("/api/v1.0/tobs")
def temperatures():

   # Calculate the date one year from the last date in data set.
   previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   
   # Return the previous year temperatures
   previous_year_temps = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= previous_year).all()

   # Close session
   session.close()

   # Make list of temperatures
   temperature_list = list(np.ravel(previous_year_temps))

   # Return the list of temperatures
   return jsonify(temperature_list)


# Start date and start and end date
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None): 

   # Select statement to make list
   selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

   # If no end date specified, grab temps on or after start date; otherwise, grab temps in range
   if not end:

      start_date = dt.datetime.strptime(start, "%m%d%Y")

      results = session.query(*selection).\
         filter(Measurement.date >= start_date).all()

      # Close session
      session.close()

      # Create list of temperatures
      temperature_list = list(np.ravel(results))

      # Jsonify
      return jsonify(temperature_list)
   
   start_date = dt.datetime.strptime(start, "%m%d%Y")
   end_date = dt.datetime.strptime(end, "%m%d%Y")

   results = session.query(*selection).\
      filter(Measurement.date >= start_date).\
      filter(Measurement.date <= end_date).all()

   # Close session
   session.close()

      # Create list of temperatures
   temperature_list = list(np.ravel(results))

   # Jsonify
   return jsonify(temperature_list=temperature_list)

# Define main branch/app launcher
if __name__ == "__main__":
  app.run(debug=True)

