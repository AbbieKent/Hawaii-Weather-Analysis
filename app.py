import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine1 = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine1, reflect=True)
# Save reference to the table
Measurement= Base.classes.measurement
Station=Base.classes.station
session=Session(engine1)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
####################################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    results=session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()
    precipit=[]
    for x in results:
        precip={}
        precip['date']=x.date
        precip['precip']=x.prcp
        precipit.append(precip)
    return jsonify(precipit)
@app.route('/api/v1.0/stations')
def station():
    active_station=session.query(Station.station, func.count(Station.station)).group_by(Station.station).\
        order_by(func.count(Station.station).desc()).all()
    stations=[]
    for x in active_station:
        station={}
        station['station']=x[0]
        station['count']=x[1]
        stations.append(station)
    return jsonify(stations)
@app.route('/api/v1.0/tobs')
def tobs():
    last_year=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for x in last_year:
        split_date=x.split('-')
    split_date
    last_year=int(split_date[0])
    last_month=int(split_date[1])
    last_day=int(split_date[2])

    query_date=dt.date(last_year, last_month, last_day)-dt.timedelta(days=365)
    low_high_avg_temp=session.query(Measurement.station, func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)). \
        order_by(func.count(Measurement.station).desc()).first()
    last_year_preci=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=query_date)
    temp_obs=session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station==low_high_avg_temp[0]).\
        filter(Measurement.date>=query_date).order_by(Measurement.date).all()
    temp_obs_list=[]
    for x in temp_obs:
        temp={}
        temp['date']=x[0]
        temp['tobs']=x[1]
        temp_obs_list.append(temp)
    return jsonify(temp_obs_list)
@app.route("/api/v1.0/<start>")
def calc_start_date(start):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX"""
    low_high_avg_temp=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    start_temp=[]
    for x in low_high_avg_temp:
        start_dict={}
        start_dict['TMIN']=x[0]
        start_dict['TMAX']=x[1]
        start_dict['TAVG']=x[2]
        start_temp.append(start_dict)
    return jsonify(start_temp)
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    start_end=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date<=end).\
        filter(Measurement.date>=start).all()
    start_end_list=[]
    for x in start_end:
        start_end_dict={}
        start_end_dict['min']=x[0]
        start_end_dict['max']=x[1]
        start_end_dict['avg']=x[2]
        start_end_list.append(start_end_dict)
    return jsonify(start_end_list)

if __name__ == "__main__":
    app.run(debug=True)

