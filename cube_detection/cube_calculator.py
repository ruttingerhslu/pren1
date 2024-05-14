from datetime import datetime
import cv2
import numpy as np
import math
import serial

import sys

from modules.verification.verification import send_cube_configuration_to_server
sys.path.append('modules')

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
        self._list_of_centers = []
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
            if (self._center_x == None and self._center_y == None):
                self.setCenterPoint()
            #if (self.verify_config()):
            #    self.send_config_to_server()
            if (self._center_x != None and self._center_y != None):
                angle = self.getMeanAngle()
                # check if angle is close to 0, 90, etc.
                if (math.isclose(abs(angle) % 90, 0, abs_tol = 0.5) or math.isclose(angle, 0, abs_tol = 0.5)):
                    direction = self.getDirection(angle)
                    if direction != self._curr_direction:
                        # cv2.imshow('img', self._img)
                        lower_quantile_length = self.get_lower_quantile_length()
                        self._curr_direction = direction
                        points = self.getCubePoints(lower_quantile_length)
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
        kernel = np.ones((9,9),np.uint8)
        opening = cv2.morphologyEx(mask_gray, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        angles = []

        # self._center_x = image.shape[1] // 2
        # self._center_y = (image.shape[0] // 2) - 60

        # cv2.circle(image, (self._center_x, self._center_y), 5, (0, 255, 255), -1)

        for contour in contours:
            area = cv2.contourArea(contour)
            # only get larger gray areas
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
    
    def get_lower_quantile_length(self):
        image = self._img

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 100, 200)

        mask = np.zeros_like(edges)

        for _, (lower, upper) in color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            color_mask = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), lower, upper)
            mask = cv2.bitwise_or(mask, color_mask)

        masked_edges = cv2.bitwise_and(edges, mask)

        lines = cv2.HoughLinesP(masked_edges, rho=1, theta=np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)

        edge_lengths = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                # cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                edge_lengths.append(length)

        # not median, but lower percentile, as most edges are longer
        lower_quantile_length = np.percentile(edge_lengths, 25)
        lower_quantile_length = lower_quantile_length + lower_quantile_length * 1/4
        return int(lower_quantile_length)

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

    def getCubePoints(self, a):
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
            det = 0
            # sort out longest lines
            lines = sorted(lines, key=lambda x: ((x[0][0] - x[0][2])**2 + (x[0][1] - x[0][3])**2)**0.5, reverse=True)[:2]
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            if len(lines) == 2:
                x1, y1, x2, y2 = lines[0][0]
                x3, y3, x4, y4 = lines[1][0]    
                det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

            if det != 0:
                intersection_x = int(((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / det)
                intersection_y = int(((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / det)
                self._list_of_centers.append((intersection_x, intersection_y))

                if(len(self._list_of_centers) > 30):
                    related_points = self.find_related_points(self._list_of_centers)
                    median_x, median_y = self.get_points_medians(related_points)
                    self._center_x = median_x
                    self._center_y = median_y

    def setConfig(self, arrangement):
        for index, point in enumerate(arrangement):
            index += 1
            if point != (): # and self._curr_config[index] == "undefined":
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

    def euclidean_distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def find_related_points(self, points):
        related_points = []
        for i in range(len(points)):
            for j in range(i+1, len(points)):
                distance = self.euclidean_distance(points[i], points[j])
                if distance <= 0.1 * min(points[i][0], points[j][0], points[i][1], points[j][1]):
                    related_points.append((points[i], points[j]))
        return related_points

    def get_points_medians(self, related_points):
        x_values = []
        y_values = []
        for group in related_points:
            x_values.extend([point[0] for point in group])
            y_values.extend([point[1] for point in group])
        median_x = math.trunc(np.median(x_values))
        median_y = math.trunc(np.median(y_values))
        return median_x, median_y


    def verify_config(self):
        colors = ["red", "blue", "yellow", ""]

        # Check if all keys are present
        keys_present = all(str(i) in self._curr_config for i in range(1, 9))
        if not keys_present:
            return False
        
        # Check if all values are either red, blue, yellow, or empty
        for value in self._curr_config.values():
            if value not in colors:
                return False
        
        return True

    def send_config_to_server(self):
        configuration = {
            "time": str(datetime.now()),
            "config": self._curr_config
        }
        send_cube_configuration_to_server(configuration)
        return

if __name__ == '__main__':
    CubeCalculator()