import cv2
import numpy as np
import math

color_ranges = {
    "blue": (np.array([90, 100, 100]), np.array([135, 255, 255])),
    "yellow": (np.array([25, 100, 100]), np.array([35, 255, 255])),
    "red1": (np.array([0, 100, 100]), np.array([50, 255, 255])),
    "red2": (np.array([150, 100, 100]), np.array([180, 255, 255]))
}


class CubeCalculator:
    def __init__(self) -> None:
        self._img = None
        self._gray = np.array([0, 0, 0])
        self._center_x = 0
        self._center_y = 0
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
            angle = self.getMeanAngle()
            if (math.isclose(abs(angle) % 90, 0, abs_tol = 1) or math.isclose(angle, 0, abs_tol = 1)):
                # cv2.imshow('good angle', frame)
                # print(self.getDirection(angle))
                direction = self.getDirection(angle)
                points = self.getCubePoints()
                arrangement = self.getArrangement(direction, points)
                # print(arrangement)
                # cv2.imwrite('arrangement.png', self._img)
                config = self.getConfig(arrangement)
                # print(config)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def getMeanAngle(self):
        image = self._img

        lower_gray = np.array([180, 175, 170], dtype=np.uint8)
        upper_gray = np.array([240, 220, 220], dtype=np.uint8)

        mask_gray = cv2.inRange(image, lower_gray, upper_gray)
        contours, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        angles = []

        self._center_x = image.shape[1] // 2
        self._center_y = (image.shape[0] // 2) - 80
        # cv2.circle(image, (self._center_x, self._center_y), 5, (0, 255, 0), -1)

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
                    # cv2.line(image, (centroid_x, centroid_y), (self._center_x, self._center_y), (255, 0, 0), 1)
        mean_angle = np.mean(angles)
        # cv2.putText(image, str(mean_angle), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        return mean_angle

    def getDirection(self, angle):
        if angle < 0:
            angle += 360

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
        image = self._img
        a = 90

        points = [[
                (self._center_x - a, self._center_y), # left bottom
                (self._center_x, int(self._center_y + a/2)), # mid bottom
                (self._center_x + a, self._center_y), # right bottom
                (), #UNKONWN (behind bottom)
            ],
            [
                (self._center_x - a, self._center_y - a), # left top
                (self._center_x, self._center_y - a), # mid top (NOT CERTAIN)
                (self._center_x + a, self._center_y - a), # right top
                (self._center_x, self._center_y - 2*a), # top top
        ]]

        # for layer in points:
        #     for point in layer:
        #         cv2.circle(image, point, 5, (0, 255, 0), -1)
        return points
        # cv2.imshow('test', image)

    def getArrangement(self, orientation, points):
        order = []
        arrangement = []
        match (orientation):
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

    def getConfig(self, arrangement):
        image = self._img
        config = {}
        for index, point in enumerate(arrangement):
            if point:
                index += 1 # config starts at 1
                config.update({ index : self.mapColor(point) })
                cv2.circle(image, tuple(point), 5, (0, 255, 0), -1)
                cv2.putText(image, str(index), tuple(point), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        cv2.imshow('img', image)
        return config
    
    def mapColor(self, point):
        image = self._img
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        hsv_point = hsv_img[tuple(reversed(point))]     

        for color, (lower, upper) in color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            if np.all(hsv_point >= lower) and np.all(hsv_point <= upper):
                return color
        return "Unknown"


if __name__ == '__main__':
    CubeCalculator()