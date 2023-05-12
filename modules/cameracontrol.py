from .parametersIO import load_parameters, create_folder
from time import sleep
from threading import Thread, Event

camera_full_resolution = (4056,3040)
camera_max_resolution = (3000, 2248)
h264_max_resolution = (1664,1248)

def previewPiCam(camera): #show preview directly as screen overlay
    camera.preview_fullscreen=False
    camera.preview_window=(0,25, 800, 625)
    camera.resolution=(camera_max_resolution) #change picture resolution here
    camera.video_stabilization=True
    camera.start_preview()

def change_zoom(camera, value):
    ##Centered zoom
    position_scale = (1 - value)/2

    ###Scale the resolution according to the zoom
    new_resolution = (int(value*camera_full_resolution[0]),int(value*camera_full_resolution[1]))

    camera.resolution=(new_resolution)
    camera.zoom=(position_scale,position_scale, value, value)


def save_image(camera, picture_name):
    data_dir= load_parameters()["data_dir"]
    create_folder(data_dir + "img/")
    full_data_name = data_dir + "img/"  + picture_name + ".png"
    save = Thread(target = save_img_thread, args=(camera, full_data_name))
    save.start()

def save_img_thread(camera, name):
     camera.capture(name, format = 'png')

class VideoRecorder(Thread):
    def __init__(self,camera, video_name,event_rec_on):
        Thread.__init__(self)
        self.camera = camera
        self.video_name = video_name
        self.event = event_rec_on

    def run(self):
        old_resolution = self.camera.resolution

        #### Change resolution if incompatible with the video
        if old_resolution[0] > h264_max_resolution[0]:
            self.camera.resolution=(h264_max_resolution[0],h264_max_resolution[1])

        ### Start recording and wait for stop button
        self.camera.start_recording(self.video_name)
        while not self.event.is_set():
            sleep(0.1)

        ### Stop recording
        self.camera.stop_recording()

        ### put back the former resolution setting
        if old_resolution != self.camera.resolution:
            self.camera.resolution= old_resolution

def start_recording(camera, video_name="test"):
    data_dir = load_parameters()["data_dir"]
    create_folder(data_dir + "rec/")
    data_name = data_dir + "rec/" + video_name + ".h264"
    rec_off = Event()
    rec = VideoRecorder(camera, data_name, rec_off)
    rec.start()

    return rec , rec_off

def stop_video(off_event):
    off_event.set()

    
             
