import cv2
import numpy as np

def getFrame(file):
    cap = cv2.VideoCapture(file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 1000)
    success, image = cap.read()
    if success:
        return image


def edge_detection(frame):
    # gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(frame, (3, 3), 0)
    canny = cv2.Canny(blurred, 20, 40)
    kernel = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(canny, kernel, iterations=2)
    return dilated

def find_contours(edges):
    image = edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over the contours to find cubes
    for contour in contours:
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        print(approx)

        # Check if the detected shape has 4 corners (a square or rectangle)
        if len(approx) >= 4:
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)  # Draw the contour
    return image


frame = getFrame('../resources/pren_cube_03.mp4')
gray1 = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
edge_detect1 = edge_detection(gray1)
edge_detect2 = edge_detection(gray2)

cv2.imwrite("img.jpg", frame)

cv2.imwrite("edges1.jpg", edge_detect1)
cv2.imwrite("edges2.jpg", edge_detect2)
edge_detect = cv2.addWeighted(edge_detect1,1,edge_detect2,1,0)
cv2.imwrite("edges.jpg", edge_detect)
cv2.imwrite("contours.jpg", find_contours(edge_detect))

cv2.imwrite("gray.jpg", cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))