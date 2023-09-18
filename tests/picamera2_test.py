from time import time, sleep
from PIL import Image 

from picamera2 import Picamera2, Preview
#import cv2
#picam2.start_preview(Preview.QT)

from threading import Thread, Event


picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (1400,1080)}, lores={"size": (800, 620), "format": "YUV420"}, display= "lores", buffer_count=4)
picam2.configure(config)
print(picam2.sensor_modes)
