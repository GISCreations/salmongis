"""
This module provides a custom `Map` class that extends `ipyleaflet.Map` to include additional functionality
such as adding images, videos, COGs, GeoJSON layers, and a collapsible menu.
"""

import ipyleaflet
from ipyleaflet import GeoJSON
import ipywidgets as widgets
from localtileserver import TileClient, get_leaflet_tile_layer
import ipyfilechooser as filechooser
import time
import requests


class Map(ipyleaflet.Map):
    """A custom map class extending `ipyleaflet.Map`."""

    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        """
        Initializes the map with a given center, zoom level, and height.

        Args:
            center (list): The initial center of the map as [latitude, longitude].
            zoom (int): The initial zoom level of the map.
            height (str): The height of the map in pixels or percentage.
            **kwargs: Additional keyword arguments for `ipyleaflet.Map`.
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_combined_ui(self, options=None, video_options=None, video_bounds=None, cog_options=None, geojson_options=None, title="Map Title", position="topleft", font_size="16px", font_color="black"):
        """
        Combines all functionalities (image GUI, video overlay, title, COG, GeoJSON, and basemap selector) into one unified UI with a menu.

        Args:
            options (dict, optional): A dictionary for image options where keys are image names (strings)
                and values are tuples containing the image URL (str) and bounds (list).
            video_options (dict, optional): A dictionary for video options where keys are video names (strings)
                and values are file paths or URLs to the video files.
            video_bounds (list, optional): The geographical bounds for the video overlay as [[lat_min, lon_min], [lat_max, lon_max]].
            cog_options (dict, optional): A dictionary for COG options where keys are COG names (strings)
                and values are URLs to the COG files.
            geojson_options (dict, optional): A dictionary for GeoJSON options where keys are GeoJSON names (strings)
                and values are URLs to the GeoJSON files.
            title (str, optional): The initial text of the title to be displayed on the map. Defaults to "Map Title".
            position (str, optional): The initial position of the title on the map. Defaults to "topleft".
            font_size (str, optional): The initial font size of the title. Defaults to "16px".
            font_color (str, optional): The initial font color of the title. Defaults to "black".

        Returns:
            None
        """
        # Default options
        options = options or {
            "Sample Image 1": ("https://example.com/sample1.png", [[-90, -180], [90, 180]]),
            "Sample Image 2": ("https://example.com/sample2.png", [[10, -50], [20, 50]]),
        }
        video_options = video_options or {
            "Sample Video 1": "https://example.com/sample_video1.mp4",
            "Sample Video 2": "https://example.com/sample_video2.mp4",
        }
        video_bounds = video_bounds or [[-10, -20], [10, 20]]
        cog_options = cog_options or {
            "Select a COG": None,
            "COG 1": "https://example.com/cog1.tif",
            "COG 2": "https://example.com/cog2.tif",
        }
        geojson_options = geojson_options or {
            "Select a GeoJSON": None,
            "World Countries": "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json",
            "World Cities": "https://github.com/opengeos/datasets/releases/download/world/world_cities.geojson",
        }

        # Widgets for image selection using ipyfilechooser
        image_chooser = filechooser.FileChooser()
        image_chooser.title = "Select an image file"
        image_chooser.filter_pattern = ["*.png", "*.jpg", "*.jpeg"]  # Restrict file types
        image_chooser.use_dir_icons = True

        lat_min_slider = widgets.FloatSlider(value=0, min=-90, max=90, step=0.1, description="Lat Min:")
        lon_min_slider = widgets.FloatSlider(value=0, min=-180, max=180, step=0.1, description="Lon Min:")
        lat_max_slider = widgets.FloatSlider(value=0, min=-90, max=90, step=0.1, description="Lat Max:")
        lon_max_slider = widgets.FloatSlider(value=0, min=-180, max=180, step=0.1, description="Lon Max:")
        image_opacity_slider = widgets.FloatSlider(value=0.8, min=0, max=1, step=0.1, description="Opacity:")
        image_sliders = widgets.VBox([lat_min_slider, lon_min_slider, lat_max_slider, lon_max_slider, image_opacity_slider])

        # Widgets for video overlay
        video_dropdown = widgets.Dropdown(
            options=["Select a video"] + list(video_options.keys()),
            value="Select a video",
            description="Video:",
        )
        video_opacity_slider = widgets.FloatSlider(value=0.7, min=0, max=1, step=0.1, description="Opacity:")

        # Widgets for COG selection using ipyfilechooser
        cog_chooser = filechooser.FileChooser()
        cog_chooser.title = "Select a COG file"
        cog_chooser.filter_pattern = ["*.tif", "*.tiff"]  # Restrict file types to TIFF
        cog_chooser.use_dir_icons = True

        cog_opacity_slider = widgets.FloatSlider(value=0.8, min=0, max=1, step=0.1, description="Opacity:")

        # Function to add or update the COG layer
        def add_cog_layer(change):
            """
            Adds or updates the COG layer on the map based on the selected file and opacity.

            Args:
                change: The change event triggered by the FileChooser or opacity slider.

            Returns:
                None
            """
            selected_file = cog_chooser.selected
            if not selected_file:
                # Remove the current COG layer if no file is selected
                if current_overlay["cog"]:
                    self.remove(current_overlay["cog"])
                    current_overlay["cog"] = None
            else:
                # Remove the existing COG layer if it exists
                if current_overlay["cog"]:
                    self.remove(current_overlay["cog"])
                try:
                    # Add the new COG layer
                    client = TileClient(selected_file)
                    cog_layer = get_leaflet_tile_layer(client, opacity=cog_opacity_slider.value)
                    self.add(cog_layer)
                    current_overlay["cog"] = cog_layer

                    # Zoom to the bounds of the COG layer
                    self.fit_bounds(client.bounds)
                except Exception as e:
                    print(f"Error adding COG layer: {e}")

        # Observe changes in the FileChooser
        cog_chooser.register_callback(add_cog_layer)

        # Observe changes in the opacity slider
        cog_opacity_slider.observe(add_cog_layer, names="value")

        # Create the COG control panel
        cog_control_panel = widgets.VBox([cog_chooser, cog_opacity_slider])
        cog_control = ipyleaflet.WidgetControl(widget=cog_control_panel, position="topright")


        # Widgets for GeoJSON selection using ipyfilechooser
        geojson_chooser = filechooser.FileChooser()
        geojson_chooser.title = "Select a GeoJSON file"
        geojson_chooser.filter_pattern = ["*.geojson", "*.json"]  # Restrict file types to GeoJSON/JSON
        geojson_chooser.use_dir_icons = True

        # Function to add or update the GeoJSON layer
        def update_geojson(change):
            """
            Adds or updates the GeoJSON layer on the map based on the selected file.

            Args:
                change: The change event triggered by the FileChooser.

            Returns:
                None
            """
            selected_file = geojson_chooser.selected
            if not selected_file:
                # Remove the current GeoJSON layer if no file is selected
                if current_overlay["geojson"]:
                    self.remove(current_overlay["geojson"])
                    current_overlay["geojson"] = None
            else:
                # Remove the existing GeoJSON layer if it exists
                if current_overlay["geojson"]:
                    self.remove(current_overlay["geojson"])
                try:
                    # Load the GeoJSON data from the selected file
                    with open(selected_file, "r") as f:
                        geojson_data = f.read()
                    geojson_layer = GeoJSON(data=geojson_data)
                    self.add(geojson_layer)
                    current_overlay["geojson"] = geojson_layer

                    # Zoom to the bounds of the GeoJSON layer
                    self.fit_bounds(geojson_layer.bounds)
                except Exception as e:
                    print(f"Error loading GeoJSON: {e}")

        # Observe changes in the FileChooser
        geojson_chooser.register_callback(update_geojson)

        # Create the GeoJSON control panel
        geojson_control_panel = widgets.VBox([geojson_chooser])  # Use geojson_chooser here
        geojson_control = ipyleaflet.WidgetControl(widget=geojson_control_panel, position="topright")

        # Add the GeoJSON control to the map

        # Widgets for title
        title_input = widgets.Text(value=title, description="Title:")
        font_size_slider = widgets.IntSlider(value=int(font_size[:-2]), min=10, max=50, step=1, description="Font Size:")
        font_color_picker = widgets.ColorPicker(value=font_color, description="Font Color:")
        position_dropdown = widgets.Dropdown(
            options=["topcenter", "topright", "topleft", "bottomright", "bottomleft"],
            value=position,
            description="Position:",
        )

        # Initialize the title widget
        title_widget = widgets.HTML(
            value=f"<div style='color:{font_color}; font-size:{font_size}; text-align:center; background-color: transparent;'>{title}</div>"
        )
        self.title_control = ipyleaflet.WidgetControl(widget=title_widget, position=position)
        self.add_control(self.title_control)

        # Dictionary to keep track of overlays
        current_overlay = {"image": None, "video": None, "cog": None, "geojson": None}

        # Functions for updating the map
        def update_image(change):
            """
            Updates the image overlay on the map based on the selected file and bounds.

            Args:
                change: The change event triggered by the FileChooser.

            Returns:
                None
            """
            selected_file = image_chooser.selected
            if not selected_file:
                # Remove the current image overlay if no file is selected
                if current_overlay["image"]:
                    self.remove(current_overlay["image"])
                    current_overlay["image"] = None
            else:
                # Remove the existing image overlay if it exists
                if current_overlay["image"]:
                    self.remove(current_overlay["image"])

                # Use bounds from sliders
                bounds = [
                    [lat_min_slider.value, lon_min_slider.value],
                    [lat_max_slider.value, lon_max_slider.value],
                ]
                try:
                    # Add the new image overlay
                    overlay = ipyleaflet.ImageOverlay(
                        url=selected_file,
                        bounds=bounds,
                        opacity=image_opacity_slider.value,
                    )
                    self.add(overlay)
                    current_overlay["image"] = overlay
                except Exception as e:
                    print(f"Error adding image overlay: {e}")

        # Observe changes in the FileChooser
        image_chooser.register_callback(update_image)

        def update_image_bounds(change):
            if current_overlay["image"]:
                new_bounds = [
                    [lat_min_slider.value, lon_min_slider.value],
                    [lat_max_slider.value, lon_max_slider.value],
                ]
                current_overlay["image"].bounds = new_bounds

        # Function to add or update the COG layer
        def add_cog_layer(change):
            """
            Adds or updates the COG layer on the map based on the selected file and opacity.

            Args:
                change: The change event triggered by the FileChooser or opacity slider.

            Returns:
                None
            """
            selected_file = cog_chooser.selected
            if not selected_file:
                # Remove the current COG layer if no file is selected
                if current_overlay["cog"]:
                    self.remove(current_overlay["cog"])
                    current_overlay["cog"] = None
            else:
                # Remove the existing COG layer if it exists
                if current_overlay["cog"]:
                    self.remove(current_overlay["cog"])
                try:
                    # Add the new COG layer
                    client = TileClient(selected_file)
                    cog_layer = get_leaflet_tile_layer(client, opacity=cog_opacity_slider.value)
                    self.add(cog_layer)
                    current_overlay["cog"] = cog_layer

                    # Zoom to the bounds of the COG layer
                    self.fit_bounds(client.bounds)
                except Exception as e:
                    print(f"Error adding COG layer: {e}")

        # Observe changes in the FileChooser
        cog_chooser.register_callback(add_cog_layer)

        # Observe changes in the opacity slider
        cog_opacity_slider.observe(add_cog_layer, names="value")

        def update_geojson(change):
            # Remove the current GeoJSON layer if it exists
            if current_overlay["geojson"]:
                self.remove(current_overlay["geojson"])
                current_overlay["geojson"] = None

            # Add the new GeoJSON layer
            geojson_url = geojson_chooser.selected
            if geojson_url:
                try:
                    response = requests.get(geojson_url)
                    response.raise_for_status()
                    geojson_layer = GeoJSON(data=response.json())
                    self.add(geojson_layer)
                    current_overlay["geojson"] = geojson_layer

                    # Zoom to the bounds of the GeoJSON layer
                    self.fit_bounds(geojson_layer.bounds)
                except Exception as e:
                    print(f"Error loading GeoJSON: {e}")

        def update_title(change):
            title_widget.value = (
                f"<div style='color:{font_color_picker.value}; font-size:{font_size_slider.value}px; text-align:center;'>"
                f"{title_input.value}</div>"
            )
            if self.title_control in self.controls:
                self.remove_control(self.title_control)
            self.title_control = ipyleaflet.WidgetControl(widget=title_widget, position=position_dropdown.value)
            self.add_control(self.title_control)

        # Observe changes in widgets
        image_chooser.observe(update_image, names="value")
        lat_min_slider.observe(update_image_bounds, names="value")
        lon_min_slider.observe(update_image_bounds, names="value")
        lat_max_slider.observe(update_image_bounds, names="value")
        lon_max_slider.observe(update_image_bounds, names="value")
        cog_chooser.observe(add_cog_layer, names="value")
        cog_opacity_slider.observe(add_cog_layer, names="value")
        geojson_chooser.observe(update_geojson, names="value")  # Use geojson_chooser here
        title_input.observe(update_title, names="value")
        font_size_slider.observe(update_title, names="value")
        font_color_picker.observe(update_title, names="value")
        position_dropdown.observe(update_title, names="value")

        # Create control panels
        image_control_panel = widgets.VBox([image_chooser, image_sliders])
        video_control_panel = widgets.VBox([video_dropdown, video_opacity_slider])
        cog_control_panel = widgets.VBox([cog_chooser, cog_opacity_slider])
        geojson_control_panel = widgets.VBox([geojson_chooser])  # Use geojson_chooser here
        title_control_panel = widgets.VBox([title_input, font_size_slider, font_color_picker, position_dropdown])

        # Create WidgetControl objects
        image_control = ipyleaflet.WidgetControl(widget=image_control_panel, position="topright")
        video_control = ipyleaflet.WidgetControl(widget=video_control_panel, position="topright")
        cog_control = ipyleaflet.WidgetControl(widget=cog_control_panel, position="topright")
        geojson_control = ipyleaflet.WidgetControl(widget=geojson_control_panel, position="topright")
        title_control_panel_control = ipyleaflet.WidgetControl(widget=title_control_panel, position="topright")

        # Default basemaps
        basemaps = [
            "OpenStreetMap.Mapnik",
            "OpenTopoMap",
            "CartoDB.Positron",
            "CartoDB.DarkMatter",
        ]

        # Dropdown widget for selecting a basemap
        basemap_dropdown = widgets.Dropdown(
            options=basemaps,
            value="OpenStreetMap.Mapnik",
            description="Basemap:",
            layout=widgets.Layout(width="225px"),
        )

        # Button to apply the selected basemap
        apply_button = widgets.Button(
            description="Apply",
            button_style="success",
            tooltip="Apply the selected basemap",
            icon="map",
            layout=widgets.Layout(width="75px"),
        )

        # Function to update the basemap
        def update_basemap(b):
            # Remove all existing tile layers
            for layer in self.layers:
                if isinstance(layer, ipyleaflet.TileLayer):
                    self.remove_layer(layer)

            # Add the selected basemap
            basemap_name = basemap_dropdown.value
            basemap = eval(f"ipyleaflet.basemaps.{basemap_name}")
            tile_layer = ipyleaflet.TileLayer(url=basemap.build_url(), name=basemap_name)
            self.add_layer(tile_layer)

        # Attach the update function to the button
        apply_button.on_click(update_basemap)

        # Create a control panel for the basemap selector
        basemap_control_panel = widgets.VBox([basemap_dropdown, apply_button])
        basemap_control = ipyleaflet.WidgetControl(widget=basemap_control_panel, position="topright")  # Define basemap_control here

        # Toggle menu
        toggle_menu = widgets.ToggleButtons(
            options=["None", "Title", "Image", "COG", "JSON", "Basemap"],  # Removed "Video" option
            value=None,
            description="",
            style={"button_width": "80px"},
        )

        def toggle_controls(change):
            for control in [image_control, cog_control, title_control_panel_control, geojson_control, basemap_control]:
                if control in self.controls:
                    self.remove_control(control)
            if change["new"] == "Title":
                self.add_control(title_control_panel_control)
            elif change["new"] == "Image":
                self.add_control(image_control)
            elif change["new"] == "COG":
                self.add_control(cog_control)
            elif change["new"] == "JSON":
                self.add_control(geojson_control)
            elif change["new"] == "Basemap":
                self.add_control(basemap_control)

        toggle_menu.observe(toggle_controls, names="value")

        # Collapsible menu button
        collapse_button = widgets.Button(
            description="",
            button_style="warning",
            tooltip="Click to hide/show the menu",
            icon="eye-slash",
            layout=widgets.Layout(width="40px", height="40px"),
        )

        def toggle_menu_visibility(b):
            """
            Toggles the visibility of the toggle menu and removes all controls when collapsed.

            Args:
                b: The button click event.

            Returns:
                None
            """
            if toggle_menu.layout.display == "none":
                # Show the toggle menu
                toggle_menu.layout.display = "flex"
                collapse_button.icon = "eye-slash"
            else:
                # Hide the toggle menu and remove all controls
                toggle_menu.layout.display = "none"
                collapse_button.icon = "eye"

                # Remove all active controls
                for control in [image_control, cog_control, title_control_panel_control, geojson_control, basemap_control]:
                    if control in self.controls:
                        self.remove_control(control)

        collapse_button.on_click(toggle_menu_visibility)

        # Add controls to the map
        self.add_control(ipyleaflet.WidgetControl(widget=collapse_button, position="topright"))
        self.add_control(ipyleaflet.WidgetControl(widget=toggle_menu, position="topright"))

    def save_map(self):
        """
        Adds a button to save the current map extent as an HTML file.
        """
        save_button = widgets.Button(
            description="Save Map",
            button_style="success",
            tooltip="Save the current map as an HTML file",
            icon="download",
            layout=widgets.Layout(width="100px", height="30px"),
        )

        def save_map_as_html(b):
            """
            Saves the current map as an HTML file.
            """
            html_file = "map.html"
            try:
                # Save the map as an HTML file
                from ipyleaflet import Map
                Map.save(self, html_file)
                print(f"Map saved as {html_file}. Open it in a browser to view.")
            except Exception as e:
                print(f"Error saving map: {e}")

        save_button.on_click(save_map_as_html)
        self.add_control(ipyleaflet.WidgetControl(widget=save_button, position="bottomleft"))