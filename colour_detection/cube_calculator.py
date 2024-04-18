import cv2
import numpy as np
import math

directions = {
    "north": (30, 120),
    "east": ((0, 30), (330, 360)),
    "south": (210, 300),
    "west": (150, 240)
}

class CubeCalculator:
    def __init__(self) -> None:
        self._img = None
        self._gray = np.array([0, 0, 0])
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
            if (math.isclose(abs(angle) % 90, 0, abs_tol = 1) ):
                cv2.imshow('good angle', frame)
                print(self.getDirection(angle))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def getMeanAngle(self):
        image = self._img

        lower_gray = np.array([180, 175, 170], dtype=np.uint8)
        upper_gray = np.array([240, 220, 200], dtype=np.uint8)

        mask_gray = cv2.inRange(image, lower_gray, upper_gray)
        contours, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        angles = []

        image_center_x = image.shape[1] // 2
        image_center_y = (image.shape[0] // 2) - 80
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
        mean_angle = np.mean(angles)
        # cv2.putText(image, str(mean_angle), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        return mean_angle


    def getDirection(self, angle):
        if angle < 0:
            angle += 360
        for direction, angle_range in directions.items():
            if isinstance(angle_range[0], tuple):
                if (angle >= angle_range[0][0] and angle <= angle_range[0][1]) or \
                    (angle >= angle_range[1][0] and angle <= angle_range[1][1]):
                    return direction
            else:
                if angle >= angle_range[0] and angle <= angle_range[1]:
                    return direction
        return "Unknown"

if __name__ == '__main__':
    CubeCalculator()