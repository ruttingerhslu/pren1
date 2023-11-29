import cv2
import numpy as np

from gray_area_orientation_detector import check_pixels_and_save_frame
from pixel_detection.configuration_detector import detect_cube_configuration
from pixel_detection.verification import send_cube_configuration_to_server

# Path to your video file
video_path = '../resources/pren_cube_01.mp4'

# Initialize the starting timestamp
current_timestamp = 0

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
        (635, 270, 'black'),
        (665, 270, 'gray'),
        (515, 775, 'gray'),
        (550, 775, 'black')
    ]
}

# Define the color range for gray
lower_gray = np.array([0, 0, 40])
upper_gray = np.array([180, 40, 220])



while True:
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    # Check the video and capture the frame
    found, timestamp, position = check_pixels_and_save_frame(
        cap,
        pixel_coords_dict,
        lower_gray,
        upper_gray,
        current_timestamp
    )
    cap.release()

    if found:
        print(f"Frame found at position {position} with timestamp: {timestamp} ms")

        # Update the current timestamp for the next iteration
        # Adding a small increment to avoid rechecking the same frame
        current_timestamp = timestamp + 1
    else:
        print("No more frames with all pixels in the specified color ranges were found.")
        break

    config = detect_cube_configuration(f"../resources/cubes_gray_area_{position}_img.jpg")
    send_cube_configuration_to_server(config)

