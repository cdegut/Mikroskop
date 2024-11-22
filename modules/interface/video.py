from .super import Interface
from customtkinter import CTkFrame, CTkButton, CTkLabel, BOTH, CTkOptionMenu, N, StringVar
import os
from time import time
from .popup import led_focus_zoom_buttons

from modules.controllers import *
from modules.controllers.microscope_param import *


class Video_record_window(Interface, CTkFrame):
        
    def __init__(self, Tk_root, microscope, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, camera=camera, parameters=parameters)
        
        self.rec_off_event = None
        self.recorder = None
        self.quality = StringVar()  
        self.quality.set(720)      

        self.init_window() 

    ######Function called to open this window, generate an new object the first time, 
    ###### then recall the init_window function of the same object
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._video_record:
            Interface._video_record.init_window()
        else:
            Interface._video_record = Video_record_window(self.Tk_root, self.microscope, self.camera, self.parameters)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):
        self.pack(fill=BOTH, expand=1)

        #generic buttons
        self.back_to_main_button()
        self.coordinate_place()
        self.show_record_label()
        led_focus_zoom_buttons(self)

        
        self.timer = CTkLabel(self, text="0 min 0 sec")
        QualityLabel = CTkLabel(self, text="Video Quality:")
        self.QualityMenu = CTkOptionMenu(self, values=["1600","1200","720","480"], variable=self.quality)        
     
        self.record_button_place((60,50))
        self.timer.place(x=80, y=100)
        QualityLabel.place(x=10, y=150)      
        self.QualityMenu.place(x=20, y=180)

        self.show_record_label()
        self.timer_update()
        self.snap_button()
        
    def record_button_place(self, rec_position):
        self.Rec = CTkButton(self, text="Start Recording", command=lambda: self.start_recording_action(rec_position))
        self.Stop = CTkButton(self, fg_color='Red', text="Stop Recording", command=lambda: self.stop_recording_action(rec_position))

        if not self.recorder:
            self.Rec.place(x=rec_position[0], y=rec_position[1])
        else:
            self.Stop.place(x=rec_position[0], y=rec_position[1])
        
    def start_recording_action(self, position):
        timestamp = self.timestamp()
        home = os.getenv("HOME")
        data_dir = f"{home}/{self.parameters.get()['data_dir']}"
        self.recorder, self.rec_off_event = start_recording(self.camera, data_dir,  video_quality=int(self.quality.get()), video_name=timestamp)
        self.Stop.place(x=position[0], y=position[1])
        Interface._video_timer = VideoTimer()
        Interface._video_timer.start()
        
        ### Reset the window with the new elements
        self.open()
    
    ##### Update the timer text if the _video_timer object exist
    def timer_update(self):
        if Interface._video_timer:
            Interface._video_timer.update_time()
            self.timer.configure(text=Interface._video_timer.text_output)
            Interface._job1 = self.after(500, self.timer_update)

    ######### End recording, set the off event for the recording Thread        
    def stop_recording_action(self, position):
        if self.rec_off_event:
            ### Tell the worker to stop recording
            self.rec_off_event.set()
            self.recorder.join()           
            #### Reinitialise all the object related to video recording
            self.rec_off_event = None
            self.recorder = None
            Interface._video_timer = None  ## Deactivate the timer           
            ### Reset the window with the new elements
            self.open()
            

class VideoTimer(): ## callable timer for measuring video lengh
    def __init__(self):
        self.start_time = None
        self.text_output = None
    
    def start(self):
        self.start_time = int(time())
    
    def update_time(self):
        current_time = int(time()) - self.start_time
        minutes = int(current_time / 60)
        secondes = current_time - (minutes * 60)
        self.text_output = f"{minutes} min {secondes} sec"