import ipyleaflet
import geopandas as gpd
from ipyleaflet import GeoJSON
import ipywidgets as widgets
import base64
from pathlib import Path


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

    def add_video(self, video_url, bounds, opacity=0.7, name="Video Overlay", zoom_to_layer=True):
        """
        Adds a video overlay to the map using a video URL.

        Args:
            video_url (str): The URL of the MP4 video to be added.
            bounds (list): The geographical bounds for the video overlay as [[lat_min, lon_min], [lat_max, lon_max]].
            opacity (float, optional): The opacity of the video overlay. Defaults to 0.7.
            name (str, optional): The name of the video overlay. Defaults to "Video Overlay".
            zoom_to_layer (bool, optional): Whether to zoom the map to the video layer. Defaults to True.

        Returns:
            None
        """
        # Create the video overlay using the provided URL
        video_overlay = ipyleaflet.VideoOverlay(
            url=video_url,
            bounds=bounds,
            opacity=opacity,
            name=name,
        )

        # Add the video overlay to the map
        self.add(video_overlay)

        # Zoom to the layer if the option is enabled
        if zoom_to_layer:
            self.fit_bounds(bounds)

    def add_title(self, title="Map Title", position="topleft", font_size="16px", font_color="black"):
        """
        Adds a title to the map with dynamic controls to change its properties.

        Args:
            title (str, optional): The initial text of the title to be displayed on the map. Defaults to "Map Title".
            position (str, optional): The initial position of the title on the map. Defaults to "topleft".
            font_size (str, optional): The initial font size of the title. Defaults to "16px".
            font_color (str, optional): The initial font color of the title. Defaults to "black".

        Returns:
            None
        """
        # Create a label widget for the title
        title_widget = widgets.HTML(
            value=f"<div style='color:{font_color}; font-size:{font_size}; text-align:center;'>{title}</div>"
        )

        # Add the title widget to the map as a WidgetControl
        title_control = ipyleaflet.WidgetControl(widget=title_widget, position=position)
        self.add_control(title_control)

        # Create widgets for dynamic control
        title_input = widgets.Text(value=title, description="Title:")
        font_size_slider = widgets.IntSlider(value=int(font_size[:-2]), min=10, max=50, step=1, description="Font Size:")
        font_color_picker = widgets.ColorPicker(value=font_color, description="Font Color:")
        position_dropdown = widgets.Dropdown(
            options=["topright", "topleft", "bottomright", "bottomleft"],
            value=position,
            description="Position:",
        )

        # Function to update the title properties
        def update_title(change):
            nonlocal title_control  # Ensure we update the reference to the control
            title_widget.value = (
                f"<div style='color:{font_color_picker.value}; font-size:{font_size_slider.value}px; text-align:center;'>"
                f"{title_input.value}</div>"
            )

            # Update the position of the title
            self.remove_control(title_control)
            title_control = ipyleaflet.WidgetControl(widget=title_widget, position=position_dropdown.value)
            self.add_control(title_control)

        # Observe changes in the widgets
        title_input.observe(update_title, names="value")
        font_size_slider.observe(update_title, names="value")
        font_color_picker.observe(update_title, names="value")
        position_dropdown.observe(update_title, names="value")

        # Create a control panel for the widgets
        control_panel = widgets.VBox([title_input, font_size_slider, font_color_picker, position_dropdown])
        control_panel_control = ipyleaflet.WidgetControl(widget=control_panel, position="topright")
        self.add_control(control_panel_control)

    def add_combined_ui(self, options=None, video_bounds=None, title="Map Title", position="topleft", font_size="16px", font_color="black"):
        """
        Combines all functionalities (image GUI, video overlay, and title) into one unified UI.

        Args:
            options (dict, optional): A dictionary for image options where keys are image names (strings)
                and values are tuples containing the image URL (str) and bounds (list).
            video_bounds (list, optional): The geographical bounds for the video overlay as [[lat_min, lon_min], [lat_max, lon_max]].
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

        if video_bounds is None:
            video_bounds = [[-10, -20], [10, 20]]

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
        video_url_input = widgets.Text(value="https://example.com/sample_video.mp4", description="Video URL:")
        video_opacity_slider = widgets.FloatSlider(value=0.7, min=0, max=1, step=0.1, description="Opacity:")

        # Widgets for title
        title_input = widgets.Text(value=title, description="Title:")
        font_size_slider = widgets.IntSlider(value=int(font_size[:-2]), min=10, max=50, step=1, description="Font Size:")
        font_color_picker = widgets.ColorPicker(value=font_color, description="Font Color:")
        position_dropdown = widgets.Dropdown(
            options=["topleft", "topright", "topleft", "bottomright", "bottomleft"],
            value=position,
            description="Position:",
        )

        # Dictionary to keep track of overlays
        current_overlay = {"image": None, "video": None}

        # Create the title widget and control
        title_widget = widgets.HTML(
            value=f"<div style='color:{font_color}; font-size:{font_size}; text-align:center;'>{title}</div>"
        )
        title_control = ipyleaflet.WidgetControl(widget=title_widget, position=position)
        self.add_control(title_control)

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

        def add_video_overlay(change):
            if current_overlay["video"]:
                self.remove(current_overlay["video"])
            video_url = video_url_input.value
            overlay = ipyleaflet.VideoOverlay(
                url=video_url,
                bounds=video_bounds,
                opacity=video_opacity_slider.value,
            )
            self.add(overlay)
            current_overlay["video"] = overlay

        def update_title(change):
            title_widget.value = (
                f"<div style='color:{font_color_picker.value}; font-size:{font_size_slider.value}px; text-align:center;'>"
                f"{title_input.value}</div>"
            )
            self.remove_control(title_control)
            new_control = ipyleaflet.WidgetControl(widget=title_widget, position=position_dropdown.value)
            self.add_control(new_control)

        # Observe changes in widgets
        image_dropdown.observe(update_image, names="value")
        lat_min_slider.observe(update_image_bounds, names="value")
        lon_min_slider.observe(update_image_bounds, names="value")
        lat_max_slider.observe(update_image_bounds, names="value")
        lon_max_slider.observe(update_image_bounds, names="value")
        video_url_input.observe(add_video_overlay, names="value")
        video_opacity_slider.observe(add_video_overlay, names="value")
        title_input.observe(update_title, names="value")
        font_size_slider.observe(update_title, names="value")
        font_color_picker.observe(update_title, names="value")
        position_dropdown.observe(update_title, names="value")

        # Create control panels
        image_control_panel = widgets.VBox([image_dropdown, image_sliders])
        video_control_panel = widgets.VBox([video_url_input, video_opacity_slider])
        title_control_panel = widgets.VBox([title_input, font_size_slider, font_color_picker, position_dropdown])

        # Add control panels to the map
        self.add_control(ipyleaflet.WidgetControl(widget=image_control_panel, position="topright"))
        self.add_control(ipyleaflet.WidgetControl(widget=video_control_panel, position="bottomright"))
        self.add_control(ipyleaflet.WidgetControl(widget=title_control_panel, position="bottomleft"))

