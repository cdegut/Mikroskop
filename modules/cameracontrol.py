from .parametersIO import create_folder
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


def save_image(camera, picture_name, data_dir):
    create_folder(data_dir + "img/")
    full_data_name = data_dir + "img/"  + picture_name + ".png"
    save = Thread(target = save_img_thread, args=(camera, full_data_name))
    save.start()

def save_img_thread(camera, name):
     camera.capture(name, format = 'png')

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
            self.camera.resolution= preview_resolution


##### Function that generate the worker and pass the information to it
def start_recording(camera, data_dir, video_quality=320, video_name="test"):
    create_folder(data_dir + "rec/")
    data_name = data_dir + "rec/" + video_name + ".h264"
    rec_off = Event()
    rec = VideoRecorder(camera, video_quality, data_name, rec_off)
    rec.start()

    return rec , rec_off ## return the worker and the event to stop the recording

def stop_video(off_event):
    off_event.set()

    
             
