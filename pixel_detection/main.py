from datetime import datetime

import cv2
import numpy as np

from gray_area_orientation_detector import check_pixels_and_save_frame
from pixel_detection.configuration_detector import detect_cube_configuration
from pixel_detection.verification import send_cube_configuration_to_server

from pixel_detection.constants import *

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
        if color != '':
            config["config"][key] = color

    # TODO add to pixel_coords_dict the configuration_detector which cube configs are 100% found and have priority
    return config


# Initialize the starting timestamp
current_frame = 0

found_images = 0

config = {'1': '',
          '2': '',
          '3': '',
          '4': '',
          '5': '',
          '6': '',
          '7': '',
          '8': ''}

config_request_body = {
    "time": "",
    "config": config
}

start_time = datetime.now()
print(f"Starttimestamp: {start_time}")

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
        current_frame = frame_number + 90
        found_images += 1
    else:
        print("No more frames with all pixels in the specified color ranges were found.")
        break

    new_config = detect_cube_configuration(f"../resources/cubes_gray_area_{position}.jpg", position)
    config_request_body = merge_configs(config_request_body, new_config)
    print(config_request_body)
    print(f"found Images: {found_images}")
    if found_images == 4:
        send_cube_configuration_to_server(config_request_body)
        end_time = datetime.now()
        time_used = end_time - start_time
        print(f"Endtimestamp: {end_time}")
        print(f"Time needed to complete: {time_used}")
