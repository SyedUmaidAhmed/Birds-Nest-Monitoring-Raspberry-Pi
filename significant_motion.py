import cv2
import os
import time
import numpy as np

# Specify the custom output directory path
output_directory = "/media/pi/Birds"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Define the coordinates of the rectangular region of interest (ROI)
roi_x = 224  # X-coordinate of the top-left corner of the ROI
roi_y = 132  # Y-coordinate of the top-left corner of the ROI
roi_width = 286  # Width of the ROI
roi_height = 271  # Height of the ROI

# Create a background subtractor for motion detection
fgbg = cv2.createBackgroundSubtractorMOG2()

# Motion detection function within the ROI
def detect_motion(frame):
    roi = frame[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
    fgmask = fgbg.apply(roi)

    # Further process the mask to reduce false positives
    fgmask = cv2.medianBlur(fgmask, 5)  # Apply median blur to remove small noise
    _, fgmask = cv2.threshold(fgmask, 128, 255, cv2.THRESH_BINARY)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any significant contours exist within the ROI
    motion_detected = False
    for contour in contours:
        if cv2.contourArea(contour) > 300:  # Adjust the area threshold as needed
            motion_detected = True
            break
    
    return motion_detected

recording = False  # Track recording state
out = None

motion_detected = False  # Track motion detection state
motion_start_time = None  # Timestamp when motion started
motion_timeout = 10.0  # Duration in seconds to continue recording after motion stops

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

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if detect_motion(frame):
            motion_detected = True

            if not recording:
                # Start recording
                output_path = os.path.join(current_folder, f'{time.strftime("%H-%M-%S")}.avi')
                out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (frame_width, frame_height))
                recording = True
                motion_start_time = time.time()
        elif recording and motion_detected:
            # If motion was detected before, continue recording a few frames after motion stops
            out.write(frame)

            if time.time() - motion_start_time > motion_timeout:
                # Stop recording after the specified timeout
                recording = False
                out.release()
                out = None
                motion_detected = False

        if recording:
            out.write(frame)

        # Draw the ROI rectangle on the frame for visualization
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

    # Stop recording if motion was detected
    if recording:
        out.release()
        out = None

cv2.destroyAllWindows()
