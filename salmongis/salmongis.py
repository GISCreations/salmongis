"""Main module."""

import ipyleaflet
import geopandas as gpd
from ipyleaflet import GeoJSON
import ipywidgets as widgets


class Map(ipyleaflet.Map):
    """A custom map class extending ipyleaflet.Map."""

    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        """
        Initializes the map with a given center, zoom level, and height.

        Args:
            center (list): The initial center of the map as [latitude, longitude].
            zoom (int): The initial zoom level of the map.
            height (str): The height of the map in pixels or percentage.
            **kwargs: Additional keyword arguments for ipyleaflet.Map.
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap="OpenTopoMap"):
        """
        Adds a basemap layer to the map.

        Args:
            basemap (str): The name of the basemap to add. Must be a valid basemap
                available in ipyleaflet.basemaps.
        """
        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add_layer(layer)

    def add_layer_control(self):
        """
        Adds a layer control widget to the map.

        The layer control allows users to toggle visibility of layers on the map.
        """
        control = ipyleaflet.LayersControl(position="topright")
        self.add(control)

    def add_google_map(self, map_type="ROADMAP"):
        """
        Adds a Google Maps layer to the map.

        Args:
            map_type (str): The type of Google Map to add. Options are:
                "ROADMAP", "SATELLITE", "TERRAIN", "HYBRID".
        """
        map_types = {
            "ROADMAP": "m",
            "SATELLITE": "s",
            "TERRAIN": "p",
            "HYBRID": "y",
        }

        map_type = map_types[map_type]

        url = (
            f"https://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}"
        )
        layer = ipyleaflet.TileLayer(ur1=url, name="Google Map")
        self.add(layer)

    def add_vector(self, data, **kwargs):
        """
        Adds a vector layer to the map from a GeoJSON or file.

        Args:
            data (str): The path or URL to the vector data (e.g., GeoJSON file).
            **kwargs: Additional keyword arguments for ipyleaflet.GeoJSON.
        """
        import geopandas as gpd

        # Load the data into a GeoDataFrame
        gdf = gpd.read_file(data)

        # Reproject to EPSG:4326
        gdf = gdf.to_crs(epsg=4326)

        # Convert to GeoJSON
        geojson = gdf.__geo_interface__

        # Add the GeoJSON layer to the map
        self.add_layer(ipyleaflet.GeoJSON(data=geojson, **kwargs))
    
    def add_raster(self, filepath, **kwargs):
        from localtileserver import TileClient, get_leaflet_tile_layer 
        client = TileClient(filepath)
        tile_layer = get_leaflet_tile_layer(client, **kwargs)
        self = Map(zoom=3)
        self.add(tile_layer)
        self.center = client.center()
        self.zoom = client.default_zoom
    
    def add_image (self, image, bounds=None, **kwargs):
        """Adds an image to the map.
        Args: image (str): The file path to the image.
            
        bounds (list, optional): The bounds for the image. Defaults to None.
        **kwargs: Additional keyword arguments for the ipyleaflet. ImageOverlay layer.
        """
        if bounds is None: 
            bounds = [[-90, -180] [90,1801]]
        overlay = ipyleaflet.ImageOverlay(url=image, bounds=bounds, **kwargs)
        self.add(overlay)

    def add_video(self, video, bounds = None, **kwargs):
        """Adds a video to the map.
        Args: video (str): The file path to the video.
            
        bounds (list, optional): The bounds for the video. Defaults to None.
        **kwargs: Additional keyword arguments for the ipyleaflet. VideoOverlay layer.
        """
        if bounds is None: 
            bounds = [[-90, -180] [90, 180]]
        overlay = ipyleaflet.VideoOverlay(url=video, bounds=bounds, **kwargs)
        self.add(overlay)

    def add_wms_layer(self, url, layers, format = "image/png", transparent = True, **kwargs):
        """
        Adds a WMS layer to the map.

        Args:
            url (str): The WMS service URL.
            layers (str): The layers to be displayed.
            **kwargs: Additional keyword arguments for ipyleaflet.WMSLayer.
        """
        wms_layer = ipyleaflet.WMSLayer(url=url, layers=layers, format = format, transparent = transparent,  **kwargs)
        self.add(wms_layer)
    
    def add_basemap_gui(self, options=None, position="topright"):
        """
        Adds a graphical user interface (GUI) for selecting and switching basemaps.

        This function creates a toggle button, dropdown menu, and close button
        to allow users to interactively select a basemap from a predefined list
        and apply it to the map.

        Args:
            options (list, optional): A list of basemap names (strings) to display
                in the dropdown menu. Defaults to a list of common basemaps:
                ["OpenStreetMap.Mapnik", "OpenTopoMap", "Esri.WorldImagery", "CartoDB.DarkMatter"].
            position (str, optional): The position of the GUI widget on the map.
                Defaults to "topright". Valid positions include "topleft", "topright",
                "bottomleft", and "bottomright".

        Returns:
            None
        """
        if options is None:
            options = [
                "OpenStreetMap.Mapnik",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "CartoDB.DarkMatter",
            ]

        toggle = widgets.ToggleButton(
            value=True,
            button_style="",
            tooltip="Click me",
            icon="map",
        )
        toggle.layout = widgets.Layout(width="38px", height="38px")

        dropdown = widgets.Dropdown(
            options=options,
            value=options[0],
            description="Basemap:",
            style={"description_width": "initial"},
        )
        dropdown.layout = widgets.Layout(width="250px", height="38px")

        button = widgets.Button(
            icon="times",
        )
        button.layout = widgets.Layout(width="38px", height="38px")

        hbox = widgets.HBox([toggle, dropdown, button])

        def on_toggle_change(change):
            if change["new"]:
                hbox.children = [toggle, dropdown, button]
            else:
                hbox.children = [toggle]

        toggle.observe(on_toggle_change, names="value")

        def on_button_click(b):
            hbox.close()
            toggle.close()
            dropdown.close()
            button.close()

        button.on_click(on_button_click)

        def on_dropdown_change(change):
            if change["new"]:
                self.layers = self.layers[:-2]
                self.add_basemap(change["new"])

        dropdown.observe(on_dropdown_change, names="value")

        control = ipyleaflet.WidgetControl(widget=hbox, position=position)
        self.add(control)