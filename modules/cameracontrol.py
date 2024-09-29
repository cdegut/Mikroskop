from picamera2 import Picamera2,Preview
from .parametersIO import create_folder
from threading import Thread, Event
from .microscope_param import awbR_fluo, awbB_fluo, awbR_white, awbB_white, preview_resolution
from libcamera import Transform
from time import sleep
from .interface.picameraQT import PreviewWidget
from picamera2.previews.qt import QGlPicamera2, QPicamera2

camera_full_resolution = (4056,3040)
h264_max_resolution = (1664,1248)

class Microscope_camera(Picamera2):
    def __init__(self):
        Picamera2.__init__(self)
        self.crop_value = 1
        self.EV_value = 0
        self.exp = 500
        self.gain = 1
        self.initialise()
        self.metadata = []
        self.post_callback = self.post_callback_exec
        self.qpicamera: QPicamera2 | QGlPicamera2 = None
        self.save_data_name = None

        self.request_counter = 0
        self.zoom_animation = {}
    
    def initialise(self):
        self.general_config = self.create_preview_configuration(main={"size":  (1610, 1200)}, 
                                                                lores={"size": preview_resolution, "format": "YUV420"}, 
                                                                raw={"size": (2028, 1520)}, display= "lores", buffer_count=1)
        self.align_configuration(self.general_config)
        self.full_res_config = self.create_still_configuration(main={"size":  camera_full_resolution},
                                                               lores={"size": (402, 300), "format": "YUV420"}, 
                                                               raw={"size":  camera_full_resolution}, display= "lores")
        self.align_configuration(self.full_res_config)

        self.make_running_config()

        self.configure(self.running_config)

        self.title_fields = ['FocusFoM']
    
    def post_callback_exec(self, request):
        self.metadata = request.get_metadata()

    def simple_preview(self, QT):
        if not QT:
            self.start_preview(Preview.QTGL, x=0 , y=25, width=800, height=625, transform=Transform(vflip=1))
        else:
            self.start_preview(Preview.QT, width=800, height=625, transform=Transform(vflip=1))
        self.start()
    
    def make_running_config(self):
        ## make a copy of general_config (copy and deep copy do not work well)
        main = self.general_config["main"]
        lores = self.general_config["lores"]
        raw = self.general_config["raw"]
        buffer =  self.general_config["buffer_count"]
        print(f"main{main}, lores {lores}, raw {raw}, buffers {buffer}")
        self.running_config = self.create_preview_configuration(main=main, lores=lores, raw=raw, display= "lores", buffer_count=buffer)
    
    def change_zoom(self, crop_factor, animation = True):
    
        self.zoom_animation["full_res"] = self.camera_properties['PixelArraySize']  
        #curent_crop = self.crop_value

        
        if not animation:
            crop = [int(crop_factor*self.zoom_animation["full_res"][0]),int(crop_factor*self.zoom_animation["full_res"][1])]
            offset = [(self.zoom_animation["full_res"][0] - crop[0]) // 2 , (self.zoom_animation["full_res"][1] - crop[1]) // 2 , ]
            self.set_controls({"ScalerCrop": offset  + crop})
            return offset, crop
        
        self.post_callback = self.post_callback_zoom_animation
        self.request_counter = 0
        self.zoom_animation["steps"] = (crop_factor - self.crop_value) / 20 

    ## use the callback to animate the zoom
    def post_callback_zoom_animation(self, request):
        self.metadata = request.get_metadata()
        self.request_counter += 1

        value = self.crop_value + ((self.request_counter) * self.zoom_animation["steps"])
        crop = [int(value*self.zoom_animation["full_res"][0]),int(value*self.zoom_animation["full_res"][1])]
        offset = [(self.zoom_animation["full_res"][0] - crop[0]) // 2 , (self.zoom_animation["full_res"][1] - crop[1]) // 2 , ]
        self.set_controls({"ScalerCrop": offset  + crop})
        
        if self.request_counter == 20:
            self.post_callback = self.post_callback_exec
            #self.correct_resolution((crop[0], crop[1]))
            self.set_controls({"ScalerCrop": offset  + crop}) 
            self.crop_value = value     

    def correct_resolution(self, new_field = (1400, 1080)):
        new_main_config = None
        new_lores_config = None
        
        ## main corection when zooming in
        if new_field[0] < self.general_config["main"]["size"][0]:
            new_main_config = new_field
            
            ## lores corection when zooming in
            if new_main_config[0] < self.running_config["lores"]["size"][0]:
                new_lores_config = new_field
            
 
        ## main corection when zooming out
        if new_field[0] > self.running_config["main"]["size"][0]:
            
            if new_field[0] < self.general_config["main"]["size"][0]:
                new_main_config = new_field
            else:
                new_main_config = self.general_config["main"]["size"]
            
            ## lowres corection when zoming out
            if self.running_config["lores"]["size"][0] < new_field[0]:
                if new_field[0] < self.general_config["lores"]["size"][0]:
                    new_lores_config = new_field
                else:
                    new_lores_config = self.general_config["lores"]["size"]
        
        
        if new_main_config:            
            self.running_config["main"]["size"] = (new_main_config[0] // 2 * 2 , new_main_config[1] // 2 * 2 )
        
        if new_lores_config:
            self.running_config["lores"]["size"] = (new_lores_config[0] // 2 * 2 , new_lores_config[1] // 2 * 2 )
        
        self.align_configuration(self.running_config)
        if self.running_config["main"]["size"] > self.running_config["lores"]["size"]:
            self.running_config["lores"]["size"] = self.running_config["main"]["size"]
        self.switch_mode(self.running_config, signal_function=self.qpicamera.signal_done)
                        

    def switch_mode_keep_zoom(self, mode):
        if mode == "general":
            self.switch_mode(self.running_config)
            self.change_zoom(self.crop_value, animation =False)
        if mode == "full_res":
            offset, crop = self.change_zoom(self.crop_value, False)
            self.full_res_config["main"]["size"] = (crop[0] //2 *2, crop[1]//2*2)
            self.align_configuration(self.full_res_config)
            self.switch_mode(self.full_res_config)
            self.set_controls({"ScalerCrop": offset  + crop})
            self.capture_metadata() ## need to wait an image before giving the feed back
        if mode == "video":
            self.switch_mode(self.video_config)
            self.change_zoom(self.crop_value, animation =False)
             

    def capture_and_save(self, picture_name, data_dir):
        create_folder(data_dir)
        self.save_data_name = f"{data_dir}/{picture_name}.png"
        self.capture_image("main", signal_function=self.process_capture_)        

    def process_capture_(self,capture_job):
        self.qpicamera.signal_done(capture_job)
        pil_img = self.wait(capture_job)
        save = Thread(target = self.thread_save_capture_, args=(pil_img, self.save_data_name))
        save.start()
   
    def thread_save_capture_(self, pil_img , full_data_name): ##run as a separate thread
        print("saving")
        img_RGB = pil_img.convert('RGB')
        img_RGB.save(full_data_name, format = "png" )

    def capture_full_res(self,  picture_name, data_dir):
        self.save_data_name = f"{data_dir}/{picture_name}.png"
        self.switch_mode(self.full_res_config, signal_function=self.qpicamera.signal_done)
        self.capture_and_save(picture_name, data_dir) 
        self.switch_mode(self.running_config, signal_function=self.qpicamera.signal_done)
        if self.crop_value != 1:
            self.change_zoom(self.crop_value, False)
    
    def capture_HD_(self, switch_job):
        self.qpicamera.signal_done(switch_job)
        self.wait(switch_job)
        self.capture_image("main", signal_function=self.process_capture_)
        

    def capture_with_flash(self, picture_name, data_dir, microscope, led, ledpwr):
        
        microscope.set_led_state(led)
        microscope.set_ledpwr(ledpwr)
        
        self.capture_metadata()
        self.capture_and_save(picture_name, data_dir)

        microscope.set_led_state(0)
        microscope.set_ledpwr(0)

    def awb_preset(self, awb):
        if awb == "Green Fluo":
            self.controls.AwbEnable = False
            self.controls.ColourGains = awbR_fluo,  awbB_fluo
            #camera.controls.Contrast = 10
        if awb == "auto":
            self.controls.AwbEnable = True
        if awb == "white":
            self.controls.AwbEnable = True
            #self.controls.AwbEnable = False
            #self.controls.ColourGains = awbR_white,  awbB_white
            #camera.controls.Contrast = 10 

    def current_exposure(self):
        return (self.metadata['ExposureTime'], self.metadata['AnalogueGain'])

    def auto_exp_enable(self, value):

        if value == False:
            with self.controls as controls:
                controls.AeEnable = False
                controls.AnalogueGain = self.metadata['AnalogueGain']
                controls.ExposureTime = self.metadata['ExposureTime']

        elif value == True:
            with self.controls as controls:
                controls.AeEnable = True
                controls.AnalogueGain = 0
                controls.ExposureTime = 0
        
    def set_exposure(self, shutter = None, gain= None):
        if shutter:
            self.controls.ExposureTime = shutter
        if gain:
            with self.controls as controls:
                controls.AeEnable = False
                controls.AnalogueGain = gain

    def set_EV(self, value):
        self.controls.ExposureValue = value
        self.EV_value = value 

from picamera2.encoders import H264Encoder, Quality

class VideoRecorder(Thread):
    def __init__(self,camera, video_quality, video_name,event_rec_on):
        Thread.__init__(self)
        self.camera = camera
        self.video_name = video_name
        self.event = event_rec_on
        self.video_quality = video_quality

    def run(self):
        ## Save the current preview settings
        preview_resolution = self.camera.running_config["main"]["size"]

        ## If the video quality demanded is higher than the preview, get back to the preview (avoided useless oversampling of zoomed in video)
        if preview_resolution[0] < self.video_quality:          
            record_resolution = preview_resolution
        
        ## else set the camera to the new resolution
        else:
            record_resolution = (self.video_quality, 
                int((self.video_quality)*(self.camera.camera_properties['PixelArraySize'][1]/self.camera.camera_properties['PixelArraySize'][0])))

        #### Change resolution if incompatible with the video
        if record_resolution[0] > h264_max_resolution[0]:
            record_resolution = h264_max_resolution
        
        #### Set the resolution
        if record_resolution[0] < self.camera.general_config["lores"]["size"][0]:
            self.camera.video_config = self.camera.create_video_configuration(main={"size":  (record_resolution[0],record_resolution[1]), "format": "YUV420" },
                                                                raw={"size": (2028, 1520)}, 
                                                                display= "main", encode = "main", buffer_count=6)
        else:
            self.camera.video_config = self.camera.create_video_configuration(main={"size":  (record_resolution[0],record_resolution[1]), "format": "YUV420"}, 
                                                                lores={"size": (804, 600), "format": "YUV420"},
                                                                raw={"size": (2028, 1520)}, 
                                                                display= "lores", encode = "main", buffer_count=6)
        self.camera.align_configuration(self.camera.video_config)

        ### Start recording and wait for stop button
        encoder = H264Encoder()
        self.camera.switch_mode_keep_zoom("video")
        self.camera.start_encoder(encoder, self.video_name)
        while not self.event.is_set():
            sleep(0.1)

        ### Stop recording
        self.camera.stop_encoder()

        self.camera.switch_mode_keep_zoom("general")



##### Function that generate the worker and pass the information to it
def start_recording(camera, data_dir, video_quality=320, video_name="test"):

    create_folder(data_dir + "/rec/")
    data_name = data_dir + "/rec/" + video_name + ".h264"
    rec_off = Event()
    rec = VideoRecorder(camera, video_quality, data_name, rec_off)
    rec.start()

    return rec , rec_off ## return the worker and the event to stop the recording

def stop_video(off_event):
    off_event.set()
    
if __name__ == "__main__":
    import time
    micro_cam = Microscope_camera()
    micro_cam.initialise(QT=True)
    print(micro_cam.camera_ctrl_info)
    while True:
        time.sleep(1)
    #micro_cam.print_metadata()
    #micro_cam.list_controls()

    

    
    

    

