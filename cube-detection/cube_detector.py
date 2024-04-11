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

def find_contours(image, edges, sigma=0.02):
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Loop over the contours to find cubes
    for contour in contours:
        epsilon = sigma * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        # Check if the detected shape has 4 corners (a square or rectangle)
        if len(approx) >= 4:
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)  # Draw the contour
            # print(approx)
    return image

def detect_color(frame, color):
    match color:
        case "blue":
            color_mask = filter_color(frame, lower_blue, upper_blue)
        case "yellow":
            color_mask = filter_color(frame, lower_yellow, upper_yellow)
        case "red":
            color_mask = cv2.addWeighted(filter_color(frame, lower_red1, upper_red1), 1, filter_color(frame, lower_red2, upper_red2), 1, 0)
            # cv2.imwrite('cube-detection/color_mask.jpg', color_mask)
    edges = edge_detection(color_mask)
    contours = find_contours(frame, edges)

    return color_mask
    # cv2.imwrite("cube-detection/edges_"+color+".jpg", contours)

def getCenterPoint(image):
    mask = 0
    for color in ["blue", "yellow", "red"]:
        mask += detect_color(image, color)
    # edges = edge_detection(mask)
    contours = find_contours(image, mask, 1)
    cv2.imshow('contours', contours)

def getMeanAngle(image):
    lower_gray = np.array([0, 20, 200])
    upper_gray = np.array([180, 50, 255])

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)

    contours, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    angles = []

    image_center_x = image.shape[1] // 2
    image_center_y = image.shape[0] // 2

    cv2.circle(image, (image_center_x, image_center_y), 5, (0, 255, 0), -1)

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
                cv2.line(image, (centroid_x, centroid_y), (image_center_x, image_center_y), (255, 0, 0), 1)
    cv2.imshow('frame', image)
    mean_angle = np.mean(angles)
    return mean_angle

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
        # detect_color(frame, "blue")
        getCenterPoint(frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

open_camera_profile('147.88.48.131', 'pren', '463997',
'pren_profile_med')
