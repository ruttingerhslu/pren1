import cv2
import numpy as np


found_orientations = []

def is_color_in_range(color, lower_bound, upper_bound):
    return np.all(lower_bound <= color) and np.all(color <= upper_bound)


# Main function to check the video for specific colors at pixel coordinates
def check_pixels_and_save_frame(cap, pixel_coords_dict, start_frame_number=0):
    print(start_frame_number)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return False, start_frame_number, None

    # Skip to the start time if provided
    if start_frame_number > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)

    if cap.get(cv2.CAP_PROP_FRAME_COUNT) <= start_frame_number:
        print("Error: Video is finished.")
        return False, start_frame_number, None

    frame_count = start_frame_number
    while True:
        success, frame = cap.read()
        if not success:
            cap.release()
            print('failed to read cap')
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_count += 1
        for position, coords in pixel_coords_dict.items():
            match = True
            for x, y, expected_color in coords:
                pixel_value = gray_frame[y, x]
                if expected_color == 'gray' and pixel_value < 80:
                    match = False
                    break
                elif expected_color == 'black' and pixel_value > 80:
                    match = False
                    break

            if match and not position in found_orientations:
                found_orientations.append(position)
                # Frame matched, save it and return information
                image_name = f'../resources/cubes2_gray_area_{position}_img.jpg'
                cv2.imwrite(image_name, frame)
                print(f"Match found at position {position} in frame {frame_count}.")
                print(f"Frame saved as {image_name}")
                cap.release()
                return True, frame_count, position

    # No match found, release the video capture
    cap.release()
    return False, start_frame_number, None
