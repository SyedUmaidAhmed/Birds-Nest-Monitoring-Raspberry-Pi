import cv2
import os
import time
import numpy as np

# Specify the custom output directory path
output_directory = "/media/pi/Birds"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Define the coordinates of the rectangular region of interest (ROI)
roi_x = 100  # X-coordinate of the top-left corner of the ROI
roi_y = 100  # Y-coordinate of the top-left corner of the ROI
roi_width = 200  # Width of the ROI
roi_height = 200  # Height of the ROI

# Create a background subtractor for motion detection
fgbg = cv2.createBackgroundSubtractorMOG2()

# Motion detection function within the ROI
def detect_motion(frame):
    roi = frame[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
    fgmask = fgbg.apply(roi)
    return cv2.countNonZero(fgmask) > 1600  # Adjust the threshold as needed

recording = False  # Track recording state
out = None

while True:
    # Create a folder for today's date
    current_date = time.strftime("%Y-%m-%d")
    current_folder = os.path.join(output_directory, current_date)
    os.makedirs(current_folder, exist_ok=True)

    # Initialize video capture from the Raspberry Pi camera
    cap = cv2.VideoCapture(0)

    # Set up video recording parameters
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    motion_detected = False  # Track motion detection state

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if detect_motion(frame):
            motion_detected = True

            # Start recording
            if out is None:
                output_path = os.path.join(current_folder, f'{time.strftime("%H-%M-%S")}.avi')
                out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (frame_width, frame_height))
        elif motion_detected:
            # If motion was detected before, continue recording a few frames
            recording = True

        if recording:
            out.write(frame)

        # Draw the ROI rectangle on the frame for visualization
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

    # Stop recording
    if out is not None:
        out.release()
        out = None

cv2.destroyAllWindows()
