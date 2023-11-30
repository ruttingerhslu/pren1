from datetime import datetime

import cv2
import numpy as np

from gray_area_orientation_detector import check_pixels_and_save_frame
from pixel_detection.configuration_detector import detect_cube_configuration
from pixel_detection.verification import send_cube_configuration_to_server


def merge_configs(config, new_config):
    print('Merging Configs')

    if config == new_config:
        return new_config

    # Update the time field
    config_request_body["time"] = datetime.now().isoformat()
    new_config_data = new_config["config"]
    print(new_config_data)
    config_data = config["config"]
    print(config_data)

    # Update the config field
    for key, color in new_config["config"].items():
        if color != 'undefined':
            config["config"][key] = color

    # TODO add to pixel_coords_dict the configuration_detector which cube configs are 100% found and have priority
    return config


# Path to your video file
video_path = '../resources/pren_cube_02.mp4'

# Initialize the starting timestamp
current_frame = 0

config = {'1': 'undefined',
          '2': 'undefined',
          '3': 'undefined',
          '4': 'undefined',
          '5': 'undefined',
          '6': 'undefined',
          '7': 'undefined',
          '8': 'undefined'}

config_request_body = {
    "time": "",
    "config": config
}

found_images = 0

# Define the coordinates to check
pixel_coords_dict = {
    'bottom': [
        (615, 720, 'black'),
        (650, 720, 'gray'),
        (1350, 720, 'gray'),
        (400, 720, 'black')
    ],
    'top': [
        (1265, 270, 'black'),
        (1245, 270, 'gray'),
        (655, 270, 'gray'),
        (630, 270, 'black')
    ],
    'right': [
        (1200, 230, 'black'),
        (1210, 230, 'gray'),
        (1480, 710, 'gray'),
        (1460, 710, 'black')
    ],
    'left': [
        (670, 280, 'black'),
        (655, 290, 'gray'),
        (605, 700, 'gray'),
        (625, 725, 'black')
    ]
}

while True:
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    success, frame = cap.read()

    found, frame_number, position = check_pixels_and_save_frame(
        cap,
        pixel_coords_dict,
        current_frame
    )
    cap.release()

    if found:
        print(f"Frame found at position {position} at frame: {frame_number}")

        # Update the current timestamp + advance for the next iteration
        current_frame = frame_number + 20
    else:
        print("No more frames with all pixels in the specified color ranges were found.")
        break

    new_config = detect_cube_configuration(f"../resources/cubes2_gray_area_{position}_img.jpg", position)
    config_request_body = merge_configs(config_request_body, new_config)
    print(config_request_body)
    if found_images == 2:
        send_cube_configuration_to_server(config_request_body)
