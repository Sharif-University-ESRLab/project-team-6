"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""
from picamera.array import PiRGBArray # Generates a 3D RGB array
from picamera import PiCamera # Provides a Python interface for the RPi Camera Module
import time
import cv2
from gaze_tracking import GazeTracking

gaze = GazeTracking()
# webcam = cv2.VideoCapture(0)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
raw_capture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

def get_eye_direction(t: int):
    start_time = time.time()
    directions = dict()
    
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        # We get a new frame from the webcam
        # _, frame = webcam.read()
        image = frame.array

        # We send this frame to GazeTracking to analyze it
        # gaze.refresh(frame)
        gaze.refresh(image)

        frame = gaze.annotated_frame()
        text = ""

        if gaze.is_right():
            text = "Looking right"
        elif gaze.is_left():
            text = "Looking left"
        elif gaze.is_center():
            text = "Looking center"

        if len(text) > 0:
            directions[text] = directions.get(text, 0) + 1
            print("Direction:", text)

        # cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        
        print("Pupils' locations:", left_pupil, right_pupil)

        # cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        # cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        # cv2.imshow("Demo", frame)

        # addr = 'log/frame_' + str(r) + '.jpg'
        # cv2.imwrite(addr, frame)

        # if cv2.waitKey(1) == 27:
        #     break

        raw_capture.truncate(0)

        curr_time = time.time()

        if curr_time - start_time > t:
            break
    
    answer = "Looking right"
    
    if directions.get("Looking left", 0) > directions.get(answer, 0):
        answer = "Looking left"
    
    if directions.get("Looking center", 0) > directions.get(answer, 0):
        answer = "Looking center"

    return answer, directions

