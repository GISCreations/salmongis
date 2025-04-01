import folium
import geopandas as gpd


class Map(folium.Map):
    def __init__(self, center=(0, 0), zoom=2, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)
        folium.LayerControl().add_to(self)

    def add_basemap(self, basemap="OpenStreetMap"):
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
        folium.LayerControl().add_to(self)
