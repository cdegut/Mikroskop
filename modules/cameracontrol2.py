from .parametersIO import create_folder
from time import sleep, time
from threading import Thread, Event
from .microscope_param import awbR_fluo, awbB_fluo, awbR_white, awbB_white
from picamera2 import Preview
from libcamera import Transform
import picamera.array
import numpy as np
from PIL import Image
import io
from time import time


camera_full_resolution = (4056,3040)
camera_max_resolution = (3000, 2248)
h264_max_resolution = (1664,1248)

def camera_get_config(picam2, value = "general"):
    if value == "general":
        camera_config = picam2.create_preview_configuration(main={"size":  (1400, 1080)}, lores={"size": (800, 620), "format": "YUV420"}, display= "lores", buffer_count=4)
    if value == "full":
        camera_config = picam2.create_preview_configuration(main={"size":  (4056,3040)}, lores={"size": (400, 310), "format": "YUV420"}, display= "lores", buffer_count=1)
    return camera_config


def preview_picam(picam2, external=False): 
    picam2.configure(camera_get_config(picam2, "general"))
    if not external:
        picam2.start_preview(Preview.QTGL, x=0 , y=25, width=800, height=625)
    else:
        picam2.start_preview(Preview.QT, width=80, height=60) 

    Transform(hflip=1, vflip = 1)

    picam2.start()
    picam2.title_fields = ['FocusFoM']

