import cv2
import numpy as np
import datetime

colors = {
        "red": ([170, 50, 50], [180, 255, 255]),
        "blue": ([110, 50, 50], [130, 255, 255]),
        "yellow": ([20, 50, 50], [40, 255, 255]),
        "brown": ([0, 100, 50], [20, 160, 80]),
        "black": ([70, 10, 20], [80, 20, 30])
    }

config = {
    # Format "2023-10-10 17:10:05"
    "time": str(datetime.datetime.now()),
    "config": {}
}

# Config Gray top Pixel Coordinates (x/y)
# TODO
# x, y, position, 100% sure
top_cubes_coordinates = [
    (0, 0, 1, False),  # impossible read
    (800, 460, 2, True),
    (965, 535, 3, True),
    (1140, 435, 4, True),
    (950, 100, 5, True),
    (820, 200, 6, True),
    (965, 300, 7, True),
    (1120, 150, 8, True)
]

bottom_cubes_coordinates = [
    (0, 0, 3, False),  # impossible read
    (800, 460, 4, True),
    (965, 535, 1, True),
    (1140, 435, 2, True),
    (950, 100, 7, True),
    (820, 200, 8, True),
    (965, 300, 5, True),
    (1120, 150, 6, True)
]

right_cubes_coordinates = [
    (0, 0, 0, False),  # impossible read
    (800, 460, 0, True),
    (965, 535, 0, True),
    (1140, 435, 0, True),
    (950, 100, 0, True),
    (820, 200, 0, True),
    (965, 300, 0, True),
    (1120, 150, 0, True)
]

left_cubes_coordinates = [
    (0, 0, 0, False),  # impossible read
    (800, 460, 0, True),
    (965, 535, 0, True),
    (1140, 435, 0, True),
    (950, 100, 0, True),
    (820, 200, 0, True),
    (965, 300, 0, True),
    (1120, 150, 0, True)
]

def detect_cube_configuration(image_path, position):
    img = cv2.imread(image_path)

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Config Gray front RGB to Verify Color Ranges
    # left down 167,168,14
    # Left top 140,5,9
    # back top 221,226,36
    # front right 21,9,143
    # front bottom 137,4,9

    # Config Gray bottom Pixel Coordinates (x/y)
    # left down 760, 445
    # Left top 745, 275
    # back top 967, 142
    # front right 1132, 452
    # right top 1127, 260
    # front bottom 1000, 575
    # front top 1010, 410



    # left down 760, 445
    # Left top 745, 275
    # back top 967, 142
    # front right 1132, 452
    # right top 1127, 260
    # front bottom 1000, 575
    # front top 1010, 410

    # Config Gray left Pixel Coordinates (x/y)
    # TODO
    # left down 760, 445
    # Left top 745, 275
    # back top 967, 142
    # front right 1132, 452
    # right top 1127, 260
    # front bottom 1000, 575
    # front top 1010, 410

    # Config Gray right Pixel Coordinates (x/y)
    # TODO
    # left down 760, 445
    # Left top 745, 275
    # back top 967, 142
    # front right 1132, 452
    # right top 1127, 260
    # front bottom 1000, 575
    # front top 1010, 410

    # Create a list to store the colors
    color_names = []

    coordinates_to_check = None
    if position == "top":
        coordinates_to_check = top_cubes_coordinates
    elif position == "bottom":
        coordinates_to_check = bottom_cubes_coordinates
    elif position == "left":
        coordinates_to_check = left_cubes_coordinates
    elif position == "right":
        coordinates_to_check = right_cubes_coordinates

    # Loop over the front_coordinates and check the colors
    for (y, x, position) in coordinates_to_check:
        # Get the HSV color of the pixel
        hsv_color = hsv[y, x]

        # Determine the color name
        print(hsv_color)
        color_name = get_color_name(hsv_color, colors)

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

    print(color_names)
    print(config)
    return config


# Function to check if color is within any of the defined ranges
def get_color_name(hsv_color, colors):
    for color_name, (lower, upper) in colors.items():
        if np.all(lower <= hsv_color) and np.all(hsv_color <= upper):
            return color_name
    return "undefined"

