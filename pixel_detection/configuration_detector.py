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

    # Config Gray front RGB to Verify Color Ranges
    # left down 167,168,14
    # Left top 140,5,9
    # back top 221,226,36
    # front right 21,9,143
    # front bottom 137,4,9

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

        # Determine the color name
        color_name = get_color_name(hsv_color)

        # Print the result
        print(f"The color at pixel ({x}, {y}) is: {color_name}")

        # Append the color name to the list
        color_names.append(color_name)

    # Iterate through each cube's region
    for idx in range(1, 9):
        # ROIs for each cube as roi_list
        # roi = roi_list[idx-1]

        # Remove
        roi = hsv

        max_color_count = 0
        dominant_color = ""

        for color, (lower, upper) in colors.items():
            lower = np.array(lower)
            upper = np.array(upper)

            mask = cv2.inRange(roi, lower, upper)
            color_count = np.sum(mask) / 255.0

            if color_count > max_color_count:
                max_color_count = color_count
                dominant_color = color

        config["config"][str(idx)] = dominant_color

    print(config)
    return config


# Function to check if color is within any of the defined ranges
def get_color_name(hsv_color):
    for color_name, (lower, upper) in colors.items():
        if np.all(lower <= hsv_color) and np.all(hsv_color <= upper):
            return color_name
    return ""

