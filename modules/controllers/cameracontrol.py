from picamera2 import Picamera2,Preview
from threading import Thread, Event
from libcamera import Transform
from time import sleep
#from .QTinterface.picameraQT import PreviewWidget
from picamera2.previews.qt import QGlPicamera2, QPicamera2
from modules.controllers import MicroscopeManager , create_folder
from .pins import *

camera_full_resolution = (4056,3040)
h264_max_resolution = (1664,1248)

class Microscope_camera(Picamera2):
    def __init__(self, microscope: MicroscopeManager):
        Picamera2.__init__(self)
        self.crop_factor = 1
        self.EV_value = 0
        self.exp = 500
        self.gain = 1
        self.initialise()
        self.metadata = []
        self.post_callback = self.post_callback_exec
        self.qpicamera: QPicamera2 | QGlPicamera2 = None
        self.save_data_name = None
        self.microscope: MicroscopeManager = microscope

        self.new_config = None

        self.request_counter = 0
        self.zoom_animation = {}
        self.capture_param = {}

        self.is_capturing = False

        self.full_image_array = None
    
    def initialise(self):
        self.general_config = self.create_preview_configuration(main={"size":  (1610, 1200), "format": "RGB888" }, 
                                                                lores={"size": (preview_resolution), "format": "YUV420"}, 
                                                                raw={"size": (2028, 1520)}, display= "lores", buffer_count=1)
        self.align_configuration(self.general_config)
        self.full_res_config = self.create_still_configuration(main={"size":  camera_full_resolution, "format": "RGB888" },
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
       
        if not animation:
            crop = [int(crop_factor*self.zoom_animation["full_res"][0]),int(crop_factor*self.zoom_animation["full_res"][1])]
            offset = [(self.zoom_animation["full_res"][0] - crop[0]) // 2 , (self.zoom_animation["full_res"][1] - crop[1]) // 2 , ]
            self.zoom_animation["final_crop"] = crop
            self.zoom_animation["final_offset"] = offset
            self.correct_resolution(crop)
            self.set_controls({"ScalerCrop": offset  + crop})
        
        self.post_callback = self.post_callback_zoom_animation_
        self.request_counter = 0
        self.zoom_animation["steps"] = (crop_factor - self.crop_factor) / 20

    ## use the callback to animate the zoom
    def post_callback_zoom_animation_(self, request):
        self.metadata = request.get_metadata()
        self.request_counter += 1

        crop_factor = self.crop_factor + ((self.request_counter) * self.zoom_animation["steps"])
        crop = [int(crop_factor*self.zoom_animation["full_res"][0]),int(crop_factor*self.zoom_animation["full_res"][1])]
        offset = [(self.zoom_animation["full_res"][0] - crop[0]) // 2 , (self.zoom_animation["full_res"][1] - crop[1]) // 2 , ]
        self.set_controls({"ScalerCrop": offset  + crop})
        
        if self.request_counter == 20:
            
            self.zoom_animation["final_crop"] = crop   
            self.zoom_animation["final_offset"] = offset
            self.crop_factor = crop_factor
            self.post_callback = self.post_callback_exec
            self.correct_resolution(crop)
            self.set_controls({"ScalerCrop": offset  + crop})
    

    def correct_resolution(self, new_field = (1400, 1080)):
        '''
        crop to the real sensor resolution
        '''
        new_main_config = None
        
        ## main corection when zooming in
        if new_field[0] < self.general_config["main"]["size"][0]:
            new_main_config = new_field
            
        ## main corection when zooming out
        if new_field[0] > self.running_config["main"]["size"][0]:
            
            if new_field[0] < self.general_config["main"]["size"][0]:
                new_main_config = new_field
            else:
                new_main_config = self.general_config["main"]["size"]
        
        if new_main_config:
            self.running_config["main"]["size"] = (new_main_config[0] - new_main_config[0] % 16,
                                                    new_main_config[1] - new_main_config[1] % 16)        

        # need to alin configuration to 64 for YUV stram and 16 omly for RGB stream, not exactly sure why

        self.stop()
        #rescale the preview if needed, start by resting to default before rescaling
        self.running_config["lores"]["size"] = self.general_config["lores"]["size"]
        if self.running_config["main"]["size"] < self.running_config["lores"]["size"]:
            self.running_config["lores"]["size"] = self.running_config["main"]["size"]

        self.configure_(self.running_config)
        self.start()

                        

    def switch_mode_keep_zoom(self, mode):
        if mode == "general":
            self.switch_mode(self.running_config, signal_function=self.qpicamera.signal_done)
            self.change_zoom(self.crop_factor, animation =False)
        if mode == "full_res":
            offset, crop = self.change_zoom(self.crop_factor, False)
            self.full_res_config["main"]["size"] = (crop[0] //2 *2, crop[1]//2*2)
            self.align_configuration(self.full_res_config)
            self.switch_mode(self.full_res_config)
            self.set_controls({"ScalerCrop": offset  + crop})
            self.capture_metadata() ## need to wait an image before giving the feed back
        if mode == "video":
            self.switch_mode(self.video_config)
            self.change_zoom(self.crop_factor, animation =False)
             

    def capture_and_save(self, picture_name, data_dir):
        self.is_capturing = True
        create_folder(data_dir)
        self.save_data_name = f"{data_dir}/{picture_name}.png"
        self.capture_image("main", signal_function=self.process_capture_)

    def lores_capture(self, picture_name, data_dir):
        self.is_capturing = True
        create_folder(data_dir)
        self.save_data_name = f"{data_dir}/{picture_name}.jpg"
        self.capture_image("lores", signal_function=self.process_capture_)

    def process_capture_(self,capture_job):
        self.qpicamera.signal_done(capture_job)
        pil_img = self.wait(capture_job)
        save = Thread(target = self.thread_save_capture_, args=(pil_img, self.save_data_name))
        save.start()
        self.is_capturing = False
   
    def thread_save_capture_(self, pil_img , full_data_name): ##run as a separate thread
        img_RGB = pil_img.convert('RGB')
        img_RGB.save(full_data_name, format = "png" )

    def capture_full_res(self,  picture_name, data_dir):
        self.is_capturing = True
        self.save_data_name = f"{data_dir}/{picture_name}.png"
        self.switch_mode(self.full_res_config, signal_function=self.qpicamera.signal_done)
        self.capture_and_save(picture_name, data_dir) 
        self.switch_mode(self.running_config, signal_function=self.zoom_back_)

    def create_full_res_array(self):
        self.is_capturing = True
        self.switch_mode(self.full_res_config, signal_function=self.qpicamera.signal_done)
        self.create_main_array()
        self.switch_mode(self.running_config, signal_function=self.zoom_back_)

    def create_main_array(self):
        self.capture_array( name="main", wait=None, signal_function=self.process_array_)

    def process_array_(self, array_job):
        self.qpicamera.signal_done(array_job)
        array = self.wait(array_job)
        self.full_image_array = array
        
 
    def zoom_back_(self, job):
        self.qpicamera.signal_done(job)
        if self.crop_factor != 1:
            print("zoom back")
            self.wait(job)
            self.set_controls({"ScalerCrop": self.zoom_animation["final_offset"]  + self.zoom_animation["final_crop"]})
        
    def capture_with_preset(self):
        #self.capture_param = capture_param

        self.stop()
        self.configure_(self.full_res_config)
        self.start()
        self.post_callback = self.capture_with_preset_callback_
        self.capture_param["counter"] = 0

        if "led1pwr" in self.capture_param.keys():
            self.set_preset_values(self.capture_param)
  
    def capture_with_preset_callback_(self, request):
        self.capture_param["counter"] += 1
        self.metadata = request.get_metadata()

        if self.capture_param["counter"] < 5: #some images are needed to stabilise the cature
            return 
        
        data_name = f"{self.capture_param['data_dir']}/{self.capture_param['picture_name']}"
        result = request.make_image("main")
        save = Thread(target = self.thread_save_capture_, args=(result, data_name))
        save.start()
        self.post_callback = self.post_callback_exec

        # No blocking switch_mode:
        self.stop()
        self.configure_(self.running_config)
        self.start()

        if "led1pwr" in self.capture_param.keys():
            self.set_preset_values()


    def set_preset_values(self, preset = None):
        '''
        take dictionary with ["awb"] ["led1pwr"] ["led2pwr"] ["auto_exp"] (auto) ["EV"] ["gain"] ["exp"]
        None = all auto values
        '''
        if preset is None:
             self.awb_preset("auto")
             self.auto_exp_enable(True)
             self.set_EV(0)
             self.microscope.request_ledspwr(25,0)
             self.microscope.run() # do not wait for next microscope runtime

             return

        self.awb_preset(preset["awb"])
        self.microscope.request_ledspwr(preset["led1pwr"],preset["led2pwr"])
        self.microscope.run() # do not wait for next microscope runtime

        if preset["auto_exp"] == "auto":
            self.auto_exp_enable(True)
            self.set_EV(preset["EV"])
        else:
            self.set_exposure(preset["exp"], preset["gain"])


    def awb_preset(self, awb):
        if awb == "Green Fluo":
            self.controls.AwbEnable = False
            self.controls.ColourGains = awbR_fluo,  awbB_fluo
            #camera.controls.Contrast = 10
        
        if awb == "Green Fluo 2":
            self.controls.AwbEnable = False
            self.controls.ColourGains = awbR_fluo,  0.25
        
        if awb == "Green Fluo 3":
            self.controls.AwbEnable = False
            self.controls.ColourGains = awbR_fluo,  0.15

        if awb == "Green Fluo 3":
            self.controls.AwbEnable = False
            self.controls.ColourGains = awbR_fluo,  0.05

        if awb == "auto":
            self.controls.AwbEnable = True
        if awb == "White LED":
            self.controls.AwbEnable = True
            self.controls.AwbEnable = False
            self.controls.ColourGains = awbR_white,  awbB_white
            #camera.controls.Contrast = 10 

    def current_exposure(self):
        return (self.metadata['ExposureTime'], self.metadata['AnalogueGain'])

    def auto_exp_enable(self, value: bool):

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
    def __init__(self,camera: Microscope_camera, video_quality, video_name,event_rec_on):
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
            record_resolution = [preview_resolution[0], preview_resolution[1]]
        
        ## else set the camera to the new resolution
        else:
            record_resolution = [self.video_quality, 
                int((self.video_quality)*(self.camera.camera_properties['PixelArraySize'][1]/self.camera.camera_properties['PixelArraySize'][0]))]

        #### Change resolution if incompatible with the video
        if record_resolution[0] > h264_max_resolution[0]:
            record_resolution = h264_max_resolution
        
        #align resolution for YUV (need to be *64)
        record_resolution[0] = record_resolution[0] - record_resolution[0] %64
        record_resolution[1] = record_resolution[1] - record_resolution[1] %64

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
        self.camera.stop()
        self.camera.configure_(self.camera.video_config)
        self.camera.start()
        if self.camera.crop_factor != 1:
            self.camera.set_controls({"ScalerCrop": self.camera.zoom_animation["final_offset"]  + self.camera.zoom_animation["final_crop"]})
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
    micro_cam.initialise()
    print(micro_cam.camera_ctrl_info)
    while True:
        time.sleep(1)
    #micro_cam.print_metadata()
    #micro_cam.list_controls()

    

    
    

    

