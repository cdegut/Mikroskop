'''
Deprecated file, using the old Picamera instead of picamera 2
'''
from .parametersIO import create_folder
from time import sleep
from threading import Thread, Event
from .microscope_param import awbR_fluo, awbB_fluo, awbR_white, awbB_white
#import picamera
import picamera.array
import numpy as np
import cv2
from PIL import Image
import io


camera_full_resolution = (4056,3040)
camera_max_resolution = (3000, 2248)
h264_max_resolution = (1664,1248)


def previewPiCam(camera): #show preview directly as screen overlay
    camera.preview_fullscreen=False
    camera.preview_window=(0,25, 800, 625)
    camera.resolution=(camera_max_resolution)
    camera.video_stabilization=True
    camera.iso = 200
    camera.brightness = 50
    camera.exposure_compensation = 0
    camera.start_preview()
    camera.vflip = True
    camera.hflip = True


def change_zoom(camera, value):
    ##Centered zoom
    position_scale = (1 - value)/2

    ###Scale the resolution according to the zoom
    new_resolution = (int(value*camera_full_resolution[0]),int(value*camera_full_resolution[1]))

    camera.resolution=(new_resolution)
    camera.zoom=(position_scale,position_scale, value, value)


def save_image(camera, picture_name, data_dir):
    create_folder(data_dir + "img/")

    full_data_name = data_dir + "img/"  + picture_name 
    save = Thread(target = save_img_thread, args=(camera, full_data_name))
    save.start()

def awb_preset(camera, awb):
    if awb == "Green Fluo":
        camera.awb_mode = 'off'
        camera.awb_gains = (awbR_fluo, awbB_fluo)
        camera.contrast = 10
    if awb == "auto":
        camera.awb_mode = "auto"
    if awb == "white":
        camera.awb_mode = 'off'
        camera.awb_gains = (awbR_white, awbB_white)
        camera.contrast = 10 

def save_img_thread(camera, name):

    ## get the size of the image rounded to 32x16
    image_w = camera.resolution[0]
    if image_w%32 != 0:
        image_w = image_w + 32 - image_w%32
    image_h = camera.resolution[1]
    if image_h%16 != 0:
        image_h = image_h + 16 - image_h%16 
    
    stream = io.BytesIO()
    #start = time.time()
    camera.capture(stream, format='bgr')
    # I have got this code from picamera array.py :                                                                                                                                         
    # class PiRGBArray(PiArrayOutput):                                                                                                                                          
    # Produces a 3-dimensional RGB array from an RGB capture.                                                                                                                   
    # Round a (width, height) tuple up to the nearest multiple of 32 horizontally                                                                                               
    # and 16 vertically (as this is what the Pi's camera module does for                                                                                                        
    # unencoded output).                                                                                                                                                        
    width, height = camera.resolution
    fwidth = (width + 31) // 32 * 32
    fheight = (height + 15) // 16 * 16
    #if len(stream.getvalue()) != (fwidth * fheight * 3):
    #    raise PiCameraValueError('Incorrect buffer length for resolution %dx%d' % (width, height))
    image= np.frombuffer(stream.getvalue(), dtype=np.uint8).\
        reshape((fheight, fwidth, 3))[:height, :width, :]
    cv2.imwrite(f'{name}.png',image)
   
    ###
    #output = picamera.array.PiRGBArray(camera)
    #camera.capture(output, 'rgb')
    #print(output)
    #print('Captured %dx%d image' % (output.array.shape[1], output.array.shape[0]))
    #output.array.
    ###
    #output = output.reshape((image_h, image_w, 3))
    #image = Image.fromarray(output)
    #image.save(name + ".png",)
    #cv2.imwrite(name + ".png", output)
    
    #image = np.empty((image_w * image_h * 3,), dtype=np.uint8)
    #camera.capture(image, "bgr")
    #image = image.reshape((image_h, image_w, 3))
    #cv2.imwrite(name + ".png", image)

