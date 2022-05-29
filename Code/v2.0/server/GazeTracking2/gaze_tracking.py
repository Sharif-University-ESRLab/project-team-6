import cv2
import numpy as np
from picamera.array import PiRGBArray 
from picamera import PiCamera 
import time


class GazeDetector:
  class Directions:
    LEFT = "LEFT"
    RIGHT = "RIGHT"

  def __init__(
      self, 
      scale_factor: float = 1.1,
      min_neighbors: int = 70,
      pupil_blackness_threshold: float = 1.1
    ):
     self._eye_cascade_classifier: cv2.CascadeClassifier = cv2.CascadeClassifier("haarcascade_eye.xml")
     self.scale_factor = scale_factor
     self.min_neighbors = min_neighbors
     self.pupil_blackness_threshold = pupil_blackness_threshold
  
  def detect_eye_and_direction(self, face: np.ndarray):
    eyes = self._eye_cascade_classifier.detectMultiScale(face, scaleFactor=self.scale_factor, minNeighbors=self.min_neighbors)

    face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

    sum_of_dists = 0
    for idx, (eye_x, eye_y, eye_w, eye_h) in enumerate(eyes):
      if idx == 2:
        break;
      eye_rect = face_gray[eye_y+int(eye_h/3):eye_y+int(2*eye_h/3), eye_x:eye_x+eye_w]
      pupil_mask = (eye_rect < np.sort(eye_rect.flatten())[int(self.pupil_blackness_threshold*eye_rect.size)]).astype(int)
      _, y_arr_pupil = np.where(pupil_mask)
      y_median_pupil = np.median(y_arr_pupil)
      sum_of_dists += y_median_pupil - eye_rect.shape[1]//2

    return self.Directions.LEFT if sum_of_dists > 0 else self.Directions.RIGHT


class GazeTracking:
  def __init__(
      self,
      gaze_detector: GazeDetector, 
      print_logs: bool = True, 
      camera_width: int = 640, 
      camera_height: int = 480,
      camera_framerate: int = 32
    ):
    self._init_camera(camera_width, camera_height, camera_framerate)
    self._gaze_detector = gaze_detector
    self._print_logs = print_logs
  
  def _init_camera(self, camera_width: int, camera_height: int, camera_framerate: int):
    self._camera = PiCamera()
    self._camera.resolution = (camera_width, camera_height)
    self._camera.framerate = camera_framerate
    self.raw_capture = PiRGBArray(self._camera, size=(camera_width, camera_height))

  def get_eye_direction(self, time_to_capture: int):
      start_time = time.time()
      directions = {GazeDetector.Directions.LEFT: 0, GazeDetector.Directions.RIGHT: 0}
      
      for frame in self._camera.capture_continuous(self._raw_capture, format="bgr", use_video_port=True):
          image = frame.array
          direction = self._gaze_detector.detect_eye_and_direction(image)
          directions[direction] = directions[direction] + 1

          if self._print_logs:
            print("[GazeTracking LOG] Eye Direction:", direction)

          self._raw_capture.truncate(0)

          curr_time = time.time()
          if curr_time - start_time > time_to_capture:
              break
      
      answer = GazeDetector.Directions.LEFT 
      if directions[GazeDetector.Directions.LEFT] < directions[GazeDetector.Directions.RIGHT]:
        answer = GazeDetector.Directions.RIGHT 
      
      return answer, directions
