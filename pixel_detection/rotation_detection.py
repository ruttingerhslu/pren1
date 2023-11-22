import cv2
import numpy as np


def estimate_rotation_speed(video_path):
    cap = cv2.VideoCapture(video_path)

    prev_gray_area = None
    rotation_count = 0
    total_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Gray color range
        lower_gray = np.array([0, 0, 40])
        upper_gray = np.array([180, 40, 220])
        mask = cv2.inRange(hsv, lower_gray, upper_gray)

        # Find current gray area
        current_gray_area = np.sum(mask) / 255.0

        if prev_gray_area and current_gray_area < prev_gray_area:
            rotation_count += 1

        prev_gray_area = current_gray_area
        total_frames += 1

    cap.release()

    # Assuming video is 30 fps
    rpm = (rotation_count / total_frames) * 1800

    return rpm


video_path = "../resources/pren_cube_01.mp4"
print(f"Estimated RPM: {estimate_rotation_speed(video_path)}")
