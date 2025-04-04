"""
This module provides a custom map class extending folium.Map!
"""

import folium
import geopandas as gpd
from typing import Union, Tuple, Dict


class Map(folium.Map):
    """
    A custom map class extending folium.Map.
    """

    def __init__(self, center: Tuple[float, float] = (0, 0), zoom: int = 2, **kwargs) -> None:
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
        data: Union[str, Dict],
        zoom_to_layer: bool = True,
        hover_style: Dict = None,
        **kwargs,
    ) -> None:
        """Adds a GeoJSON layer to the map.

        Args:
            data (str or dict): The GeoJSON data. Can be a file path (str) or a dictionary.
            zoom_to_layer (bool, optional): Whether to zoom to the layer's bounds. Defaults to True.
            hover_style (dict, optional): Style to apply when hovering over features. Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments for the folium.GeoJson layer.

        Raises:
            ValueError: If the data type is invalid.
        """
        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data
        else:
            raise ValueError("Invalid data type")

        geojson_layer = folium.GeoJson(data=geojson, **kwargs)
        geojson_layer.add_to(self)

    def add_shp(self, data: str, **kwargs) -> None:
        """Adds a shapefile to the map.

        Args:
            data (str): The file path to the shapefile.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """
        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf: gpd.GeoDataFrame, **kwargs) -> None:
        """Adds a GeoDataFrame to the map.

        Args:
            gdf (geopandas.GeoDataFrame): The GeoDataFrame to add.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_basemap(self, basemap: str = "OpenStreetMap") -> None:
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
        ).add_to(self)

    def add_vector(self, data: Union[str, gpd.GeoDataFrame, Dict], **kwargs) -> None:
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
        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Invalid data type")

    def add_layer_control(self) -> None:
        """
        Adds a layer control widget to the map.

        The layer control allows users to toggle visibility of layers on the map.
        """
        folium.LayerControl().add_to(self)

    def add_split_map(self, left_basemap: str, right_basemap: str) -> None:
        """
        Adds a split map to the map, displaying two basemaps side by side.

        Args:
            left_basemap (str): The name of the basemap to display on the left side.
            right_basemap (str): The name of the basemap to display on the right side.

        Raises:
            ValueError: If the provided basemap names are not supported.
        """
        basemaps = {
            "OpenStreetMap": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "Stamen Terrain": "http://{s}.tile.stamen.com/terrain/{z}/{x}/{y}.png",
            "Stamen Toner": "http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png",
            "Stamen Watercolor": "http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg",
        }

        if left_basemap not in basemaps or right_basemap not in basemaps:
            raise ValueError("Invalid basemap name. Supported basemaps are: " + ", ".join(basemaps.keys()))

        left_layer = folium.TileLayer(tiles=basemaps[left_basemap], name=f"Left: {left_basemap}")
        right_layer = folium.TileLayer(tiles=basemaps[right_basemap], name=f"Right: {right_basemap}")

        left_layer.add_to(self)
        right_layer.add_to(self) 
