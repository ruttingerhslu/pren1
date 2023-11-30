import cv2
import numpy as np
import datetime


def detect_cube_configuration(image_path):
    img = cv2.imread(image_path)

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define color ranges
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

    # List of pixel gray_front_coordinates (y,x)
    x1 = 760
    x2 = 745
    x3 = 967
    x4 = 1132
    x5 = 1127
    x6 = 1000
    x7 = 1010

    y1 = 445
    y2 = 275
    y3 = 142
    y4 = 452
    y5 = 260
    y6 = 575
    y7 = 410

    gray_front_coordinates = [
        (y1, x1),
        (y2, x2),
        (y3, x3),
        (y4, x4),
        (y5, x5),
        (y6, x6),
        (y7, x7)
    ]


    # List of pixel gray_front_coordinates (y,x)
    # TODO
    x1 = 760
    x2 = 745
    x3 = 967
    x4 = 1132
    x5 = 1127
    x6 = 1000
    x7 = 1010

    y1 = 445
    y2 = 275
    y3 = 142
    y4 = 452
    y5 = 260
    y6 = 575
    y7 = 410
    gray_left_coordinates = [
        (y1, x1),
        (y2, x2),
        (y3, x3),
        (y4, x4),
        (y5, x5),
        (y6, x6),
        (y7, x7)
    ]

    print(f"img size : {img.shape}")

    color_1 = hsv[y1, x1]
    color_2 = hsv[y2, x2]
    color_3 = hsv[y3, x3]
    color_4 = hsv[y4, x4]
    color_5 = hsv[y5, x5]
    color_6 = hsv[y6, x6]
    color_7 = hsv[y7, x7]

    print(f"color black (empty) : {hsv[260, 1127]}")
    print(color_1)
    print(color_2)
    print(color_3)
    print(color_4)
    print(color_5)
    print(color_6)
    print(color_7)

    # Config Gray front RGB to Verify Color Ranges
    # left down 167,168,14
    # Left top 140,5,9
    # back top 221,226,36
    # front right 21,9,143
    # front bottom 137,4,9

    # Config Gray front Pixel Coordinates (x/y)
    # left down 760, 445
    # Left top 745, 275
    # back top 967, 142
    # front right 1132, 452
    # right top 1127, 260
    # front bottom 1000, 575
    # front top 1010, 410

    # Create a list to store the colors
    color_names = []

    # Loop over the gray_front_coordinates and check the colors
    for (y, x) in gray_front_coordinates:
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

