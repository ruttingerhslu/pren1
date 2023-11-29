import cv2
import numpy as np

def is_color_in_range(color, lower_bound, upper_bound):
    return np.all(lower_bound <= color) and np.all(color <= upper_bound)


def get_frame_time(cap, frame_count):
    # Get the frame rate
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Calculate the timestamp
    timestamp = frame_count / fps
    return timestamp


# Main function to check the video for specific colors at pixel coordinates
def check_pixels_and_save_frame(cap, pixel_coords_dict, lower_gray, upper_gray, start_time=0):
    print(start_time)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return False, start_time, None

    # Skip to the start time if provided
    if start_time > 0:
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time*100)  # Convert to milliseconds

    # Define the black color range in HSV
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])  # Adjust the upper HSV values for black as needed

    frame_count = 0
    while True:
        success, frame = cap.read()
        if not success:
            cap.release()
            print('failed to read cap')
            break

        frame_count += 1
        for position, coords in pixel_coords_dict.items():
            match = True
            print(frame_count)
            for x, y, expected_color in coords:
                pixel_hsv = cv2.cvtColor(frame[y:y+1, x:x+1], cv2.COLOR_BGR2HSV)[0][0]

                if expected_color == 'gray' and not is_color_in_range(pixel_hsv, lower_gray, upper_gray):
                    match = False
                    break
                elif expected_color == 'black' and not is_color_in_range(pixel_hsv, lower_black, upper_black):
                    match = False
                    break

            if match:
                # Frame matched, save it and return information
                frame_time_millis = cap.get(cv2.CAP_PROP_POS_MSEC)
                image_name = f'../resources/cubes_gray_area_{position}_img.jpg'
                cv2.imwrite(image_name, frame)
                print(f"Match found at position {position} in frame {frame_count}.")
                print(f"Frame saved as {image_name}")
                cap.release()
                return True, frame_time_millis, position

    # No match found, release the video capture
    cap.release()
    return False, start_time, None

