from tkinter import Frame, Button, Label
from ..microscope import Microscope
from ..position_grid import PositionsGrid
from time import localtime


plate_name = "Plate" ##is a place holder to later add a plate type selector, maybe

############
## Super class that contain shared functions for all interface windows
## and job handelers

class Interface: 

    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None, parameters=None):
        Frame.__init__(self, Tk_root)
        self.Tk_root = Tk_root
        self.microscope = microscope
        self.grid = grid
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


    ######## update the label to corespond to the actual curent position of the microscope
    def update_coordinates_label(self):
        if self.microscope.is_ready():
            self.microscope.positions = self.microscope.checked_read_positions()
        
        positions = self.microscope.positions
        text_coordinates = "X: " + str(positions[0]) + "   Y: " + str(positions[1]) + "   F: " + str(positions[2]) + "\nLed "+ str(positions[4])  + ": " + str(positions[3])
        self.Coordinates.configure(text=text_coordinates)

        if hasattr(self, 'well_info'): ## update the well_info atribute if needed
            self.well_info.configure(text=self.grid.current_grid_position)
        
        Interface._coordinates_job = self.after(500, self.update_coordinates_label)

    ########## Handel the scale that allow large movements
    def set_scale(self):
        positions = self.microscope.positions
        if positions != self.last_positions:       
            self.Xaxis.set(positions[0]/1000)
            self.Yaxis.set(positions[1]/1000)

        self.last_positions = positions
        Interface._scale_job = self.after(500, self.set_scale)
    
    def save_positions(self,parameter_subset): 
        self.parameters.update_start(self.microscope.positions[0],self.microscope.positions[1], self.microscope.positions[2],parameter_subset)
        self.grid.generate_grid() 

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
        picture_name = timestamp + "_" + str(self.grid.current_grid_position[0]) + "-" + str(self.grid.current_grid_position[1])
        data_dir = self.parameters.get()["data_dir"]
        self.camera.capture_and_save(picture_name, data_dir, full_res)
    
    def snap_timestamp(self, full_res=False):
        picture_name = self.timestamp()
        data_dir = self.parameters.get()["data_dir"]
        if full_res:
            self.camera.capture_and_save(picture_name, f"{data_dir}/img")
        else:
            self.camera.capture_full_res(picture_name, f"{data_dir}/img")
    
    def show_record_label(self):
        if Interface._video_timer:
            self.RecordingLabel = Label(self, fg = "red4", font=("Arial", 25), text = "◉")
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
        Main = Button(self, fg='Red', text="Main", command=self.back_to_main)
        Main.place(x=position[0],y=position[1])
    
    def coordinate_place(self, x_p=10, y_p=500):
        self.Coordinates = Label(self, text="test")
        self.Coordinates.place(x=x_p, y=y_p)
        self.update_coordinates_label()
    
    def snap_button(self, position=(10,350) , full_res_button = True):
        if not Interface._video_timer:
            Snap = Button(self, text="Snap!", command=self.snap_timestamp)
            SnapFR = Button(self, text="Full Res Picture", command=lambda: self.snap_timestamp(full_res=True))
            Snap.place(x=position[0], y=position[1])
            SnapFR.place(x=position[0] + 70 , y=position[1])
        else:
            Snap = Button(self, text="Snap!", fg="Red")
            SnapFR = Button(self, text="Full Res Picture", fg="Red")
            Snap.place(x=position[0], y=position[1])
            SnapFR.place(x=position[0] + 70 , y=position[1])    
        
    def back_button(self, position=(10,450)):
        Back =  Button(self, text="Back", command=self.close)
        Back.place(x=position[0], y=position[1])

    

       

    
#main loop
if __name__ == "__main__": 

    import picamera
    from ..microscope import *
    from ..position_grid import *
    from tkinter import Tk

    microscope = Microscope(addr, ready_pin)
    grid = PositionsGrid(microscope)
    #start picamPreview
    camera = picamera.PiCamera()
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

