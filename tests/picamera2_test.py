from time import time, sleep
from PIL import Image 

from picamera2 import Picamera2, Preview
#import cv2
#picam2.start_preview(Preview.QT)
from modules.cameracontrol import Microscope_camera

from threading import Thread, Event
import time

micro_cam = Microscope_camera()
micro_cam.initialise()  