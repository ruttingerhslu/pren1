import math
import random
import statistics
import cv2
import numpy as np

# blue
lower_blue = np.array([90, 100, 100])
upper_blue = np.array([135, 255, 255])

# yellow
lower_yellow = np.array([25, 100, 100])
upper_yellow = np.array([35, 255, 255])

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

def edge_detection(frame):
    kernel = np.ones((12, 12), np.uint8)
    eroded = cv2.erode(frame, kernel)
    gray = cv2.cvtColor(eroded, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    canny = cv2.Canny(blurred, 20, 40)
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(canny, kernel, iterations=2)
    return dilated

def find_contours(image, edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Loop over the contours to find cubes
    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        # Check if the detected shape has 4 corners (a square or rectangle)
        if len(approx) >= 4:
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)  # Draw the contour
            print(approx)
    return image

def detect_color(frame, color):
    match color:
        case "blue":
            color_mask = filter_color(frame, lower_blue, upper_blue)
        case "yellow":
            color_mask = filter_color(frame, lower_yellow, upper_yellow)
        case "red":
            color_mask = cv2.addWeighted(filter_color(frame, lower_red1, upper_red1), 1, filter_color(frame, lower_red2, upper_red2), 1, 0)
            cv2.imwrite('cube-detection/color_mask.jpg', color_mask)
    edges = edge_detection(color_mask)
    contours = find_contours(frame, edges)

    cv2.imwrite("cube-detection/edges_"+color+".jpg", contours)

frame = getFrame('../resources/pren_cube_01.mp4')
detect_color(frame.copy(), "blue")
detect_color(frame.copy(), "yellow")
detect_color(frame.copy(), "red")
