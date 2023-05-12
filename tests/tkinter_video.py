
import picamera
import picamera.array
import time
import cv2
import tkinter 
from PIL import Image, ImageTk
import sys


def capturePiCam():
    with picamera.PiCamera() as camera:
        cap=picamera.array.PiRGBArray(camera)
        camera.resolution = (640, 480)
        camera.start_preview()
        time.sleep(3)
        camera.capture(cap,format="bgr")
        global img
        img =cap.array

#- display on Tkinter -
def displayAtThinter():
    root = tkinter.Tk() 
    b,g,r = cv2.split(img) 
    img2 = cv2.merge((r,g,b))
    img2FromArray = Image.fromarray(img2)
    imgtk = ImageTk.PhotoImage(image=img2FromArray) 
    kinter.Label(root, image=imgtk).pack() 
    root.mainloop()

capturePiCam()
displayAtThinter()