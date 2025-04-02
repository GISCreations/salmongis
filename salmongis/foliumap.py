"""
This module provides a custom map class extending folium.Map!
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

     def add_geojson(
        self,
        data,
        zoom_to_layer=True,
        hover_style=None,
        **kwargs,
    ):
        """Adds a GeoJSON layer to the map.

        Args:
            data (str or dict): The GeoJSON data. Can be a file path (str) or a dictionary.
            zoom_to_layer (bool, optional): Whether to zoom to the layer's bounds. Defaults to True.
            hover_style (dict, optional): Style to apply when hovering over features. Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments for the folium.GeoJson layer.

        Raises:
            ValueError: If the data type is invalid.
        """

        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data

        geojson = folium.GeoJson(data=geojson, **kwargs)
        geojson.add_to(self)

    def add_shp(self, data, **kwargs):
        """Adds a shapefile to the map.

        Args:
            data (str): The file path to the shapefile.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """
        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)
        
    def add_gdf(self, gdf, **kwargs):
        """Adds a GeoDataFrame to the map.

        Args:
            gdf (geopandas.GeoDataFrame): The GeoDataFrame to add.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    
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
        folium.TileLayer(
            tiles=basemaps.get(basemap, basemaps["OpenStreetMap"]), attr=basemap
        ).add_to(self.map)

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
