import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

app = Flask(__name__)


latestDate = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
latestDate = list(np.ravel(latestDate))[0]

latestDate = dt.datetime.strptime(latestDate, '%Y-%m-%d')
latestYear = int(dt.datetime.strftime(latestDate, '%Y'))
latestMonth = int(dt.datetime.strftime(latestDate, '%m'))
latestDay = int(dt.datetime.strftime(latestDate, '%d'))

yearBefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365)
yearBefore = dt.datetime.strftime(yearBefore, '%Y-%m-%d')




@app.route("/")
def home():
    return (f"SQLAlchemy Surf's Up <br/>"
            f"---------------------------------------------------- <br/>"
            f"API Routes <br/>"
            f"/api/v1.0/stations --------- Weather observation stations list <br/>"
            f"/api/v1.0/tobs --------------- Last year temperature data <br/>"
            f"/api/v1.0/precipitaton --------- Last year of precipitation data <br/>"
            f"/api/v1.0/startDate --------- Input a date and get back min,avg, and max temp for the date and every day after <br/>"
            f"/api/v1.0/startDate/endDate ----------- Min, max, and avg temp for a time range <br/>"
            f"------------------------------------------------- <br/>"
            f" Data available from 2010-01-01 to 2017-08-23 ")

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    tempList = []
    for r in results:
        tempDict = {r.date: r.tobs, "Station": r.station}
        tempLisr.append(tempDict)

    return jsonify(tempList)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())
    
    precipList = []
    for r in results:
        precipDict = {r.date: r.prcp, "Station": r.station}
        precipList.append(precipDict)

    return jsonify(precipList)


@app.route('/api/v1.0/<startDate>')
def start(startDate):
    x = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*x)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dateList = []                       
    for r in results:
        dateDict = {}
        dateDict["Date"] = r[0]
        dateDict["Low Temp"] = r[1]
        dateDict["Avg Temp"] = r[2]
        dateDict["High Temp"] = r[3]
        dateList.append(dateDict)
    return jsonify(dateList)

@app.route('/api/v1.0/<startDate>/<endDate>')
def dateRange(startDate, endDate):
    y = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*y)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dateList = []                       
    for r in results:
        dateDict = {}
        dateDict["Date"] = r[0]
        dateDict["Low Temp"] = r[1]
        dateDict["Avg Temp"] = r[2]
        dateDict["High Temp"] = r[3]
        dateList.append(dateDict)
    return jsonify(dateList)

if __name__ == "__main__":
    app.run(debug=True)
