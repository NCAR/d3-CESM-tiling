# import libraries
from flask import Flask, send_file, render_template, jsonify, request

import math
import pandas as pd
import xarray as xr

from datashader.utils import lnglat_to_meters

data = xr.open_dataset("static/data/TS2023_reproject.nc")
time_data = xr.open_dataset("static/data/TS_annual_reproject.nc")

# find min/max data values to set global colorbar
min_val = float(data['TS'].min())
max_val = float(data['TS'].max())

# extract dimensions
lon_array = data['x']
lat_array = data['y']
data_array = data['TS']
time_data_array = time_data['TS']

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html', colormin = min_val, colormax = max_val)

@app.route('/tiles/<ne_lng>/<ne_lat>/<sw_lng>/<sw_lat>/<year>/<forcing>')
def get_tile(ne_lng, ne_lat, sw_lng, sw_lat, year, forcing):
    ne_lng = float(ne_lng)
    ne_lat = float(ne_lat)
    sw_lng = float(sw_lng)
    sw_lat = float(sw_lat)
    year = int(year)

    xright, yright = lnglat_to_meters(ne_lng, ne_lat)
    xleft, yleft = lnglat_to_meters(sw_lng, sw_lat)

    xcondition = "x >= {xleft} and x <= {xright}".format(xleft=xleft, xright=xright)
    ycondition = "y <= {yright} and y >= {yleft}".format(yleft=yleft, yright=yright)
    frame = data.query(x=xcondition, y=ycondition)
    cornerpoints = [xleft, yleft, xright, yright]

    json_data = {
        'data': frame.to_dataframe().to_json(orient='table'),
        'cornerpoints': cornerpoints
    }
    return jsonify(json_data)
    

@app.route('/time-series', methods=['POST'])
def get_time_series():
    request_data = request.get_json()
    latitude = request_data['latitude']
    longitude = request_data['longitude']

    df_slice = time_data_array.sel(x=longitude, y=latitude, method="nearest")
    df_slice = df_slice.to_dataframe().reset_index()[['year', 'TS']]

    # convert the DataFrame to JSON
    json_data = df_slice.to_json(orient='records')
    
    # send the JSON response
    return jsonify(data=json_data)

if __name__ == '__main__':
   app.run(debug=True)