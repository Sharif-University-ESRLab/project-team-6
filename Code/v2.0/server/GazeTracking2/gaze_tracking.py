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
      pupil_blackness_threshold: float = 0.1
    ):
     self._eye_cascade_classifier = cv2.CascadeClassifier("GazeTracking2/haarcascade_eye.xml")
     self.scale_factor = scale_factor
     self.min_neighbors = min_neighbors
     self.pupil_blackness_threshold = pupil_blackness_threshold # Threshold used for detecting pupils
  
  def detect_eye_and_direction(self, face: np.ndarray):
    # Detecting eyes using cv2.CascadeClassifier and haarcascade_eye.xml
    eyes = self._eye_cascade_classifier.detectMultiScale(face, scaleFactor=self.scale_factor, minNeighbors=self.min_neighbors)

    face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) # Convert RGB image to Black-and-White image

    sum_of_dists = 0
    for idx, (eye_x, eye_y, eye_w, eye_h) in enumerate(eyes):
      if idx == 2: # We don't have more than 2 eyes!
        break;
      eye_rect = face_gray[eye_y+int(eye_h/3):eye_y+int(2*eye_h/3), eye_x:eye_x+eye_w] # Fit the rectangle to the eyes vertically
      pupil_mask = (eye_rect < np.sort(eye_rect.flatten())[int(self.pupil_blackness_threshold*eye_rect.size)]).astype(int) # 0/1 mask 
      _, y_arr_pupil = np.where(pupil_mask) # Coordinates of the pixels of the eye
      y_median_pupil = np.median(y_arr_pupil) # Median of the pixels
      sum_of_dists += y_median_pupil - eye_rect.shape[1]//2 # Distance of the pixels from median

    return self.Directions.LEFT if sum_of_dists > 0 else self.Directions.RIGHT # Decide the direction of the eye based on the distances


class GazeTracking:
  def __init__(
      self,
      gaze_detector: GazeDetector, 
      print_logs: bool = True, 
      camera_width: int = 640, 
      camera_height: int = 480,
      camera_framerate: int = 32
    ):
    """
      Parameters:
        gaze_detector (GazeDetector): A GazeDetector instance used for detecting eyes
        print_logs (bool): A boolean variable used to enable logging
        camera_width (int): Camera width use for camera initialization
        camera_height (int): Camera heigth use for camera initialization
        camera_framerate (int): Camera frame rate use for camera initialization
    """
    self._init_camera(camera_width, camera_height, camera_framerate)
    self._gaze_detector = gaze_detector
    self._print_logs = print_logs
  
  def _init_camera(self, camera_width: int, camera_height: int, camera_framerate: int):
    """
      Initiates PiCamera

      Parameters:
        camera_width (int): Capturing image width
        camera_height (int): Capturing image height
        camera_framerate (int): Camera's frame rate
    """
    self._camera = PiCamera()
    self._camera.resolution = (camera_width, camera_height)
    self._camera.framerate = camera_framerate
    self._raw_capture = PiRGBArray(self._camera, size=(camera_width, camera_height))

  def get_eye_direction(self, time_to_capture: int):
      start_time = time.time()
      directions = {GazeDetector.Directions.LEFT: 0, GazeDetector.Directions.RIGHT: 0} # Dict for counting estimations
      
      for frame in self._camera.capture_continuous(self._raw_capture, format="bgr", use_video_port=True):
          image = frame.array
          direction = self._gaze_detector.detect_eye_and_direction(image) # Detect direction using GazeDetector
          directions[direction] = directions[direction] + 1 # Update dict of estimations

          if self._print_logs: # When logging is enabled
            print("[GazeTracking LOG] Eye Direction:", direction)

          self._raw_capture.truncate(0)

          curr_time = time.time()
          if curr_time - start_time > time_to_capture: # Stop if exec. time is greater than time_to_capture
              break
      
      # Majority vote
      answer = GazeDetector.Directions.LEFT 
      if directions[GazeDetector.Directions.LEFT] < directions[GazeDetector.Directions.RIGHT]:
        answer = GazeDetector.Directions.RIGHT 
      
      return answer, directions
