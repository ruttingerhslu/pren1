import cv2
import numpy as np
import math
from matplotlib import pyplot as plt

def getFrame(file, frame):
    cap = cv2.VideoCapture(file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    success, image = cap.read()
    if success:
        return image

# blue
lower_blue = np.array([90, 100, 100])
upper_blue = np.array([135, 255, 255])

# yellow
lower_yellow = np.array([25, 100, 100])
upper_yellow = np.array([35, 255, 255])

# red1
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([50, 255, 255])

# red2
lower_red2 = np.array([150, 100, 100])
upper_red2 = np.array([180, 255, 255])

def filter_color(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    return result

def get_mask(frame, color):
    match color:
        case "blue":
            return filter_color(frame, lower_blue, upper_blue)
        case "yellow":
            return filter_color(frame, lower_yellow, upper_yellow)
        case "red":
            return cv2.addWeighted(filter_color(frame, lower_red1, upper_red1), 1, filter_color(frame, lower_red2, upper_red2), 1, 0)

def edge_detection(frame):
    kernel = np.ones((12, 12), np.uint8)
    eroded = cv2.erode(frame, kernel)
    gray = cv2.cvtColor(eroded, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    canny = cv2.Canny(blurred, 0, 255)
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(canny, kernel, iterations=2)
    return dilated

def getCenterPoint(frame, color):
    mask = get_mask(frame, color)
    edges = edge_detection(mask)
    # cv2.imshow('frame', edges)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # area = cv2.contourArea(contour)
        # if area > 200:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            centroid_x = int(M["m10"] / M["m00"])
            centroid_y = int(M["m01"] / M["m00"])
            cv2.circle(frame, (centroid_x, centroid_y), 5, (0, 255, 0), -1)
    cv2.imshow('frame', frame)

def getMeanAngle(image):
    lower_gray = np.array([175, 175, 175], dtype=np.uint8)
    upper_gray = np.array([255, 255, 255], dtype=np.uint8)

    mask_gray = cv2.inRange(image, lower_gray, upper_gray)

    contours, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    angles = []

    image_center_x = image.shape[1] // 2
    image_center_y = image.shape[0] // 2

    # cv2.circle(image, (image_center_x, image_center_y), 5, (0, 255, 0), -1)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                centroid_x = int(M["m10"] / M["m00"])
                centroid_y = int(M["m01"] / M["m00"])

                delta_x = centroid_x - image_center_x
                delta_y =  image_center_y - centroid_y 
                angle_rad = np.arctan2(delta_y, delta_x)
                angle_deg = np.degrees(angle_rad)

                angles.append(angle_deg)
                # cv2.line(image, (centroid_x, centroid_y), (image_center_x, image_center_y), (255, 0, 0), 1)
    # cv2.imshow('frame', image)
    mean_angle = np.mean(angles)
    return mean_angle


def calculateCoordinates(angle, image):
    a = 50
    b = 70

    # as quadrant is 90 degrees, and the 'angle' is the middle of the quadrant, to get the edges just add/subtract 45
    angle_right = angle - 45
    angle_left = angle + 45

    center_x = image.shape[1] // 2
    center_y = image.shape[0] // 2

    new_x = int(center_x - 200)
    # new_y = int(center_y - 20 * math.tan(angle_right))
    new_y = center_y

    cv2.circle(image, (center_x, center_y), 5, (0, 255, 0), -1)

    cv2.circle(image, (new_x, new_y), 5, (0, 255, 0), -1)

    # cv2.line(image, (new_x, new_y), (center_x, center_y), (255, 0, 0))

    cv2.imwrite('img.png', image)
    return 0

def open_camera_profile(ip_address, username, password, profile):
    # Open the camera
    cap = cv2.VideoCapture('rtsp://' +
                            username + ':' +
                            password +
                            '@' + ip_address +
                            '/axis-media/media.amp' +
                            '?streamprofile=' + profile)
    if cap is None or not cap.isOpened():
        print('Warning: unable to open video source: ', ip_address)
        return None
    while True:
        ret, frame = cap.read()
        if not ret:
            print('Warning: unable to read next frame')
            break
        # getMeanAngle(frame)
        # getCenterPoint(frame, "red")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

open_camera_profile('147.88.48.131', 'pren', '463997',
'pren_profile_med')

# frame = 1000
# image = getFrame('../resources/pren_cube_01.mp4', frame)
# print("Mean angle: ", getMeanAngle(image))
# print(calculateCoordinates(getMeanAngle(image), image))