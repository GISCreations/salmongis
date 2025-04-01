"""Main module."""

import ipyleaflet
import geopandas as gpd
from ipyleaflet import GeoJSON

class Map(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height = "600px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap = "OpenTopoMap"):
        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet. TileLayer(url=url, name=basemap)
        self.add_layer(layer)

    def add_layer_control(self):
        control = ipyleaflet.LayersControl(position="topright")
        self.add(control)

    def add_google_map(self, map_type = "ROADMAP"):

        map_types = {
            "ROADMAP": "m",
            "SATELLITE": "s",
            "TERRAIN": "p", 
            "HYBRID": "y",
        }

        map_type = map_types[map_type]

        url = f"https://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}"
        layer = ipyleaflet.TileLayer(ur1=url, name="Google Map")
        self.add(layer)
    
    def add_vector(self, data, **kwargs):
        import geopandas as gpd

        # Load the data into a GeoDataFrame
        gdf = gpd.read_file(data)

        # Reproject to EPSG:4326
        gdf = gdf.to_crs(epsg=4326)

        # Convert to GeoJSON
        geojson = gdf.__geo_interface__

        # Add the GeoJSON layer to the map
        self.add_layer(ipyleaflet.GeoJSON(data=geojson, **kwargs))

