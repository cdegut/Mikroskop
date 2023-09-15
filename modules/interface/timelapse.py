from .super import Interface
from .popup import led_focus_zoom_buttons
from ..parametersIO import create_folder
from ..cameracontrol2 import save_img_thread
from threading import Thread
from time import time, sleep
from os.path import isfile
from tinker import Frame, Button, BOTH, Label, StringVar, OptionMenu


class Time_lapse_window(Interface, Frame):
        
    def __init__(self, Tk_root, microscope, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, camera=camera, parameters=parameters)
        
        self.led = 0
        self.ledpwr = 0
        self.max_frame = 5
        self.timer = 5

        self.start_timer = None
        self.frame_index = 0
        self.is_recording = False
      
        self.init_window()
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._time_lapse:
            Interface._time_lapse.init_window()
        else:
            Interface._time_lapse = Time_lapse_window(self.Tk_root, self.microscope, self.camera, self.parameters)
    
    def init_window(self):
        self.pack(fill=BOTH, expand=1)

        #generic buttons
        self.back_to_main_button()
        self.coordinate_place()
        self.show_record_label()
        self.record_button_place((60,50))
        
    def menu(self, x_p=20, y_p=10):
        self.timer_selector = StringVar()
        self.total_time = StringVar()
        TimerLabel = Label(self, text="Delay (s)")
        TimerMenu = OptionMenu(self, self.timer_selector, *[2,5,10,20])
        TotalTimeLabel = Label(self, text="Duration (min):")
        TotalTimeMenu = OptionMenu(self, self.total_time, *[1,2,5,10,20,30,60])
        self.timer_selector.set(5)
        self.total_time.set(5)
        TimerLabel.place(x=x_p+5, y=y_p)
        TimerMenu.place(x=x_p, y=y_p+20)
        TotalTimeLabel.place(x=x_p+90, y=y_p)
        TotalTimeMenu.place(x=x_p+100, y=y_p+20)
        TotalTimeMenu.config(width=3)
        TimerMenu.config(width=3)


    def record_button_place(self, rec_position):
        self.Rec = Button(self, text="Start Recording", command= self.start_time_lapse)
        self.Stop = Button(self, fg='Red', text="Stop Recording", command= self.stop_time_lapse)

        if not self.is_recording:
            self.Rec.place(x=rec_position[0], y=rec_position[1])
            self.back_to_main_button()
            self.menu(x_p=10, y_p=120)
            led_focus_zoom_buttons(self,position=300)
        else:
            self.Stop.place(x=rec_position[0], y=rec_position[1])
            self.FrameLabel = Label(self, text=f"Frame Number: {self.frame_index + 1} \nof total: {self.max_frame }")
            self.FrameLabel.place(x=rec_position[0], y=rec_position[1]+40)


    def start_time_lapse(self):
        data_dir = self.parameters.get()["data_dir"]
        self.led = self.microscope.positions[4]
        self.ledpwr = self.microscope.positions[3]
        self.timer = int(self.timer_selector.get())
        self.max_frame = int(60 / self.timer *  int(self.total_time.get()))
        date = self.timestamp()
        create_folder(f"{data_dir}time-lapse/")
        #full_data_path = f"{data_dir}time-lapse/{date}/"
        self.full_data_path = f"{data_dir}time-lapse/"
        create_folder(self.full_data_path)
        self.start_timer = time()
        self.frame_index = 0
        self.single_frame()
        self.frame_index = 1
        self.is_recording = True
        Interface._timelapse_job = self.after(100, self.run_time_lapse)
        self.clear_frame()
        self.init_window()
    
    def run_time_lapse(self):

        if self.is_recording:

            if (time() - self.start_timer) > self.timer:
                self.start_timer = time()
                self.single_frame()
                self.FrameLabel.configure(text=f"Frame Number: {self.frame_index + 1} \nof total: {self.max_frame}")
                self.frame_index += 1
               
                if self.frame_index >= self.max_frame:
                    self.stop_time_lapse()
        
            Interface._timelapse_job = self.after(100, self.run_time_lapse)

    def single_frame(self):
        
        full_data_name = f"{self.full_data_path}{self.frame_index}"
        self.microscope.set_ledpwr(self.ledpwr)
        save = Thread(target = save_img_thread, args=(self.camera, full_data_name))
        save.start()
        while not isfile(full_data_name + ".png"):
            sleep(0.01)
        self.microscope.set_ledpwr(0)
    
    def stop_time_lapse(self):
        self.is_recording = False
        self.open()



#main loop
if __name__ == "__main__": 
    from ..microscope import Microscope
    from ..position_grid import PositionsGrid
    import picamera
    from ..microscope_param import *
    from ..cameracontrol import previewPiCam
    from ..parametersIO import ParametersSets
    from tinker import Tk
    ### Object for microscope to run
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin)
    grid = PositionsGrid(microscope, parameters=parameters)
    camera = picamera.PiCamera()

    #Tkinter object
    Tk_root = Tk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._time_lapse = Time_lapse_window(Tk_root, microscope=microscope,camera=camera, parameters=parameters)

    #start picamPreview
    previewPiCam(camera)

    Tk_root.mainloop()
