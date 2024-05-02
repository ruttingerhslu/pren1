from datetime import datetime
import cv2
import numpy as np
import math
import serial
import colorsys

import sys
sys.path.append('modules')
# Constants Cube
RED_RGB = (138, 4, 11)
LOWER_RED_HUE = max(0, int(colorsys.rgb_to_hsv(*RED_RGB)[0] * 180) - 10)
UPPER_RED_HUE = min(180, int(colorsys.rgb_to_hsv(*RED_RGB)[0] * 180) + 10)

color_ranges = {
    "blue": ([80, 100, 100], [130, 255, 255]),
    "yellow": ([20, 50, 100], [40, 255, 255]),
    "red1": (np.array([0, 100, 100]), np.array([50, 255, 255])),
    "red2": (np.array([150, 100, 100]), np.array([180, 255, 255]))
}

uart_color_mapping = {
    "yellow": "Y",
    "blue": "B",
    "red": "R",
    "": "E",
    "undefined": "U"
}

class CubeCalculator:
    def __init__(self) -> None:
        self._img = None
        self._gray = np.array([0, 0, 0])
        self._center_x = None
        self._center_y = None
        self._curr_config = { index + 1 : 'undefined' for index in range(8) }
        self._curr_direction = ""
        self.open_camera_profile('147.88.48.131', 'pren', '463997', 'pren_profile_med')

    def open_camera_profile(self, ip_address, username, password, profile):
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
            self._img = frame
            self.setCenterPoint()
            if (self._center_x != None and self._center_y != None):
                angle = self.getMeanAngle()

                # check if angle is close to 0, 90, etc.
                if (math.isclose(abs(angle) % 90, 0, abs_tol = 1) or math.isclose(angle, 0, abs_tol = 1)):
                    # cv2.imshow('frame', self._img)
                    direction = self.getDirection(angle)
                    if direction != self._curr_direction:
                        self._curr_direction = direction
                        points = self.getCubePoints()
                        arrangement = self.getArrangement(points)
                        self.setConfig(arrangement)
                        self.sendConfig()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def getMeanAngle(self):
        image = self._img

        lower_gray = np.array([180, 175, 170], dtype=np.uint8)
        upper_gray = np.array([240, 220, 220], dtype=np.uint8)

        mask_gray = cv2.inRange(image, lower_gray, upper_gray)
        contours, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        angles = []

        # self._center_x = image.shape[1] // 2
        # self._center_y = (image.shape[0] // 2) - 60

        # cv2.circle(image, (self._center_x, self._center_y), 5, (0, 255, 255), -1)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    centroid_x = int(M["m10"] / M["m00"])
                    centroid_y = int(M["m01"] / M["m00"])

                    delta_x = centroid_x - self._center_x
                    delta_y =  self._center_y - centroid_y 
                    angle_rad = np.arctan2(delta_y, delta_x)
                    angle_deg = np.degrees(angle_rad)

                    angles.append(angle_deg)
        mean_angle = np.mean(angles)
        if mean_angle < 0:
            mean_angle += 360
        cv2.putText(image, str(mean_angle), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        return mean_angle

    def getDirection(self, angle):
        if angle >= 30 and angle <= 120:
            return 'north'
        elif (angle >= 0 and angle <= 30) or (angle >= 330 and angle <= 360):
            return 'east'
        elif angle >= 210 and angle <= 300:
            return 'south'
        elif angle >= 150 and angle <= 240:
            return 'west'
        else:
            return 'unknown'

    def getCubePoints(self):
        a = 90

        points = [[
                (self._center_x - a, self._center_y), # left bottom
                (self._center_x, int(self._center_y + a / 2)), # mid bottom
                (self._center_x + a + 10, self._center_y), # right bottom
                (), #UNKONWN (behind bottom)
            ],
            [
                (self._center_x - a, int(self._center_y - a * 1.5)), # left top
                (), # mid top (NOT CERTAIN) (self._center_x, self._center_y - a)
                (self._center_x + a + 20, int(self._center_y - a * 1.5)), # right top
                (self._center_x, self._center_y - a * 2), # top top
        ]]

        # image_dupe = self._img
        # for point in points:
        #     for p in point: 
        #         if p != ():
        #             cv2.circle(image_dupe, (p), 5, (0, 255, 0), -1)

        # cv2.imshow("frame", image_dupe)
        return points

    def getArrangement(self, points):
        order = []
        arrangement = []
        match (self._curr_direction):
            case 'west':
                order = [0, 1, 2, 3]
            case 'south':
                order = [1, 2, 3, 0]
            case 'east':
                order = [2, 3, 0, 1]
            case 'north':
                order = [3, 0, 1, 2]
        for i in range(0, 2):
            for j in order:
                arrangement.append(points[i][j])
        return arrangement

    def setCenterPoint(self):
        image = self._img

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=20)

        if lines is not None and len(lines) >= 2:
            lines = sorted(lines, key=lambda x: ((x[0][0] - x[0][2])**2 + (x[0][1] - x[0][3])**2)**0.5, reverse=True)[:2]
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            x1, y1, x2, y2 = lines[0][0]
            x3, y3, x4, y4 = lines[1][0]
            det = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
            if det != 0:
                intersection_x = int(((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / det)
                intersection_y = int(((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / det)
                intersection_point = (intersection_x, intersection_y)

                center_x, center_y = image.shape[1] // 2, image.shape[0] // 2
                distance_threshold = 60
                distance_from_center = np.linalg.norm(np.array(intersection_point) - np.array([center_x, center_y]))
                if distance_from_center > distance_threshold:
                    return

                self._center_x = intersection_x
                self._center_y = intersection_y

    def setConfig(self, arrangement):
        cv2.imshow('frame', self._img)
        for index, point in enumerate(arrangement):
            index += 1
            if point != ():
                self._curr_config[index] = self.mapColor(point)
    
    def mapColor(self, point):
        image = self._img
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        hsv_point = hsv_img[tuple(reversed(point))]     
        for color, (lower, upper) in color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            if np.all(hsv_point >= lower) and np.all(hsv_point <= upper):
                if (color.startswith('red')):
                    return 'red'
                else:
                    return color
        return ''

    def sendConfig(self):
        configuration = {
            "time": str(datetime.now()),
            "config": self._curr_config
        }
        # uart_config = self.convert_config_to_uart_format(configuration)
        # self.send_message_to_micro(uart_config)
        print(configuration)

    def convert_config_to_uart_format(self, config):
        result = ""
        for key in sorted(config["config"].keys()):
            color = config["config"][key]
            if color in uart_color_mapping:
                result += uart_color_mapping[color]
            else:
                result += "E"
        return result

    def send_message_to_micro(self, message):
        if isinstance(message, str):
            message += '\n'
            message = message.encode()
        with serial.Serial() as ser:
            ser.baudrate = 9600
            ser.port = '/dev/serial0'
            ser.open()
            ser.write(message)
            ser.close()
        

if __name__ == '__main__':
    CubeCalculator()