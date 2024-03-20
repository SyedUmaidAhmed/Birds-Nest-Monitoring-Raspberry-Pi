import cv2
import os
import time

# Specify the custom output directory path
output_directory = r"/home/pi/birds"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Function to create a new video file
def create_new_video():
    global current_folder, out, frame_width, frame_height
    current_time = time.strftime("%H-%M-%S")
    output_path = os.path.join(current_folder, f'{current_time}.avi')
    out.release()  # Release the previous video writer
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (frame_width, frame_height))
    return output_path

# Create a folder for today's date
current_date = time.strftime("%Y-%m-%d")
current_folder = os.path.join(output_directory, current_date)
os.makedirs(current_folder, exist_ok=True)

# Initialize video capture from the Raspberry Pi camera
cap = cv2.VideoCapture(0,apiPreference=cv2.CAP_V4L2)
cap.set(3,640)
cap.set(4,480)

# Set up video recording parameters
frame_width = 640#int(cap.get(3))
frame_height = 480#int(cap.get(4))
output_path = os.path.join(current_folder, f'{time.strftime("%H-%M-%S")}.avi')
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (frame_width, frame_height))

# Timer for checking every 30 minutes
start_time = time.time()
elapsed_time = 0

# Record until interrupted
try:
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Get current date and time
        current_datetime = time.strftime("%Y-%m-%d %H:%M:%S")

        # Draw date and time onto the frame
        cv2.putText(frame, current_datetime, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        out.write(frame)

        #cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Check if 30 minutes have elapsed to create a new video file
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1800:  # 30 minutes (30 * 60 seconds)
            output_path = create_new_video()
            start_time = time.time()  # Reset start time

finally:
    # Release the camera and video writer
    cap.release()
    out.release()

    # Close OpenCV windows
    cv2.destroyAllWindows()
