# import libraries
# import logging
from flask import Flask, send_file, render_template, jsonify, request

import math
import pandas as pd
import xarray as xr

from datashader.utils import lnglat_to_meters

CURRENT_VARIABLE = "TS"
DATA = xr.open_dataset("static/data/TS_reproject.nc")
DATA_SLICE = ""

def flatten_ds(year, forcing):
    global DATA
    global DATA_SLICE
    DATA_SLICE = DATA.sel(time=int(year), forcing_type=forcing)
    return

app = Flask(__name__)

@app.route("/")
def index(): 
    global DATA
    DATA = xr.open_dataset("static/data/TS_reproject.nc")
    flatten_ds("2023", "cmip6")
    return render_template('index.html')

@app.route("/dataset/<variable>")
def set_dataset(variable):
    global DATA
    global CURRENT_VARIABLE
    CURRENT_VARIABLE = variable
    DATA = xr.open_dataset("static/data/" + variable + "_reproject.nc")
    return '', 204

@app.route("/dims/<year>/<forcing>")
def flatten_dims(year, forcing):
    global DATA_SLICE
    flatten_ds(year, forcing)
    return '', 204

@app.route('/tiles/<ne_lng>/<ne_lat>/<sw_lng>/<sw_lat>')
def get_tile(ne_lng, ne_lat, sw_lng, sw_lat):
    global DATA_SLICE

    ne_lng = float(ne_lng)
    ne_lat = float(ne_lat)
    sw_lng = float(sw_lng)
    sw_lat = float(sw_lat)

    xright, yright = lnglat_to_meters(ne_lng, ne_lat)
    xleft, yleft = lnglat_to_meters(sw_lng, sw_lat)

    xcondition = "x >= {xleft} and x <= {xright}".format(xleft=xleft, xright=xright)
    ycondition = "y <= {yright} and y >= {yleft}".format(yleft=yleft, yright=yright)
    frame = DATA_SLICE.query(x=xcondition, y=ycondition)
    cornerpoints = [xleft, yleft, xright, yright]

    json_data = {
        'data': frame.to_dataframe().to_json(orient='table'),
        'cornerpoints': cornerpoints,
        'colorlim': [float(DATA[CURRENT_VARIABLE].min()), float(DATA[CURRENT_VARIABLE].max())]
    }
    return jsonify(json_data)
    
@app.route('/time-series/<lon>/<lat>')
def get_time_series(lon, lat):
    longitude = float(lon)
    latitude = float(lat)

    df_slice = DATA[CURRENT_VARIABLE].sel(x=longitude, y=latitude, method="nearest")
    df_slice = df_slice.to_dataframe().reset_index()[['time', CURRENT_VARIABLE]]

    # convert the DataFrame to JSON
    json_data = df_slice.to_json(orient='records')
    
    # send the JSON response
    return jsonify(json_data)

if __name__ == '__main__':
   app.run(debug=True)