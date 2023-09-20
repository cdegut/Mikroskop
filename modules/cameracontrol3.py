from picamera2 import Picamera2,Preview
from .parametersIO import create_folder
from threading import Thread, Event
from .microscope_param import awbR_fluo, awbB_fluo, awbR_white, awbB_white
from time import sleep
camera_full_resolution = (4056,3040)
h264_max_resolution = (1664,1248)

class Microscope_camera(Picamera2):
    def __init__(self):
        Picamera2.__init__(self)
        self.crop_value = 1
    
    def initialise(self, QT=False):
        self.general_config = self.create_preview_configuration(main={"size":  (1610, 1200)}, lores={"size": (804, 600), "format": "YUV420"}, raw={"size": (2028, 1520)}, display= "lores", buffer_count=1)
        self.align_configuration(self.general_config)
        self.full_res_config = self.create_still_configuration(main={"size":  (400,300)},lores={"size": (402, 300), "format": "YUV420"}, raw={"size":  (4056,3040)}, display= "lores")
        self.align_configuration(self.full_res_config)
        self.running_config = self.create_preview_configuration(main={"size":  (1610, 1200)}, lores={"size": (804, 600), "format": "YUV420"},raw={"size": (2028, 1520)}, display= "lores", buffer_count=1)
        self.align_configuration(self.running_config)

        self.configure(self.running_config)
        if not QT:
            self.start_preview(Preview.QTGL, x=0 , y=25, width=800, height=625)
        else:
            self.start_preview(Preview.QT, width=800, height=625)

        self.start()
        self.title_fields = ['FocusFoM']
    
    def change_zoom(self, crop_factor, animation = True):
        full_res = self.camera_properties['PixelArraySize']
        
        if not animation:
            crop = [int(crop_factor*full_res[0]),int(crop_factor*full_res[1])]
            offset = [(full_res[0] - crop[0]) // 2 , (full_res[1] - crop[1]) // 2 , ]
            self.set_controls({"ScalerCrop": offset  + crop})
            return offset, crop

        old_crop_factor = self.capture_metadata()['ScalerCrop'][2] / full_res[0]
        zoom_step = (crop_factor - old_crop_factor) / 20 

        for i in range(20):
            self.capture_metadata()
            value = old_crop_factor + (i * zoom_step)
            crop = [int(value*full_res[0]),int(value*full_res[1])]
            offset = [(full_res[0] - crop[0]) // 2 , (full_res[1] - crop[1]) // 2 , ]
            self.set_controls({"ScalerCrop": offset  + crop})
            
        crop = [int(crop_factor*full_res[0]),int(crop_factor*full_res[1])]

        
        offset = [(full_res[0] - crop[0]) // 2 , (full_res[1] - crop[1]) // 2 , ]
        self.set_controls({"ScalerCrop": offset  + crop})
        self.crop_value = crop_factor
        
        self.correct_resolution((crop[0], crop[1]))
        self.set_controls({"ScalerCrop": offset  + crop})
        


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
        self.switch_mode(self.running_config)
                        

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

    def capture_and_save(self, picture_name, data_dir, full_res = False):
        create_folder(data_dir)
        full_data_name = f"{data_dir}/{picture_name}.png"
        
        if full_res:
            self.switch_mode_keep_zoom("full_res")

        capture = self.capture_image("main")

        if full_res:
             self.switch_mode_keep_zoom("general")
        
        save = Thread(target = self.save_caputre, args=(capture, full_data_name))
        save.start()
    
    def capture_with_flash(self, picture_name, data_dir, microscope, led, ledpwr):
        full_data_name = f"{data_dir}/{picture_name}.png"
        
        microscope.set_led_state(led)
        microscope.set_ledpwr(ledpwr)

        for _ in range(2):
            self.capture_metadata()

        capture = self.capture_image("main")

        microscope.set_led_state(0)
        microscope.set_ledpwr(0)
        
        save = Thread(target = self.save_caputre, args=(capture, full_data_name))
        save.start()
    
    def save_caputre(self, capture, full_data_name):
        capture.save(full_data_name, format = "png" )

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

    def curent_exposure(self):
        metadata = self.capture_metadata()
        return (metadata['ExposureTime'], metadata['AnalogueGain'])

    def auto_exp_enable(self, value):
        metadata = self.capture_metadata()
        if value == False:
            with self.controls as controls:
                controls.AeEnable = False
                controls.AnalogueGain = metadata['AnalogueGain']
                controls.ExposureTime = metadata['ExposureTime']

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
                int((self.video_quality)*(self.camera_properties['PixelArraySize'][1]/self.camera_properties['PixelArraySize'][0])))

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

    create_folder(data_dir + "rec/")
    data_name = data_dir + "rec/" + video_name + ".h264"
    rec_off = Event()
    rec = VideoRecorder(camera, video_quality, data_name, rec_off)
    rec.start()

    return rec , rec_off ## return the worker and the event to stop the recording

def stop_video(off_event):
    off_event.set()
    
if __name__ == "__main__": 
    m = Microscope_camera()
    m.initialise()
    import time
    time.sleep(10)
    print(f"array: {m.capture_array().shape}")
    time.sleep(20)
    
    

    

