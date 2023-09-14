from time import time

from picamera2 import Picamera2, Preview
#import cv2

picam2 = Picamera2()
#picam2.start_preview(Preview.QT)

preview_config = picam2.create_preview_configuration()
capture_config = picam2.create_still_configuration()
picam2.configure(preview_config)

picam2.start()

start = time()
full_data_name = f"/home/clement/microscope_data/img/test.png"
picam2.switch_mode(capture_config)
array = picam2.capture_array("main")
picam2.switch_mode(preview_config)  
print(time() -start)

