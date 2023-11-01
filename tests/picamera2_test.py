from time import time, sleep
from PIL import Image 

from picamera2 import Picamera2, Preview
#import cv2
#picam2.start_preview(Preview.QT)

from threading import Thread, Event
import time


picam2 = Picamera2()
config = picam2.create_preview_configuration(raw={"size": picam2.sensor_resolution})
picam2.configure(config)

raw = picam2.capture_array("raw")
time.sleep(2)

print(raw.shape)
print(picam2.stream_configuration("raw"))