class VideoRecorder(Thread):
    def __init__(self,camera, video_quality, video_name,event_rec_on):
        Thread.__init__(self)
        self.camera = camera
        self.video_name = video_name
        self.event = event_rec_on
        self.video_quality = video_quality

    def run(self):
        ## Save the current preview settings
        preview_resolution = self.camera.resolution

        ## If the video quality demanded is higher than the preview, get back to the preview (avoided useless oversampling of zoomed in video)
        if preview_resolution[0] < self.video_quality:          
            record_resolution = preview_resolution
        
        ## else set the camera to the new resolution
        else:
            record_resolution = (self.video_quality, 
                int((self.video_quality)*(camera_full_resolution[1]/camera_full_resolution[0])))

        #### Change resolution if incompatible with the video
        if record_resolution[0] > h264_max_resolution[0]:
            record_resolution = h264_max_resolution
        
        #### Set the resolution
        self.camera.resolution = record_resolution

        ### Start recording and wait for stop button
        self.camera.start_recording(self.video_name)
        while not self.event.is_set():
            sleep(0.1)

        ### Stop recording
        self.camera.stop_recording()

        ### put back the former resolution setting
        if preview_resolution != self.camera.resolution:
            self.camera.resolution=preview_resolution


##### Function that generate the worker and pass the information to it
def start_recording(camera, data_dir, video_quality=320, video_name="test"):
    """Start a recording worker as a separate thread

    Args:
        camera (Pi.camera object): _description_
        data_dir (str): data directory 
        video_quality (int, optional): image heigh. Defaults to 320.
        video_name (str, optional): video name. Defaults to "test".

    Returns:
        VideoRecorder, Event: the video recorder object, and the event to stop it
    """
    create_folder(data_dir + "rec/")
    data_name = data_dir + "rec/" + video_name + ".h264"
    rec_off = Event()
    rec = VideoRecorder(camera, video_quality, data_name, rec_off)
    rec.start()

    return rec , rec_off ## return the worker and the event to stop the recording

def stop_video(off_event):
    off_event.set()


if __name__ == "__main__":
    import picamera
    from RPi import GPIO
    from os import environ

    from modules.cameracontrol import previewPiCam
    from modules.microscope import Microscope
    from modules.position_grid import PositionsGrid
    from modules.physical_controller import encoder_read, controller_startup
    from modules.interface.main_menu import *
    from modules.microscope_param import *
    from modules.parametersIO import ParametersSets
    from time import sleep


    ### Object for microscope to run
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin, parameters)
    grid = PositionsGrid(microscope, parameters)
    camera = picamera.PiCamera()

    
    #start picamPreview
    previewPiCam(camera)
    sleep(1)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.drc_strength = 'off'
    awb_preset(camera, "Green Fluo")


    while True:
        print("1 AWB \n2 Shutter \n3 Brightness \n4 ISO \n5 Contrast \n6 Analog Gain\n7 Save Image")
        setting_choice = input("Seting:")
       
        if setting_choice == "1":
            camera.awb_mode = 'off'
            blue_input = input("AWB_blue: ")
            red_input = input("AWB_red: ")
            camera.awb_gains = (float(red_input), float(blue_input))

        if setting_choice == "2":        
            shutter_input = input("Shutter_speed: ")
            camera.shutter_speed = (int(shutter_input))
        
        if setting_choice == "3":     
            bright_input = input("Brightness: ")
            camera.brightness = int(bright_input)

        if setting_choice == "4": 
            iso_input = input("Iso: ")
            camera.iso = int(iso_input)
        
        if setting_choice == "5": 
            text_input = input("Contrast -100 to 100:")
            camera.contrast = int(text_input)
        
        if setting_choice == "6": 
            text_input = input("Analog Gain:")
            print(camera.analog_gain)
            camera.analog_gain = int(text_input)
        
        if setting_choice == "7": 
            text_input = input("Save")
            save_img_thread(camera, "/home/pi/microscope_data/img/test_img" )
        



    #GPIO cleanup
    GPIO.cleanup()