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

# following function from ScottSyms tileshade repo under the GNU General Public License v3.0.
# https://github.com/ScottSyms/tileshade/
def tile2mercator(xtile, ytile, zoom):
    # takes the zoom and tile path and passes back the EPSG:3857
    # coordinates of the top left of the tile.
    # From Openstreetmap
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)

    # Convert the results of the degree calulation above and convert
    # to meters for web map presentation
    mercator = lnglat_to_meters(lon_deg, lat_deg)
    return mercator

# following function adapted from ScottSyms tileshade repo under the GNU General Public License v3.0.
# https://github.com/ScottSyms/tileshade/
# changes made: snapping values to ensure continuous tiles; use of quadmesh instead of points; syntax changes to work with Flask.
def generateatile(zoom, x, y):
    # The function takes the zoom and tile path from the web request,
    # and determines the top left and bottom right coordinates of the tile.
    # This information is used to query against the dataframe.
    xleft, yleft = tile2mercator(int(x), int(y), int(zoom))
    xright, yright = tile2mercator(int(x)+1, int(y)+1, int(zoom))

    # ensuring no gaps are left between tiles due to partitioning occurring between coordinates.
    # xleft_snapped = lon_array.sel(x=xleft, method="nearest").values
    # yleft_snapped = lat_array.sel(y=yleft, method="nearest").values
    # xright_snapped = lon_array.sel(x=xright, method="nearest").values
    # yright_snapped = lat_array.sel(y=yright, method="nearest").values

    xcondition = "x >= {xleft_snapped} and x <= {xright_snapped}".format(xleft_snapped=xleft, xright_snapped=xright)
    ycondition = "y <= {yleft_snapped} and y >= {yright_snapped}".format(yleft_snapped=yleft, yright_snapped=yright)
    frame = data.query(x=xcondition, y=ycondition)
    cornerpoints = [xleft, yleft, xright, yright]
    return [cornerpoints, frame.to_dataframe()]

   
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html', colormin = min_val, colormax = max_val)

@app.route("/tiles/<int:zoom>/<int:x>/<int:y>")
def tile(x, y, zoom):
    results = generateatile(zoom, x, y)

    coordinates = results[0]
    dataresults = results[1].drop(columns=['spatial_ref'])
    
    data = {
        'data': dataresults.to_json(orient='table'),
        'cornerpoints': coordinates
    }

    # # convert the DataFrame to JSON
    # json_data = dataresults.to_json(orient='table')

    # # send the JSON response
    # return jsonify(data=json_data)
    return jsonify(data)


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