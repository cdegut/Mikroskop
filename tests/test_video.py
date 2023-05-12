# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from smbus2 import SMBus
import tkinter as tk

# address for I2C
addr = 0x8 # bus address

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    # show the frame
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop

    if key == ord("q"):
        with SMBus(1) as bus:
            destination = int(1000)
            destination_as_bytes = (destination).to_bytes(4, byteorder='big', signed=False)
            bus.write_i2c_block_data(addr, 2, destination_as_bytes)

    if key == ord("z"):
        with SMBus(1) as bus:
            destination = int(29000)
            destination_as_bytes = (destination).to_bytes(4, byteorder='big', signed=False)
            bus.write_i2c_block_data(addr, 2, destination_as_bytes)'''