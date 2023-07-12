# d3-CESM-tiling
Using d3.js with a Flask server to render map tiles from a NetCDF file completely on the client side.

Instructions to view:
- Clone repository and navigate to it in terminal
- Download datasets from [this Google Drive link](https://drive.google.com/drive/folders/1GnIz4b8MIDNfr5Sc8TaXKRm-2G4UOs80?usp=sharing), extract files directly into `static/data`
- Ensure flask is installed and datashader.utils, xarray, and pandas are accessible in the directory (or virtual environment, if you are using one) as well
- Use command `flask run` and navigate to the provided URL in a browser

See [this Figma schematic](https://www.figma.com/file/0uEs0MQVAUsDu5Yj47vmQo/Map-Application-Structure?type=whiteboard&node-id=0%3A1&t=6R5mLckYIckqQT4s-1) for an overview of the application's structure.
