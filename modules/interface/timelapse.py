from .super import Interface
from .popup import led_focus_zoom_buttons
from ..cameracontrol import save_img_thread, awb_preset
from ..parametersIO import create_folder
from time import sleep
from threading import Thread, Event
import tkinter as tk
from os.path import isfile


class Time_lapse_window(Interface, tk.Frame):
        
    def __init__(self, Tk_root, microscope, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, camera=camera, parameters=parameters)
        
        self.init_window()
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._time_lapse:
            Interface._time_lapse.init_window()
        else:
            Interface._time_lapse = Time_lapse_window(self.Tk_root, self.microscope, self.camera, self.parameters)
    
    def init_window(self):
        self.pack(fill=tk.BOTH, expand=1)

        #generic buttons
        self.back_to_main_button()
        self.coordinate_place()
        self.show_record_label()
        led_focus_zoom_buttons(self)

        self.Start = tk.Button(self, text="Start Recording", command=self.start_time_lapse)
        self.Start.place(x=80, y=100)
    
    def start_time_lapse(self):
        data_dir = self.parameters.get()["data_dir"]
        ledpwr = self.microscope.positions[3]
        date = self.timestamp()
        create_folder(f"{data_dir}time-lapse/")
        #full_data_path = f"{data_dir}time-lapse/{date}/"
        full_data_path = f"{data_dir}time-lapse/"
        create_folder(full_data_path)
        for i in range(10):
            self.single_frame(255, i ,full_data_path)
            sleep(2)

    
    def single_frame(self, ledpwr, frame_number, full_data_path):
        full_data_name = f"{full_data_path}{frame_number}"
        self.microscope.set_ledpwr(ledpwr)
        save = Thread(target = save_img_thread, args=(self.camera, full_data_name))
        save.start()
        while not isfile(full_data_name + ".png"):
            sleep(0.01)
        self.microscope.set_ledpwr(0)

#main loop
if __name__ == "__main__": 
    from ..microscope import Microscope
    from ..position_grid import PositionsGrid
    import picamera
    from ..microscope_param import *
    from ..cameracontrol import previewPiCam
    from ..parametersIO import ParametersSets

    ### Object for microscope to run
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin)
    grid = PositionsGrid(microscope, parameters=parameters)
    camera = picamera.PiCamera()

    #Tkinter object
    Tk_root = tk.Tk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._time_lapse = Time_lapse_window(Tk_root, microscope=microscope,camera=camera, parameters=parameters)

    #start picamPreview
    previewPiCam(camera)

    Tk_root.mainloop()
