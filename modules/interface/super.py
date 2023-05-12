from ..cameracontrol import save_image
from ..parametersIO import load_parameters, update_parameters_start
import tkinter as tk
from ..microscope import Microscope
from ..position_grid import PositionsGrid
from time import localtime
from ..microscope_param import Xmaxrange, Ymaxrange

############
## Super class that contain shared functions for all interface windows
## and job handelers

class Interface: 

    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        tk.Frame.__init__(self, Tk_root)
        self.Tk_root = Tk_root
        self.microscope = microscope
        self.grid = grid
        self.camera = camera

        self.last_positions = None

    ###########################################
    # Interface specific movements#############
    # #########################################
          
    def go_all_axis(self, destination): #destination is an array of X Y F Led possibility to specify led state
        if len(destination) == 5: #if led state is specified
            self.microscope.set_led_state(destination[4])

        self.microscope.set_ledpwr(destination[3])    
        self.microscope.go_absolute(destination) #this function return only after arduin is ready
    
    def go_centerXY(self):
        self.microscope.checked_send_motor_cmd(1, Xmaxrange/2)
        self.microscope.checked_send_motor_cmd(2, Ymaxrange/2)

    def go_start(self):
        start_position = load_parameters()["start"]
        self.go_all_axis(start_position)
        self.grid.find_current_position()

    #####################################################
    ##### Jobs Interface scales, coordinates, etc #######
    #####################################################
    _coordinates_job = None
    _scale_job = None
    _blink = None
    _job1 = None
    _job2 = None
    _job3 = None
    _video_timer = None ## This is the timer object, it is started when recording video and stopped after it should not be cleared on window change

    def clear_jobs(self): ## Clear all tk job that have been put in the job list
        jobs_list = [Interface._coordinates_job, Interface._scale_job, Interface._blink, Interface._job1, Interface._job2, Interface._job3]
        for job in jobs_list:
            if job:
                self.Tk_root.after_cancel(job)
    
        Interface._coordinates_job = None
        Interface._scale_job = None
        Interface._job1 = None
        Interface._job2 = None
        Interface._job3 = None
        Interface._blink = None


    ######## update the label to corespond tothe actual curent position of the microscope
    def update_coordinates_label(self):
        positions = self.microscope.positions
        text_coordinates = "X: " + str(positions[0]) + "   Y: " + str(positions[1]) + "   F: " + str(positions[2]) + "\nLed "+ str(positions[4])  + ": " + str(positions[3])
        self.Coordinates.configure(text=text_coordinates)

        if hasattr(self, 'well_info'): ## update the well_info atribute if needed
            self.well_info.configure(text=self.grid.current_grid_position)
        
        Interface._coordinates_job = self.after(500, self.update_coordinates_label)

    def set_scale(self):
        positions = self.microscope.positions
        if positions != self.last_positions:       
            self.Xaxis.set(positions[0]/1000)
            self.Yaxis.set(positions[1]/1000)

        self.last_positions = positions
        Interface._scale_job = self.after(500, self.set_scale)
    
    def save_positions(self): 
        update_parameters_start(self.microscope.positions[0],self.microscope.positions[1], self.microscope.positions[2],)
        self.grid.generate_grid()    

    ###################################################
    ####### Pictures, videos ##########################
    ###################################################

    def timestamp(self): ### return a timestamp for file naming
        current_time = localtime()
        date = str(current_time[0])[2:] + str(current_time[1]).zfill(2) + str(current_time[2]).zfill(2) + "_"  \
            + str(current_time[3]).zfill(2) + str(current_time[4]).zfill(2) + str(current_time[5]).zfill(2)
        
        return date

    def snap_grid(self):
        timestamp = self.timestamp()
        picture_name = timestamp + "_" + str(self.grid.current_grid_position[0]) + "-" + str(self.grid.current_grid_position[1])
        save_image(self.camera, picture_name)
    
    def snap_timestamp(self):
        picture_name = self.timestamp()
        save_image(self.camera, picture_name)
    
    def show_record_label(self):
        if Interface._video_timer:
            self.RecordingLabel = tk.Label(self, fg = "red4", font=("Arial", 25), text = "◉")
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
       
    def clear_frame(self):
        # destroy all widgets from frame
        for widget in self.winfo_children():
            widget.destroy()
            self.pack_forget()

    def close(self):
        self.clear_jobs()
        self.clear_frame()
        self.last_window.init_window(self)
    
    def back_to_main(self):
        self.clear_jobs()
        self.clear_frame()
        self._main_menu.init_window(self)
    
    _exit = False
    def exit(self):
        #self.clear_jobs() no need to clear jobs it is done by the root.destroy comand
        Interface._exit = True

    #############
    ###Generic buttons

    def back_to_main_button(self, position=[10,450]):
        Main = tk.Button(self, fg='Red', text="Main", command=self.back_to_main)
        Main.place(x=position[0],y=position[1])
    
    def coordinate_place(self, x_p=10, y_p=500):
        self.Coordinates = tk.Label(self, text="test")
        self.Coordinates.place(x=x_p, y=y_p)
        self.update_coordinates_label()
    
    def snap_button(self, position=(10,350)):
        Snap = tk.Button(self, text="Snap!", command=self.snap_timestamp)
        Snap.place(x=position[0], y=position[1])
    
    def back_button(self, position=(10,450)):
        Back =  tk.Button(self, text="Back", command=self.close)
        Back.place(x=position[0], y=position[1])

    

       

    
#main loop
if __name__ == "__main__": 

    import picamera
    from ..microscope import *
    from ..position_grid import *

    microscope = Microscope(addr, ready_pin)
    grid = PositionsGrid(microscope)
    #start picamPreview
    camera = picamera.PiCamera()
    #previewPiCam(camera)

    #create tkinter objects
    Tk_root = tk.Tk()
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

