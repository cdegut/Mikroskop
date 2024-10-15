from .super import Interface
from .popup import led_focus_zoom_buttons
from ..parametersIO import create_folder
from time import time
from customtkinter import CTkFrame, CTkButton, CTkLabel, BOTH, CTkOptionMenu, N


class Time_lapse_window(Interface, CTkFrame):
        
    def __init__(self, Tk_root, microscope, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, camera=camera, parameters=parameters)
        
        self.led1pwr = 0
        self.led2pwr = 0
        self.max_frame = 5
        self.timer = 5

        self.start_timer = None
        self.frame_index = 0
        self.is_recording = False

        self.capture_parameters = {}
      
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
        self.Test = CTkButton(self, text="Test Image", command= self.test_image)
        
        self.back_to_main_button()
        self.coordinate_place()
        self.show_record_label()
        self.record_button_place((0.5,50))

        
        
    def menu(self, x_p=20, y_p=10):
        TimerLabel = CTkLabel(self, text="Delay (s)")
        self.TimerMenu = CTkOptionMenu(self, values=["2","5","10","20"], width=80)
        TotalTimeLabel = CTkLabel(self, text="Duration (min):")
        self.TotalTimeMenu = CTkOptionMenu(self,  values=["1","2","5","10","20","30","60"], width=80)
        self.TimerMenu.set("5")
        self.TotalTimeMenu.set("5")
        TimerLabel.place(x=x_p+5, y=y_p)
        self.TimerMenu.place(x=x_p, y=y_p+20)
        TotalTimeLabel.place(x=x_p+90, y=y_p)
        self.TotalTimeMenu.place(x=x_p+100, y=y_p+20)


    def record_button_place(self, rec_position):
        self.Rec = CTkButton(self, text="Start Recording", command= self.start_time_lapse)
        self.Stop = CTkButton(self, fg_color='Red', text="Stop Recording", command= self.stop_time_lapse)

        if not self.is_recording:
            self.Rec.place(relx=rec_position[0], y=rec_position[1], anchor=N)
            self.back_to_main_button()
            self.menu(x_p=20, y_p=120)
            self.Test.place(x=20, y=360)
            led_focus_zoom_buttons(self,position=300)
        else:
            self.Stop.place(relx=rec_position[0], y=rec_position[1], anchor=N)
            self.FrameLabel = CTkLabel(self, text=f"Frame Number: {self.frame_index + 1} \nof total: {self.max_frame }")
            self.FrameLabel.place(relx=rec_position[0], y=rec_position[1]+40, anchor=N)

    def test_image(self):
        
        self.camera.capture_param["data_dir"] = f"{self.parameters.get()['data_dir']}/time_lapse/tests"
        self.camera.capture_param["picture_name"] = self.timestamp()
        self.camera.capture_with_preset()


    def start_time_lapse(self):

        self.timer = int(self.TimerMenu.get())
        self.max_frame = int(60 / self.timer *  int(self.TotalTimeMenu.get()))
        
        self.camera.capture_param["data_dir"] = f"{self.parameters.get()['data_dir']}/time_lapse/"
        self.camera.capture_param["picture_name"] = f"{'0'.zfill(len(str(self.max_frame)))}-{self.timestamp()}"
        self.start_timer = time()
        self.camera.capture_with_preset()     
        
        self.frame_index = 1
        self.is_recording = True
        Interface._timelapse_job = self.after(100, self.run_time_lapse)
        self.clear_frame()
        self.init_window()
    
    def run_time_lapse(self):

        if self.is_recording:

            if (time() - self.start_timer) > self.timer:
                self.start_timer = time()
                
                pic_name = f"{str(self.frame_index).zfill(len(str(self.max_frame)))}-{self.timestamp()}"
                self.camera.capture_param["picture_name"] = pic_name
                self.camera.capture_with_preset()  
            
                self.FrameLabel.configure(text=f"Frame Number: {self.frame_index + 1} \nof total: {self.max_frame}")
                self.frame_index += 1
               
                if self.frame_index >= self.max_frame:
                    self.stop_time_lapse()
        
            Interface._timelapse_job = self.after(100, self.run_time_lapse)
    
    def stop_time_lapse(self):
        self.is_recording = False
        self.open()



#main loop
if __name__ == "__main__": 
    from modules.cameracontrol import Microscope_camera
    from modules.microscope import Microscope
    from modules.position_grid import PositionsGrid
    from modules.interface.main_menu import *
    from modules.microscope_param import *
    from modules.parametersIO import ParametersSets, create_folder
    import customtkinter
    ### Object for microscope to run

    #Tkinter object
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin, parameters)
    position_grid = PositionsGrid(microscope, parameters)
    micro_cam = None

    #Tkinter object
    customtkinter.set_appearance_mode("dark")
    Tk_root = customtkinter.CTk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._time_lapse = Time_lapse_window(Tk_root, microscope=microscope,camera=micro_cam, parameters=parameters)

    Tk_root.mainloop()
