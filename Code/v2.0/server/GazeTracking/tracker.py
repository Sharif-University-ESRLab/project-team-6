from picamera.array import PiRGBArray 
from picamera import PiCamera 
import time
import cv2
from .gaze_tracking import GazeTracking

gaze = GazeTracking()

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
raw_capture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

def get_eye_direction(t: int):
    start_time = time.time()
    directions = dict()
    
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        image = frame.array

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

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        
        print("Pupils' locations:", left_pupil, right_pupil)

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
