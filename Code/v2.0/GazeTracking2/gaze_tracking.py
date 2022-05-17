import cv2
import matplotlib.pyplot as plt
import math
import numpy as np
from picamera.array import PiRGBArray # Generates a 3D RGB array
from picamera import PiCamera # Provides a Python interface for the RPi Camera Module
import time


eye_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")


def detect_eye_and_direction(face):
  eyes = eye_cascade.detectMultiScale(face, scaleFactor=1.1, minNeighbors=70)

  face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

  sum_of_dists = 0
  
  for idx, (ex,ey,ew,eh) in enumerate(eyes):
    if idx == 2:
      break;

    eye_rect = face_gray[ey+int(eh/3):ey+int(2*eh/3), ex:ex+ew]
    
    pupil_mask = (eye_rect < np.sort(eye_rect.flatten())[int(0.1*eye_rect.size)]).astype(int)

    _, y_arr_pupil = np.where(pupil_mask)
    y_median_pupil = np.median(y_arr_pupil)

    sum_of_dists += y_median_pupil - eye_rect.shape[1]//2

  return "LEFT" if sum_of_dists > 0 else "RIGHT"



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

        dir = detect_eye_and_direction(image)
        directions[dir] = directions.get(dir, 0) + 1

        print("Eye Direction:", dir)

        raw_capture.truncate(0)

        curr_time = time.time()

        if curr_time - start_time > t:
            break
    
    answer = "RIGHT"
    
    if directions.get("LEFT", 0) > directions.get(answer, 0):
        answer = "LEFT"
    
    return answer, directions
