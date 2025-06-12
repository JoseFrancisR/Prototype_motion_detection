import cv2
import time
import serial
import imutils

ARDUINO_PORT = 'COM3'  
NO_MOTION_COUNTDOWN = 10
THRESHOLD_SUM_LIMIT = 300000  
CAMERA_SOURCE = "http://192.168.1.17:4747/video"  

cap = cv2.VideoCapture(CAMERA_SOURCE)
arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
time.sleep(2)

motion_detected = True
countdown_start_time = None
alarm_mode = False
alarm_counter = 0
start_frame = None

def send_command_to_arduino(cmd):
    arduino.write(cmd.encode())
    if cmd:
        print(f"Commanding the arduino to turn on")
    else:
        print(f"Commanding the arduino to turn off")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    frame = imutils.resize(frame, width=500)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if alarm_mode:
        if start_frame is None:
            start_frame = blurred_frame.copy()
            continue

        diff = cv2.absdiff(start_frame, blurred_frame)
        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        threshold_sum = thresh.sum()
        cv2.imshow("Motion", thresh)

        start_frame = blurred_frame.copy()

        # When there is detected motion 
        if threshold_sum > THRESHOLD_SUM_LIMIT:
            motion_detected = True
            countdown_start_time = None
            send_command_to_arduino('1') 
        else:
            # When theres no detected motion 
            if motion_detected and countdown_start_time is None:
                countdown_start_time = time.time()
                print("No motion detected. Starting countdown...")

            if countdown_start_time:
                elapsed = time.time() - countdown_start_time
                remaining = NO_MOTION_COUNTDOWN - elapsed
                print(f"No motion for {int(elapsed)}s, {int(remaining)}s left...")

                if elapsed >= NO_MOTION_COUNTDOWN:
                    motion_detected = False
                    print("No motion detected. Turning off light.")
                    send_command_to_arduino('0')  
                    countdown_start_time = None

    cv2.imshow("Camera", frame)

    key = cv2.waitKey(30) & 0xFF
    if key == ord('t'):
        alarm_mode = not alarm_mode
        motion_detected = True
        start_frame = None
        countdown_start_time = None
        print("Detection mode: ON" if alarm_mode else "Detection mode: OFF")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
