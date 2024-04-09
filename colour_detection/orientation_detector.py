import cv2
import numpy as np

def getFrame(file):
    cap = cv2.VideoCapture(file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 1500)
    success, image = cap.read()
    if success:
        return image

image = getFrame('../resources/pren_cube_01.mp4')

lower_gray = np.array([150, 150, 150], dtype=np.uint8)
upper_gray = np.array([255, 255, 255], dtype=np.uint8)

mask_gray = cv2.inRange(image, lower_gray, upper_gray)

contours, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cv2.imwrite('test.png', mask_gray)

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
            print(angle_deg)
            angles.append(angle_deg)
            cv2.line(image, (centroid_x, centroid_y), (image_center_x, image_center_y), (255, 0, 0), 1)

cv2.imwrite('output.png', image)

mean_angle = np.mean(angles)
print("Mean Angle:", mean_angle)
