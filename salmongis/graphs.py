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

        # Create checkboxes for each option
        checkboxes = [widgets.Checkbox(value=False, description=key) for key in options.keys()]
        checkbox_container = widgets.VBox(checkboxes)

        button = widgets.Button(
            icon="times",
        )
        button.layout = widgets.Layout(width="38px", height="38px")

        hbox = widgets.HBox([toggle, checkbox_container, button])

        def on_toggle_change(change):
            if change["new"]:
                hbox.children = [toggle, checkbox_container, button]
            else:
                hbox.children = [toggle]

        toggle.observe(on_toggle_change, names="value")

        def on_button_click(b):
            hbox.close()
            toggle.close()
            checkbox_container.close()
            button.close()

        button.on_click(on_button_click)

        # Dictionary to keep track of added overlays
        overlays = {}

        def on_checkbox_change(change):
            for checkbox in checkboxes:
                image_name = checkbox.description
                if checkbox.value:  # If the checkbox is checked
                    if image_name not in overlays:  # Add the overlay only if not already added
                        image_url, bounds = options[image_name]
                        
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
                        
                        # Add the overlay to the map and store it in the dictionary
                        self.add(overlay)
                        overlays[image_name] = overlay
                else:  # If the checkbox is unchecked
                    if image_name in overlays:  # Remove the overlay if it exists
                        self.remove(overlays[image_name])
                        del overlays[image_name]

        for checkbox in checkboxes:
            checkbox.observe(on_checkbox_change, names="value")

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
    
    def add_image_gui_with_sliders(self, options=None, position="topright"):
        """
        Adds a GUI for selecting and displaying images on the map with interactivity,
        including sliders to adjust the bounds of the selected image.

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

        # Create a dropdown menu for selecting an image
        dropdown = widgets.Dropdown(
            options=["Select an image"] + list(options.keys()),
            value="Select an image",
            description="Image:",
        )

        # Create sliders for adjusting bounds
        lat_min_slider = widgets.FloatSlider(
            value=0, min=-90, max=90, step=0.1, description="Lat Min:"
        )
        lon_min_slider = widgets.FloatSlider(
            value=0, min=-180, max=180, step=0.1, description="Lon Min:"
        )
        lat_max_slider = widgets.FloatSlider(
            value=0, min=-90, max=90, step=0.1, description="Lat Max:"
        )
        lon_max_slider = widgets.FloatSlider(
            value=0, min=-180, max=180, step=0.1, description="Lon Max:"
        )
        sliders = widgets.VBox([lat_min_slider, lon_min_slider, lat_max_slider, lon_max_slider])

        # Dictionary to keep track of the currently displayed overlay
        current_overlay = {"overlay": None}

        def on_dropdown_change(change):
            selected_image = change["new"]
            if selected_image == "Select an image":
                # Remove the current overlay if no image is selected
                if current_overlay["overlay"]:
                    self.remove(current_overlay["overlay"])
                    current_overlay["overlay"] = None
            else:
                # Remove the previous overlay
                if current_overlay["overlay"]:
                    self.remove(current_overlay["overlay"])

                # Get the selected image's URL and bounds
                image_url, bounds = options[selected_image]
                lat_min_slider.value, lon_min_slider.value = bounds[0]
                lat_max_slider.value, lon_max_slider.value = bounds[1]

                # Add the new image overlay
                overlay = ipyleaflet.ImageOverlay(url=image_url, bounds=bounds)
                self.add(overlay)
                current_overlay["overlay"] = overlay

        def update_bounds(change):
            if current_overlay["overlay"]:
                new_bounds = [
                    [lat_min_slider.value, lon_min_slider.value],
                    [lat_max_slider.value, lon_max_slider.value],
                ]
                current_overlay["overlay"].bounds = new_bounds

        # Observe changes in the dropdown and sliders
        dropdown.observe(on_dropdown_change, names="value")
        lat_min_slider.observe(update_bounds, names="value")
        lon_min_slider.observe(update_bounds, names="value")
        lat_max_slider.observe(update_bounds, names="value")
        lon_max_slider.observe(update_bounds, names="value")

        # Create a widget container
        vbox = widgets.VBox([dropdown, sliders])
        control = ipyleaflet.WidgetControl(widget=vbox, position=position)
        self.add(control)