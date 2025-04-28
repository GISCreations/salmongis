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
    

    def add_image_gui(self, options=None, position="topright"):
        """
        Adds a GUI for selecting and displaying images on the map with interactivity.

        Args:
            options (dict, optional): A dictionary where keys are image names (strings)
                and values are tuples containing the image URL (str) and bounds (list).
                Defaults to a sample list of images.
            position (str, optional): The position of the GUI widget on the map.
                Defaults to "topright".

        Returns:
            None
        """
        if options is None:
            options = {
                "Sample Image 1": (
                    "https://example.com/sample1.png",
                    [[-90, -180], [90, 180]],
                ),
                "Sample Image 2": (
                    "https://example.com/sample2.png",
                    [[10, -50], [20, 50]],
                ),
            }

        toggle = widgets.ToggleButton(
            value=True,
            button_style="",
            tooltip="Click to toggle image GUI",
            icon="image",
        )
        toggle.layout = widgets.Layout(width="38px", height="38px")

        dropdown = widgets.Dropdown(
            options=list(options.keys()),
            value=list(options.keys())[0],
            description="Images:",
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
                image_url, bounds = options[change["new"]]
                
                # Scale down the bounds to make the image smaller
                lat_min, lon_min = bounds[0]
                lat_max, lon_max = bounds[1]
                scale_factor = 0.5  # Adjust this value to control the size of the image
                lat_center = (lat_min + lat_max) / 2
                lon_center = (lon_min + lon_max) / 2
                lat_range = (lat_max - lat_min) * scale_factor / 2
                lon_range = (lon_max - lon_min) * scale_factor / 2
                scaled_bounds = [
                    [lat_center - lat_range, lon_center - lon_range],
                    [lat_center + lat_range, lon_center + lon_range],
                ]
                
                # Add the image overlay
                overlay = ipyleaflet.ImageOverlay(url=image_url, bounds=scaled_bounds)
                
                
                # Add the overlay to the map
                self.add(overlay)

        dropdown.observe(on_dropdown_change, names="value")

        control = ipyleaflet.WidgetControl(widget=hbox, position=position)
        self.add(control)
    
    def add_image(self, image_url, bounds):
        """
        Adds an image overlay to the map and makes it draggable.

        Args:
            image_url (str): The URL of the image to be added.
            bounds (list): The geographical bounds for the image overlay.
        """
        # Create the image overlay
        image_overlay = ipyleaflet.ImageOverlay(
            url=image_url,
            bounds=bounds,
            opacity=0.7,
            name="Image Overlay",
        )
        self.add(image_overlay)