import math
import random
import statistics
import cv2
import numpy as np

# red1
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])

# red2
lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([180, 255, 255])

def getFrame(file):
    cap = cv2.VideoCapture(file)
    randomFrame = random.randint(0, cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, 1700)
    success, image = cap.read()
    if success:
        return image

def filter_color(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    return result

def watershed(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    canny = cv2.Canny(blurred, 20, 40)
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(canny, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image = frame
    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        # Check if the detected shape has 4 corners
        if len(approx) >= 4:
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)
    return dilated


frame = getFrame('cube-detection/pren_cube_01.mp4')
color_mask = cv2.addWeighted(filter_color(frame, lower_red1, upper_red1), 1, filter_color(frame, lower_red2, upper_red2), 1, 0)
cv2.imwrite('cube-detection/watershed.jpg', watershed(color_mask))
