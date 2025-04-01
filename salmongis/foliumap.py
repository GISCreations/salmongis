"""
This module provides a custom map class extending folium.Map.
"""

import folium
import geopandas as gpd

class Map(folium.Map):
    """
    A custom map class extending folium.Map.
    """

    def __init__(self, center=(0, 0), zoom=2, **kwargs):
        """
        Initializes the map with a given center and zoom level.

        Args:
            center (tuple): The initial center of the map as (latitude, longitude).
            zoom (int): The initial zoom level of the map.
            **kwargs: Additional keyword arguments for folium.Map.
        """
        super().__init__(location=center, zoom_start=zoom, **kwargs)
        folium.LayerControl().add_to(self)
    
    def add_basemap(self, basemap="OpenStreetMap"):
        """
        Adds a basemap layer to the map.

        Args:
            basemap (str): The name of the basemap to add. Options include:
                "OpenStreetMap", "Stamen Terrain", "Stamen Toner", "Stamen Watercolor".
                Defaults to "OpenStreetMap".
        """
        basemaps = {
            "OpenStreetMap": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "Stamen Terrain": "http://{s}.tile.stamen.com/terrain/{z}/{x}/{y}.png",
            "Stamen Toner": "http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png",
            "Stamen Watercolor": "http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg",
        }
        folium.TileLayer(tiles=basemaps.get(basemap, basemaps['OpenStreetMap']), attr=basemap).add_to(self.map)

    def add_vector(self, data, **kwargs):
        """
        Adds a vector layer to the map from various data formats.

        Args:
            data (str, geopandas.GeoDataFrame, or dict): The vector data to add. Can be:
                - A file path or URL to a GeoJSON or shapefile.
                - A GeoDataFrame.
                - A GeoJSON-like dictionary.
            **kwargs: Additional keyword arguments for folium.GeoJson.
        
        Raises:
            ValueError: If the data type is not supported.
        """
        import geopandas as gpd 
        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Invalid data type")
        
    def add_layer_control(self):
        """
        Adds a layer control widget to the map.

        The layer control allows users to toggle visibility of layers on the map.
        """
        folium.LayerControl().add_to(self)