from datetime import datetime

# Cube Config Detection #####
colors = {
    "red": ([170, 50, 50], [180, 255, 255]),
    "blue": ([110, 50, 50], [130, 255, 255]),
    "yellow": ([20, 50, 50], [40, 255, 255]),
    "brown": ([0, 100, 50], [20, 160, 80]),
    "black": ([70, 10, 20], [80, 20, 30])
}

orientation_positions_map = {"right": [1, 3, 4], "left": [1, 2, 3], "top": [2, 3, 4], "bottom": [1, 2, 4]}

## Could define front right/left as well -> pixel coords required
orientation_top_positions_map = {"right": [6], "left": [8], "top": [5], "bottom": [7]}

# Json Config to send to server for verification
config = {
    # Format "2023-10-10 17:10:05"
    "time": str(datetime.now()),
    "config": {}
}

# Mapping of colors to their corresponding initials for UART Message to MicroController
uart_color_mapping = {
    "yellow": "Y",
    "blue": "B",
    "red": "R",
    "": "E",
    "undefined": "U"
}


# Config Cube Pixel Coordinates (x/y)
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
    (0, 0, 2, False),  # impossible read
    (800, 460, 3, True),
    (965, 535, 4, True),
    (1140, 435, 1, True),
    (950, 150, 6, True),
    (820, 200, 7, True),
    (965, 300, 8, True),
    (1120, 150, 5, True)
]

left_cubes_coordinates = [
    (0, 0, 4, False),  # impossible read
    (800, 460, 1, True),
    (965, 535, 2, True),
    (1140, 435, 3, True),
    (950, 100, 8, True),
    (820, 200, 5, True),
    (965, 300, 6, True),
    (1120, 150, 7, True)
]

# Main Constants #####

# Path to your video file
video_path = '../resources/pren_cube_01.mp4'

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

# Verification Constants #####

token = "92CMFsR7Zsrm"
base_url_test_server_http = "http://52.58.217.104:5000"
base_url_test_server_https = "https://18.192.48.168:5000"
base_url_prod_server = "https://oawz3wjih1.execute-api.eu-central-1.amazonaws.com"
endpoint = "/cubes/team09"
# URL for Verification
url = base_url_test_server_http + endpoint

# HTTP Headers
headers = {
    "Content-Type": "application/json",
    "Auth": token
}
