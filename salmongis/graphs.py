import ipyleaflet
import geopandas as gpd
from ipyleaflet import GeoJSON
import ipywidgets as widgets
import base64
from pathlib import Path
from localtileserver import TileClient, get_leaflet_tile_layer


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
    

    def add_combined_ui(self, options=None, video_options=None, video_bounds=None, cog_options=None, title="Map Title", position="topleft", font_size="16px", font_color="black"):
        """
        Combines all functionalities (image GUI, video overlay, title, and COG) into one unified UI with a menu.

        Args:
            options (dict, optional): A dictionary for image options where keys are image names (strings)
                and values are tuples containing the image URL (str) and bounds (list).
            video_options (dict, optional): A dictionary for video options where keys are video names (strings)
                and values are file paths or URLs to the video files.
            video_bounds (list, optional): The geographical bounds for the video overlay as [[lat_min, lon_min], [lat_max, lon_max]].
            cog_options (dict, optional): A dictionary for COG options where keys are COG names (strings)
                and values are URLs to the COG files.
            title (str, optional): The initial text of the title to be displayed on the map. Defaults to "Map Title".
            position (str, optional): The initial position of the title on the map. Defaults to "topleft".
            font_size (str, optional): The initial font size of the title. Defaults to "16px".
            font_color (str, optional): The initial font color of the title. Defaults to "black".

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

        if video_options is None:
            video_options = {
                "Sample Video 1": "https://example.com/sample_video1.mp4",
                "Sample Video 2": "https://example.com/sample_video2.mp4",
            }

        if video_bounds is None:
            video_bounds = [[-10, -20], [10, 20]]

        if cog_options is None:
            cog_options = {
                "Select a COG": None,
                "COG 1": "https://example.com/cog1.tif",
                "COG 2": "https://example.com/cog2.tif",
            }

        # Widgets for image GUI
        image_dropdown = widgets.Dropdown(
            options=["Select an image"] + list(options.keys()),
            value="Select an image",
            description="Image:",
        )
        lat_min_slider = widgets.FloatSlider(value=0, min=-90, max=90, step=0.1, description="Lat Min:")
        lon_min_slider = widgets.FloatSlider(value=0, min=-180, max=180, step=0.1, description="Lon Min:")
        lat_max_slider = widgets.FloatSlider(value=0, min=-90, max=90, step=0.1, description="Lat Max:")
        lon_max_slider = widgets.FloatSlider(value=0, min=-180, max=180, step=0.1, description="Lon Max:")
        image_sliders = widgets.VBox([lat_min_slider, lon_min_slider, lat_max_slider, lon_max_slider])

        # Widgets for video overlay
        video_dropdown = widgets.Dropdown(
            options=["Select a video"] + list(video_options.keys()),
            value="Select a video",
            description="Video:",
        )
        video_opacity_slider = widgets.FloatSlider(value=0.7, min=0, max=1, step=0.1, description="Opacity:")

        def add_video_overlay(change):
            selected_video = video_dropdown.value
            if selected_video == "Select a video":
                if current_overlay["video"]:
                    self.remove(current_overlay["video"])
                    current_overlay["video"] = None
            else:
                if current_overlay["video"]:
                    self.remove(current_overlay["video"])
                video_url = video_options[selected_video]
                overlay = ipyleaflet.VideoOverlay(
                    url=video_url,
                    bounds=video_bounds,
                    opacity=video_opacity_slider.value,
                )
                self.add(overlay)
                current_overlay["video"] = overlay

                # Zoom to the video layer bounds
                self.fit_bounds(video_bounds)

        # Observe changes in the video dropdown and opacity slider
        video_dropdown.observe(add_video_overlay, names="value")
        video_opacity_slider.observe(add_video_overlay, names="value")

        # Create the video control panel
        video_control_panel = widgets.VBox([video_dropdown, video_opacity_slider])
        video_control = ipyleaflet.WidgetControl(widget=video_control_panel, position="topright")

        # Widgets for COG
        cog_dropdown = widgets.Dropdown(
            options=cog_options,
            value=None,
            description="COG:",
            layout=widgets.Layout(width="400px"),
        )
        cog_opacity_slider = widgets.FloatSlider(value=0.8, min=0, max=1, step=0.1, description="Opacity:")

        # Widgets for title
        title_input = widgets.Text(value=title, description="Title:")
        font_size_slider = widgets.IntSlider(value=int(font_size[:-2]), min=10, max=50, step=1, description="Font Size:")
        font_color_picker = widgets.ColorPicker(value=font_color, description="Font Color:")
        position_dropdown = widgets.Dropdown(
            options=["topcenter", "topright", "topleft", "bottomright", "bottomleft"],
            value=position,
            description="Position:",
        )

        # Dictionary to keep track of overlays
        current_overlay = {"image": None, "video": None, "cog": None}

        # Create the title widget and control
        title_widget = widgets.HTML(
            value=f"<div style='color:{font_color}; font-size:{font_size}; text-align:center; background-color: transparent;'>{title}</div>"
        )
        self.title_control = ipyleaflet.WidgetControl(widget=title_widget, position=position)  # Use self.title_control
        self.add_control(self.title_control)

        # Functions for updating the map
        def update_image(change):
            selected_image = image_dropdown.value
            if selected_image == "Select an image":
                if current_overlay["image"]:
                    self.remove(current_overlay["image"])
                    current_overlay["image"] = None
            else:
                if current_overlay["image"]:
                    self.remove(current_overlay["image"])
                image_url, bounds = options[selected_image]
                lat_min_slider.value, lon_min_slider.value = bounds[0]
                lat_max_slider.value, lon_max_slider.value = bounds[1]
                overlay = ipyleaflet.ImageOverlay(url=image_url, bounds=bounds)
                self.add(overlay)
                current_overlay["image"] = overlay

        def update_image_bounds(change):
            if current_overlay["image"]:
                new_bounds = [
                    [lat_min_slider.value, lon_min_slider.value],
                    [lat_max_slider.value, lon_max_slider.value],
                ]
                current_overlay["image"].bounds = new_bounds

        def add_cog_layer(change):
            if current_overlay["cog"]:
                self.remove(current_overlay["cog"])
                current_overlay["cog"] = None

            cog_url = cog_dropdown.value
            if cog_url:
                try:
                    client = TileClient(cog_url)
                    cog_layer = get_leaflet_tile_layer(client, opacity=cog_opacity_slider.value)
                    self.add(cog_layer)
                    current_overlay["cog"] = cog_layer

                    # Zoom to the bounds of the COG layer
                    self.fit_bounds(client.bounds)
                except Exception as e:
                    print(f"Error adding COG layer: {e}")

        def update_title(change):
            title_widget.value = (
                f"<div style='color:{font_color_picker.value}; font-size:{font_size_slider.value}px; text-align:center;'>"
                f"{title_input.value}</div>"
            )
            # Check if the control exists on the map before removing it
            if self.title_control in self.controls:
                self.remove_control(self.title_control)
            # Create a new control with the updated title and position
            self.title_control = ipyleaflet.WidgetControl(widget=title_widget, position=position_dropdown.value)
            self.add_control(self.title_control)

        # Observe changes in widgets
        image_dropdown.observe(update_image, names="value")
        lat_min_slider.observe(update_image_bounds, names="value")
        lon_min_slider.observe(update_image_bounds, names="value")
        lat_max_slider.observe(update_image_bounds, names="value")
        lon_max_slider.observe(update_image_bounds, names="value")
        video_dropdown.observe(add_video_overlay, names="value")
        video_opacity_slider.observe(add_video_overlay, names="value")
        cog_dropdown.observe(add_cog_layer, names="value")
        cog_opacity_slider.observe(add_cog_layer, names="value")
        title_input.observe(update_title, names="value")
        font_size_slider.observe(update_title, names="value")
        font_color_picker.observe(update_title, names="value")
        position_dropdown.observe(update_title, names="value")

        # Create control panels
        image_control_panel = widgets.VBox([image_dropdown, image_sliders])
        video_control_panel = widgets.VBox([video_dropdown, video_opacity_slider])
        cog_control_panel = widgets.VBox([cog_dropdown, cog_opacity_slider])
        title_control_panel = widgets.VBox([title_input, font_size_slider, font_color_picker, position_dropdown])

        # Create WidgetControl objects once
        image_control = ipyleaflet.WidgetControl(widget=image_control_panel, position="topright")
        video_control = ipyleaflet.WidgetControl(widget=video_control_panel, position="topright")
        cog_control = ipyleaflet.WidgetControl(widget=cog_control_panel, position="topright")
        title_control_panel_control = ipyleaflet.WidgetControl(widget=title_control_panel, position="topright")

        # Toggle menu with Font Awesome icons
        toggle_menu = widgets.ToggleButtons(
            options=[
                ("None"),
                ("Image"),
                ("Video"),
                ("COG"),
                ("Title"),
            ],
            value=None,
            description="",
            style={"button_width": "75px"},
        )

        # Function to toggle controls
        def toggle_controls(change):
            # Remove all control panels
            for control in [image_control, video_control, cog_control, title_control_panel_control]:
                if control in self.controls:
                    self.remove_control(control)
            # Add the selected control panel
            if change["new"] == "Image":
                self.add_control(image_control)
            elif change["new"] == "Video":
                self.add_control(video_control)
            elif change["new"] == "COG":
                self.add_control(cog_control)
            elif change["new"] == "Title":
                self.add_control(title_control_panel_control)

        toggle_menu.observe(toggle_controls, names="value")

        # Add the toggle menu to the map
        self.add_control(ipyleaflet.WidgetControl(widget=toggle_menu, position="topright"))