def change_zoom(picam2, crop_factor, animation = True):
    ### zoom value is a crop factor
    full_res = picam2.camera_properties['PixelArraySize']
    
    if not animation:
        crop = [int(crop_factor*full_res[0]),int(crop_factor*full_res[1])]
        offset = [(full_res[0] - crop[0]) // 2 , (full_res[1] - crop[1]) // 2 , ]
        picam2.set_controls({"ScalerCrop": offset  + crop})
        return

    old_crop_factor = picam2.capture_metadata()['ScalerCrop'][2] / full_res[0]
    zoom_step = (crop_factor - old_crop_factor) / 20 

    for i in range(20):
        picam2.capture_metadata()
        value = old_crop_factor + (i * zoom_step)
        crop = [int(value*full_res[0]),int(value*full_res[1])]
        offset = [(full_res[0] - crop[0]) // 2 , (full_res[1] - crop[1]) // 2 , ]
        picam2.set_controls({"ScalerCrop": offset  + crop})
        
    crop = [int(crop_factor*full_res[0]),int(crop_factor*full_res[1])]
    offset = [(full_res[0] - crop[0]) // 2 , (full_res[1] - crop[1]) // 2 , ]
    picam2.set_controls({"ScalerCrop": offset  + crop})


def save_image(picam2, picture_name, data_dir, full_res = False):
    create_folder(data_dir + "img/")
    full_data_name = f"{data_dir}/{picture_name}.png"
    
    if full_res:
        picam2.switch_mode(camera_get_config(picam2, "full"))

    capture = picam2.capture_image("main")

    if full_res:
        picam2.switch_mode(camera_get_config(picam2, "general"))
    
    save = Thread(target = save_img_thread, args=(capture, full_data_name))
    save.start()

def save_image_time_lapse(picam2, picture_name, data_dir, microscope, led, ledpwr, flash = True):
    
    create_folder(data_dir + "img/")
    full_data_name = f"{data_dir}/{picture_name}.png"
    
    capture = picam2.capture_image("main")
    
    save = Thread(target = save_img_thread, args=(capture, full_data_name))
    save.start()

def save_image_back(picam2, picture_name, data_dir, full_res = False, microscope = None, led = None, ledpwr = None):
    create_folder(data_dir + "img/")
    full_data_name = f"{data_dir}/{picture_name}.png"
    capture_config = picam2.create_still_configuration()
    
    if full_res:
        picam2.switch_mode(picam2, capture_config("full"))
    
    if microscope and led and ledpwr:
        microscope.set_led_state(led)
        microscope.set_ledpwr(ledpwr)

    capture = picam2.capture_image("main")
    
    if microscope and led and ledpwr:
        microscope.set_led_state(0)
        
    if full_res:
        picam2.switch_mode(picam2, capture_config("general"))
    
    save = Thread(target = save_img_thread, args=(capture, full_data_name))
    save.start()

def save_img_thread(capture, full_data_name):

    capture.save(full_data_name, format = "png" )

def awb_preset(picam2, awb):
    if awb == "Green Fluo":
        picam2.controls.AwbEnable = False
        picam2.controls.ColourGains = awbR_fluo,  awbB_fluo
        #camera.controls.Contrast = 10
    if awb == "auto":
        picam2.controls.AwbEnable = True
    if awb == "white":
        picam2.controls.AwbEnable = True
        #picam2.controls.AwbEnable = False
        #picam2.controls.ColourGains = awbR_white,  awbB_white
        #camera.controls.Contrast = 10 

def curent_exposure(picam2):
    metadata = picam2.capture_metadata()
    return (metadata['ExposureTime'], metadata['AnalogueGain'])

def auto_exp_enable(picam2, value):
    metadata = picam2.capture_metadata()
    if value == False:
        with picam2.controls as controls:
            controls.AeEnable = False
            controls.AnalogueGain = metadata['AnalogueGain']
            controls.ExposureTime = metadata['ExposureTime']

    elif value == True:
        with picam2.controls as controls:
            controls.AeEnable = True
            controls.AnalogueGain = 0
            controls.ExposureTime = 0
    

def set_exposure(picam2, shutter = None, gain= None):
    if shutter:
        picam2.controls.ExposureTime = shutter
    if gain:
        with picam2.controls as controls:
            controls.AeEnable = False
            controls.AnalogueGain = gain 


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
    from picamera2 import Picamera2
    from RPi import GPIO
    from os import environ

    from modules.microscope import Microscope
    from modules.position_grid import PositionsGrid
    from modules.physical_controller import encoder_read, controller_startup
    from modules.interface.main_menu import *
    from modules.microscope_param import *
    from modules.parametersIO import ParametersSets
    from time import sleep
    from os import environ


    ### Object for microscope to run
    #parameters = ParametersSets()
    #microscope = Microscope(addr, ready_pin, parameters)
    #grid = PositionsGrid(microscope, parameters)
    camera = Picamera2()

    
    #start picamPreview
    display = environ.get('DISPLAY')
    if display == ":0.0" or display == ":0": ## :0.0 in terminal and :0 without terminal
        preview_picam(camera)    
    else:
        preview_picam(camera, external=True)

    sleep(1)
    awb_preset(camera, "auto")
    


    while True:
        metadata = camera.capture_metadata()
        print(f"ExposureTime: {metadata['ExposureTime']}, Gain: {metadata['AnalogueGain']}")
        print("1 AWB \n2 Shutter \n3 Brightness \n4 none \n5 Contrast \n6 Analog Gain\n7 Save Image")
        setting_choice = input("Seting:")
       
        if setting_choice == "1":
            camera.awb_mode = 'off'
            blue_input = input("AWB_blue: ")
            red_input = input("AWB_red: ")
            camera.controls.ColourGains = float(red_input), float(blue_input)

        if setting_choice == "2":        
            shutter_input = input("SExposure Time: ")
            camera.controls.ExposureTime = (int(shutter_input))
        
        
        if setting_choice == "3":     
            bright_input = input("Brightness: ")
            camera.controls.Brightness = int(bright_input)

        if setting_choice == "4": 
            iso_input = input("Iso: ")
            #camera.controls.iso = int(iso_input)
        
        if setting_choice == "5": 
            text_input = input("Contrast -100 to 100:")
            camera.controls.Contrast = int(text_input)
        
        if setting_choice == "6": 
            text_input = input("Analog Gain:")
            camera.controls.AeEnable = False
            camera.controls.AnalogueGain = float(text_input)
        
        if setting_choice == "7": 
            text_input = input("Save")
            save_img_thread(camera, "/home/pi/microscope_data/img/test_img" )
        



    #GPIO cleanup
    GPIO.cleanup()
