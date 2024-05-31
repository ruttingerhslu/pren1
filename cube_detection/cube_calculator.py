from datetime import datetime
import json
import cv2
import numpy as np
import math
import serial
import time
import requests


color_ranges = {
    "blue": ([80, 100, 75], [130, 255, 255]),
    "yellow": ([20, 100, 75], [40, 255, 255]),
    "red1": (np.array([0, 100, 75]), np.array([50, 255, 255])),
    "red2": (np.array([150, 100, 75]), np.array([180, 255, 255]))
}

uart_color_mapping = {
    "yellow": "Y",
    "blue": "B",
    "red": "R",
    "": "E",
    "undefined": "U"
}

# Verification Constants #####

token = "92CMFsR7Zsrm"
base_url_test_server_http = "http://52.58.217.104:5000"
base_url_test_server_https = "https://18.192.48.168:5000"
base_url_prod_server = "https://oawz3wjih1.execute-api.eu-central-1.amazonaws.com"
endpoint = "/cubes/team09"
# URL for Verification
url = base_url_prod_server + endpoint

# HTTP Headers
headers = {
    "Content-Type": "application/json",
    "Auth": token
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
        self._config_completed = False

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
        while not(self._config_completed):
            ret, frame = cap.read()
            if not ret:
                print('Warning: unable to read next frame')
                break
            self._img = frame
            if (self._center_x == None and self._center_y == None):
                self.setCenterPoint()
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
                        self.verify_config()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.send_config_to_server()

    def getMeanAngle(self):
        image = self._img

        lower_gray = np.array([180, 175, 170], dtype=np.uint8)
        upper_gray = np.array([240, 220, 220], dtype=np.uint8)

        # ellipse window
        height, width = image.shape[:2]
        center = (self._center_x, self._center_y + 50)
        axes = (330, 240)
        angle = 0
        ellipse_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.ellipse(ellipse_mask, center, axes, angle, 0, 360, 255, -1)
        black_background = np.zeros_like(image)
        ellipse_window = cv2.bitwise_and(image, image, mask=ellipse_mask)

        mask_gray = cv2.inRange(ellipse_window, lower_gray, upper_gray)
        kernel = np.ones((9, 9), np.uint8)
        opening = cv2.morphologyEx(mask_gray, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        angles = []

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
        if angle >= 45 and angle <= 135:
            return 'north'
        elif (angle >= 0 and angle <= 45) or (angle >= 315 and angle <= 360):
            return 'east'
        elif angle >= 225 and angle <= 315:
            return 'south'
        elif angle >= 135 and angle <= 225:
            return 'west'
        else:
            return 'unknown'

    def getCubePoints(self, a):
        points = [[
                (int(self._center_x - a * 1.1), self._center_y), # left bottom
                (self._center_x, int(self._center_y + a / 2)), # mid bottom
                (int(self._center_x + a * 1.1), self._center_y), # right bottom
                (), #UNKONWN (behind bottom)
            ],
            [
                (int(self._center_x - a * 1.1), int(self._center_y - a * 1.5)), # left top
                (), # mid top (NOT CERTAIN) (self._center_x, self._center_y - a)
                (int(self._center_x + a * 1.1), int(self._center_y - a * 1.5)), # right top
                (self._center_x, self._center_y - a * 2), # top top
        ]]

        # image_dupe = self._img
        # for point in points:
        #     for p in point: 
        #         if p != ():
        #             p_with_offset = (p[0] + 5, p[1] + 5)
        #             cv2.circle(image_dupe, p_with_offset, 5, (0, 255, 0), -1)

        # cv2.imshow("frame", image_dupe)
        return points

    def getArrangement(self, points):
        order = []
        arrangement = []
        match (self._curr_direction):
            case 'north':
                order = [3, 0, 1, 2]
            case 'east':
                order = [2, 3, 0, 1]
            case 'south':
                order = [1, 2, 3, 0]
            case 'west':
                order = [0, 1, 2, 3]
        for i in range(0, 2):
            for j in order:
                arrangement.append(points[i][j])
        return arrangement

    def setCenterPoint(self):
        image = self._img

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 50, 200)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=20, minLineLength=50, maxLineGap=20)

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
            if point != () and self._curr_config[index] == "undefined":
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
        uart_config = self.convert_config_to_uart_format(configuration)
        self.send_message_to_micro(uart_config)
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
        print("UART Message to Micro: " + message)
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

    
    def read_uart(self):
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()
            return message
        return None

    def verify_config(self):
        self._config_completed =  not( "undefined" in self._curr_config.values())

    def send_config_to_server(self):
        configuration = {
            "time": str(datetime.now()),
            "config": self._curr_config
        }
        print(configuration)

        data = json.dumps(configuration)
        print(f"Requestbody sent to Server: {data}")
        response = requests.post(url + "/config", headers=headers, data=data)
        print(response)
        print(f"Response Content: {response.content}")


def send_end_signal_to_server():
    print("Send end signal to Server")
    response = requests.post(url + "/end", headers=headers)
    print(f"Response Content: {response.content}")

def send_start_signal_to_server():
    print("Send start signal to Server")
    response = requests.post(url + "/start", headers=headers)
    print(f"Response Content: {response.content}")

if __name__ == '__main__':
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip()
            print("Received message from UART:", data)
            if data == "start":
                print("Start Algorithm")
                send_start_signal_to_server()
                cube_calculator = CubeCalculator()
                cube_calculator.open_camera_profile('147.88.48.131', 'pren', '463997', 'pren_profile_med')
            if data == "done":
                print("Build is completed")
                send_end_signal_to_server()

