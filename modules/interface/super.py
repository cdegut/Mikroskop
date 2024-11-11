from customtkinter import CTkFrame, CTkButton, CTkLabel, N, CTkSlider, IntVar, CENTER, CTk
from ..microscope import Microscope
from ..position_grid import PositionsGrid
from ..microscope_param import Xmaxrange, Ymaxrange
from ..cameracontrol import Microscope_camera
from time import localtime
import os


plate_name = "Plate" ##is a place holder to later add a plate type selector, maybe

############
## Super class that contain shared functions for all interface windows
## and job handelers

class Interface: 

    def __init__(self, Tk_root: CTk, last_window=None, microscope: Microscope =None, position_grid: PositionsGrid =None, camera: Microscope_camera = None, parameters=None):
        CTkFrame.__init__(self, Tk_root)
        self.Tk_root = Tk_root
        self.microscope = microscope
        self.position_grid = position_grid
        self.camera = camera
        self.parameters = parameters
        self.last_positions = None

    ###########################################
    # Interface specific movements#############
    # #########################################
    
    _current_parameters_set = None

    def go_centerXY(self):
        X_center = self.microscope.dyn_Ymin + (self.microscope.dyn_Xmax - self.microscope.dyn_Xmin)/2
        Y_center = self.microscope.dyn_Ymin + (self.microscope.dyn_Ymax - self.microscope.dyn_Ymin)/2
        self.microscope.move_X_Y(X_center,Y_center) 


    #####################################################
    ##### Jobs Interface scales, coordinates, etc #######
    #####################################################
    _coordinates_job = None
    _scale_job = None
    _timelapse_job = None
    _blink = None
    _grid_record_job = None
    _job1 = None
    _job2 = None
    _job3 = None
    _video_timer = None ## This is the timer object, it is started when recording video and stopped after it should not be cleared on window change

    def clear_jobs(self): ## Clear all tk job that have been put in the job list
        jobs_list = [Interface._coordinates_job, Interface._scale_job, Interface._timelapse_job, Interface._blink, Interface._job1, Interface._job2, Interface._job3]
        for job in jobs_list:
            if job:
                self.Tk_root.after_cancel(job)
    
        Interface._coordinates_job = None
        Interface._scale_job = None
        Interface._timelapse_job = None
        Interface._job1 = None
        Interface._job2 = None
        Interface._job3 = None
        Interface._blink = None


    ######## update the label to corespond to the actual current position of the microscope
    def update_coordinates_label(self):
        self.microscope.update_real_state()
        text_coordinates = f"X: {self.microscope.XYFposition[0]}\
 Y: {self.microscope.XYFposition[1]}\
 F: {self.microscope.XYFposition[2]}\
\nLed 1: {self.microscope.led1pwr}  Led 2: {self.microscope.led2pwr}"
        
        self.Coordinates.configure(text=text_coordinates)

        if hasattr(self, 'well_info'): ## update the well_info atribute if needed
            self.well_info.configure(text=self.position_grid.current_grid_position)
        
        Interface._coordinates_job = self.after(500, self.update_coordinates_label)

    
    def save_positions(self,parameter_subset): 
        self.parameters.update_start(self.microscope.XYFposition[0],self.microscope.XYFposition[1], self.microscope.XYFposition[2],parameter_subset)
        self.position_grid.generate_grid() 

    #def guess_parameters_subset(self):
    #    if self.last_window == Interface._freemove_main:
    #        parameters_subset = "Free"
    #    elif self.last_window == Interface._grid_main:
    #        parameters_subset = plate_name   
    #    return parameters_subset

    ###################################################
    ####### Pictures, videos ##########################
    ###################################################

    def timestamp(self): ### return a timestamp for file naming
        current_time = localtime()
        date = str(current_time[0])[2:] + str(current_time[1]).zfill(2) + str(current_time[2]).zfill(2) + "_"  \
            + str(current_time[3]).zfill(2) + str(current_time[4]).zfill(2) + str(current_time[5]).zfill(2)
        
        return date

    def snap_grid(self,full_res=False):
        timestamp = self.timestamp()
        picture_name = timestamp + "_" + str(self.position_grid.current_grid_position[0]) + "-" + str(self.position_grid.current_grid_position[1])
        home = os.getenv("HOME")
        data_dir = self.parameters.get()["data_dir"]
        self.camera.capture_and_save(picture_name, f"{home}/{data_dir}")
    
    def snap_timestamp(self, full_res=False):
        picture_name = self.timestamp()
        data_dir = self.parameters.get()["data_dir"]
        home = os.getenv("HOME")
        if not full_res:
            self.camera.capture_and_save(picture_name, f"{home}/{data_dir}/img")
        else:
            self.camera.capture_full_res(picture_name, f"{home}/{data_dir}/img")
    
    def show_record_label(self):
        if Interface._video_timer:
            self.RecordingLabel = CTkLabel(self, font=("Arial", 25), text = "◉")
            self.RecordingLabel.place(x=200, y=520)
            Interface._blink = self.after(1000, self.hide_record_label)
    
    def hide_record_label(self):
        self.RecordingLabel.destroy()
        self.after(500, self.show_record_label)

    
    #############################################
    ## Window change functions ##################
    #############################################

    #Keep track of created object and recall them instead of making new
    _main_menu = None
    _led_popup = None
    _focus_popup = None
    _grid_main = None
    _plate_parameters = None
    _grid_record = None
    _freemove_main = None
    _video_record = None
    _zoom_popup = None
    _time_lapse = None
       
    def clear_frame(self):
        # destroy all widgets from frame
        for widget in self.winfo_children():
            widget.destroy()
            self.pack_forget()

    def close(self):
        self.clear_jobs()
        self.clear_frame()
        self.last_window.init_window()
    
    def back_to_main(self):
        self.clear_jobs()
        self.clear_frame()
        self._main_menu.init_window()
    
    _exit = False
    def exit(self):
        #self.clear_jobs() no need to clear jobs it is done by the root.destroy comand
        Interface._exit = True

    #############
    ###Generic buttons

    def back_to_main_button(self, position=[10,450]):
        Main = CTkButton(self, width=80, text="Main", fg_color = "firebrick", command=self.back_to_main, )
        Main.place(x=position[0],y=position[1])
    
    def coordinate_place(self, x_p=0.5, y_p=500):
        self.Coordinates = CTkLabel(self, text="test", font=("arial", 16))
        self.Coordinates.place(relx=x_p, y=y_p, anchor=N)
        self.update_coordinates_label()
    
    def snap_button(self, position=(10,350) , full_res_button = True):
        if not Interface._video_timer:
            Snap = CTkButton(self, width=80,text="Snap!", command=self.snap_timestamp)
            SnapFR = CTkButton(self,width=80, text="Full Res Picture", command=lambda: self.snap_timestamp(full_res=True))
            Snap.place(x=position[0], y=position[1])
            SnapFR.place(x=position[0] + 100 , y=position[1])
        else:
            Snap = CTkButton(self,width=80, text="Snap!", state="disabled")
            SnapFR = CTkButton(self,width=80, text="Full Res Picture", state="disabled")
            Snap.place(x=position[0], y=position[1])
            SnapFR.place(x=position[0] + 100 , y=position[1])    
        
    def back_button(self, position=(10,450)):
        Back =  CTkButton(self,width=80,  text="Back", fg_color = "firebrick", command=self.close)
        Back.place(x=position[0], y=position[1])
    #### XY slider ###

    def XYsliders(self, position=(60,20), l=220): #### Place the two navigation sliders
        self.Xvar = IntVar()
        self.Yvar = IntVar()
        Xaxis = CTkSlider(self, from_=0, to=Xmaxrange/1000, height=l, width=60, progress_color="transparent", orientation="vertical", variable=self.Xvar)  
        Yaxis = CTkSlider(self, from_=0, to=Ymaxrange/1000, height=l, width=60, progress_color="transparent", orientation="vertical", variable=self.Yvar)
        self.Xlabel = CTkLabel(self, text="##", font=("arial", 22))
        self.Ylabel = CTkLabel(self, text="##", font=("arial", 22))

        GoX =  CTkButton(self, text="Go X", width=80, height=40, command=lambda: self.microscope.move_single_axis(1, self.Xvar.get()*1000))
        GoY =  CTkButton(self, text="Go Y", width=80, height=40, command=lambda: self.microscope.move_single_axis(2, self.Yvar.get()*1000))
    
        Xaxis.place(x=position[0], y=position[1], anchor=N)
        Yaxis.place(x=position[0]+120, y=position[1], anchor=N)

        GoX.place(x=position[0], y=position[1]+l+15, anchor=N)       
        GoY.place(x=position[0]+120, y=position[1]+l+15, anchor=N)
        
        self.Xlabel.place(x=position[0], y=position[1], anchor=N)       
        self.Ylabel.place(x=position[0]+120, y=position[1], anchor=N)

        self.last_positions = None ##For scale updates
        self.set_scale(position, l) ##Continuously update scales, if positions are changed
    
    def set_scale(self, position=(60,20), l=220):
        positions = self.microscope.XYFposition
        Xvar = self.Xvar.get()
        Yvar = self.Yvar.get()
        Xlabel_scale = (position[1]+(l-30)-Xvar*((l-60)/(Xmaxrange/1000)))
        Ylabel_scale = (position[1]+(l-30)-Yvar*((l-60)/(Ymaxrange/1000)))
        if positions != self.last_positions:  #update the scale only if microscope is moving
            self.Xvar.set(positions[0]/1000)
            self.Yvar.set(positions[1]/1000)
        self.Xlabel.configure(text = Xvar)
        self.Ylabel.configure(text = Yvar)
        self.Xlabel.place(x=position[0]+45, y=Xlabel_scale, anchor=CENTER)       
        self.Ylabel.place(x=position[0]+75, y=Ylabel_scale, anchor=CENTER)
        self.last_positions = positions
        Interface._scale_job = self.after(100,lambda: self.set_scale(position, l))


    

       

    
#main loop
if __name__ == "__main__": 

    import picamera2
    from ..microscope import *
    from ..position_grid import *
    from tkinter import Tk

    microscope = Microscope(addr, ready_pin)
    position_grid = PositionsGrid(microscope)
    #start picamPreview
    camera = picamera2.PiCamera()
    #previewPiCam(camera)

    #create tkinter objects
    Tk_root = Tk()
    #interface = MainWindow(Tk_root, microscope=microscope, grid=grid, camera=camera)
    #initialise interface

    #interface.set_scale()
    #interface.get_current_coordinates()
    #Tkinter mainloop
    while not Interface._exit:

        #Tkinter mainloop
        Tk_root.update_idletasks()
        Tk_root.update()
        if Interface._exit:
            Tk_root.destroy()

