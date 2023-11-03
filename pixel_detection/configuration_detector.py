import cv2
import numpy as np


def detect_cube_configuration(image_path):
    img = cv2.imread(image_path)

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define color ranges
    colors = {
        "red": ([0, 50, 50], [10, 255, 255]),
        "blue": ([110, 50, 50], [130, 255, 255]),
        "yellow": ([20, 50, 50], [40, 255, 255])
    }

    config = {
        "time": "2023-10-10 17:10:05",
        "config": {}
    }

    # TODO: Define ROI (regions of interest) for each cube

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

    return config


image_path = "../cube-detection/img.jpg"
print(detect_cube_configuration(image_path))
