from .super import Interface
import tkinter as tk
from ..cameracontrol import start_recording
from time import time


class Video_record_window(Interface, tk.Frame):
        
    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        tk.Frame.__init__(self, Tk_root)
        Interface.__init__(self, Tk_root, microscope=microscope, grid=grid, camera=camera)
        
        self.rec_off_event = None
        self.recorder = None
        
        self.init_window()


    ######### generate local window ######
    def init_window(self):
        self.pack(fill=tk.BOTH, expand=1)
        self.back_to_main_button()
        self.coordinate_place()
        self.record_button_place((60,50))
        self.timer = tk.Label(self, text="0 min 0 sec")
        self.timer.place(x=80, y=100)
        self.timer_update()

        self.quality = tk.StringVar()


   
    def record_button_place(self, rec_position):
        self.Rec = tk.Button(self, text="Start Recording", command=lambda: self.start_recording_action(rec_position))
        self.Stop = tk.Button(self, fg='Red', text="Stop Recording", command=lambda: self.stop_recording_action(rec_position))

        if not self.recorder:
            self.Rec.place(x=rec_position[0], y=rec_position[1])
        else:
            self.Stop.place(x=rec_position[0], y=rec_position[1])
        
    def start_recording_action(self, position):
        timestamp = self.timestamp()
        self.recorder, self.rec_off_event = start_recording(self.camera, timestamp)
        self.Rec.place_forget()
        self.Stop.place(x=position[0], y=position[1])
        Interface._video_timer = VideoTimer()
        Interface._video_timer.start()
        self.timer_update()
    
    ##### Update the timer text if the _video_timer object exist
    def timer_update(self):
        if Interface._video_timer:
            Interface._video_timer.update_time()
            self.timer.configure(text=Interface._video_timer.text_output)
            Interface._job1 = self.after(500, self.timer_update)


    ######### End recording, set the off event for the recording Thread        
    def stop_recording_action(self, position):
        if self.rec_off_event:
            self.rec_off_event.set()
            self.recorder.join()
            self.rec_off_event = None
            self.recorder = None
            self.Stop.place_forget()
            self.Rec.place(x=position[0], y=position[1])
            Interface._video_timer = None  ## Deactivate the timer 

    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._video_record:
            Interface._video_record.init_window()
        else:
            Interface._video_record = Video_record_window(self.Tk_root, last_window=self, microscope=self.microscope, grid=self.grid, camera=self.camera)

class VideoTimer(): ## callable timer for measuring video lengh
    def __init__(self):
        self.start_time = None
        self.text_output = None
    
    def start(self):
        self.start_time = int(time())
    
    def update_time(self):
        curent_time = int(time()) - self.start_time
        minutes = int(curent_time / 60)
        secondes = curent_time - (minutes * 60)
        self.text_output = f"{minutes} min {secondes} sec"
    

#main loop
if __name__ == "__main__": 
    from ..microscope import Microscope
    from ..position_grid import PositionsGrid
    import picamera
    from ..microscope_param import *
    from ..cameracontrol import previewPiCam

    ### Object for microscope to run
    microscope = Microscope(addr, ready_pin)
    grid = PositionsGrid(microscope)
    camera = picamera.PiCamera()

    #Tkinter object
    Tk_root = tk.Tk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._video_record = Video_record_window(Tk_root, last_window=None, microscope=microscope, grid=grid, camera=camera)

    #start picamPreview
    previewPiCam(camera)

    Tk_root.mainloop()

