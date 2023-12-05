import cv2
import numpy as np

from pixel_detection.constants import *

fixed_positions = []


# If position < 5 and priority == True
# then we can identify the lower three front cubes precisely
# Need to also check if the color is available, or it's gray/black/brown -> in that case keep undefined/""

def detect_cube_configuration(image_path, orientation):
    img = cv2.imread(image_path)

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Create a list to store the colors
    color_names = []

    coordinates_to_check = None
    if orientation == "top":
        coordinates_to_check = top_cubes_coordinates
    elif orientation == "bottom":
        coordinates_to_check = bottom_cubes_coordinates
    elif orientation == "left":
        coordinates_to_check = left_cubes_coordinates
    elif orientation == "right":
        coordinates_to_check = right_cubes_coordinates

    # Loop over the front_coordinates and check the colors
    for (x, y, cube_config_position, priority) in coordinates_to_check:
        # Get the HSV color of the pixel
        hsv_color = hsv[y, x]

        config_position_exists = str(cube_config_position) in config["config"]

        # Determine the color name
        color_name = get_color_name(hsv_color)

        if cube_config_position in orientation_positions_map.get(orientation):
            # set the value in the config
            if color_name not in ["black", "brown"] and not config_position_exists:
                config["config"][str(cube_config_position)] = color_name

        if cube_config_position in orientation_top_positions_map.get(orientation):
            # set the value in the config
            if color_name not in ["black", "brown"] and not config_position_exists:
                config["config"][str(cube_config_position)] = color_name
    return config


# Function to check if color is within any of the defined ranges
def get_color_name(hsv_color):
    for color_name, (lower, upper) in colors.items():
        if np.all(lower <= hsv_color) and np.all(hsv_color <= upper):
            return color_name
    return ''
