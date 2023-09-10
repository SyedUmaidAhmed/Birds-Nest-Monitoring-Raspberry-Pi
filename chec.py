import cv2
import os
import time

# Specify the custom output directory path
output_directory = r"C:\COW_WORK_EMBEDDINGS"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

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
    output_path = os.path.join(current_folder, f'{time.strftime("%H-%M-%S")}.avi')
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (frame_width, frame_height))

    # Create a background subtractor for motion detection
    fgbg = cv2.createBackgroundSubtractorMOG2()

    # Motion detection function
    def detect_motion(frame):
        fgmask = fgbg.apply(frame)
        print(cv2.countNonZero(fgmask))
        return cv2.countNonZero(fgmask) > 1600  # Adjust the threshold as needed

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        motion_detected = detect_motion(frame)

        if motion_detected:
            out.write(frame)

        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

