from PIL import Image

from pixel_detection.configuration_detector import detect_cube_configuration
from pixel_detection.verification import send_cube_configuration_to_server


def main():
    config = detect_cube_configuration("../cube-detection/img.jpg")
    send_cube_configuration_to_server(config)
