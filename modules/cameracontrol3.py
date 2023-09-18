from picamera2 import Picamera2,Preview
from .parametersIO import create_folder
from threading import Thread, Event
from .microscope_param import awbR_fluo, awbB_fluo, awbR_white, awbB_white

camera_full_resolution = (4056,3040)
h264_max_resolution = (1664,1248)

class Microscope_camera(Picamera2):
    def __init__(self):
        Picamera2.__init__(self)
        self.crop_value = 1
    
    def initialise(self, QT=False):
        self.general_config = self.create_preview_configuration(main={"size":  (1400, 1080)}, lores={"size": (800, 620), "format": "YUV420"}, display= "lores", buffer_count=4)
        self.full_res_config = self.create_preview_configuration(main={"size":  (4056,3040)}, lores={"size": (400, 310), "format": "YUV420"}, display= "lores", buffer_count=1)

        self.configure(self.general_config)
        if not QT:
            self.start_preview(Preview.QTGL, x=0 , y=25, width=800, height=625)
        else:
            self.start_preview(Preview.QT, width=800, height=625)

        self.start()
        self.title_fields = ['FocusFoM']
    
    def change_zoom(self, crop_factor, animation = True):
        ### zoom value is a crop factor
        full_res = self.camera_properties['PixelArraySize']
        
        if not animation:
            crop = [int(crop_factor*full_res[0]),int(crop_factor*full_res[1])]
            offset = [(full_res[0] - crop[0]) // 2 , (full_res[1] - crop[1]) // 2 , ]
            self.set_controls({"ScalerCrop": offset  + crop})
            return

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

    def switch_mode_keep_zoom(self, mode):
        if mode == "general":
            self.switch_mode(self.general_config)
            self.change_zoom(self.crop_value, animation =False)
        if mode == "full_res":
            self.switch_mode(self.full_res_config)
            self.change_zoom(self.crop_value, animation =False)

    def capture_and_save(self, picture_name, data_dir, full_res = False):
        create_folder(data_dir + "img/")
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

        for _ in range(5):
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

if __name__ == "__main__": 
    microscope_camera = Microscope_camera()
    microscope_camera.initialise()
    import time
    time.sleep(2)
    microscope_camera.awb_preset("Green Fluo")
    time.sleep(20)