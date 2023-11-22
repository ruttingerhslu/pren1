import cv2
import numpy as np

def getFrame(file):
    cap = cv2.VideoCapture(file)
    timestamp_seconds = 25.2
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_seconds * 1000)
    success, image = cap.read()
    if success:
        return image


frame = getFrame('../resources/pren_cube_01.mp4')

cv2.imwrite("../resources/cubes_gray_area_right_img.jpg", frame)