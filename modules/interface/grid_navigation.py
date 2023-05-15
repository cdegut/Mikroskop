import tkinter as tk
from ..parametersIO import load_parameters
from .super import Interface
from ..microscope_param import Xmaxrange, Ymaxrange
from .popup import led_focus_zoom_buttons

plate_name = "Plate" ##is a place holder to later add a plate type selector, maybe

class MainGridInterface(Interface, tk.Frame): #main GUI window
    
    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        Interface.__init__(self, Tk_root, last_window=self, microscope=microscope, grid=grid, camera=camera)

        self.init_window(last_window)
        self.start_position = load_parameters(plate_name)["start"]

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window):
        self.last_window = last_window
              
        #Title of the root  
        self.Tk_root.title("Control Panel")
        
        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        ###### Load the proper dynamic endstop for the curent window
        self.microscope.set_dynamic_endsotop(load_parameters(plate_name)["dyn_endstops"])

        ##Generic buttons
        self.back_to_main_button()
        led_focus_zoom_buttons(self)

        ##Navigation pads as function
        self.grid_position_pad((100,60))
        self.grid_navigation_pad((100,220))
        self.coordinate_place()

        # creating buttons instances          
        self.snap_button()

        # placing the elements

    
    def grid_position_pad(self, pad_position):
        A1 = tk.Button(self, width=3, heigh=2,  fg='Green', text="A1", command=lambda: self.grid.go("A1"))
        A12 = tk.Button(self, width=3, heigh=2, text="A12", command=lambda: self.grid.go("A12"))
        H1 = tk.Button(self, width=3, heigh=2, text="H1", command=lambda: self.grid.go("H1"))
        H12 = tk.Button(self, width=3, heigh=2, text="H12", command=lambda: self.grid.go("H12"))
        C6 = tk.Button(self, width=3, heigh=2, text="C6", command=lambda: self.grid.go("C6"))
        ### Pad as relative position to pad_position       
        A1.place(x=pad_position[0]-90, y=pad_position[1]-50)
        A12.place(x=pad_position[0]+70, y=pad_position[1]-50)
        H1.place(x=pad_position[0]-90, y=pad_position[1])
        H12.place(x=pad_position[0]+70, y=pad_position[1])
        C6.place(x=pad_position[0]-10, y=pad_position[1]-25)
    
    def grid_navigation_pad(self, pad_position):
        NextC = tk.Button(self, text="Col +",  width=5, heigh=2, command=lambda: self.grid.go_next_well("column", 1))
        NextL = tk.Button(self, text="Line +", width=5, heigh=2, command=lambda:self.grid.go_next_well("line", 1))
        PrevC = tk.Button(self, text="Col -",  width=5, heigh=2, command=lambda: self.grid.go_next_well("column", -1))
        PrevL = tk.Button(self, text="Line -", width=5, heigh=2, command=lambda:self.grid.go_next_well("line", -1))
        SubW = tk.Button(self, text="Sub", command=lambda:self.grid.switch_subwell())
        self.well_info = tk.Label(self, text="## - #")

        PrevC.place(x=pad_position[0]-90, y=pad_position[1])
        NextC.place(x=pad_position[0]+60, y=pad_position[1])
        NextL.place(x=pad_position[0]-15, y=pad_position[1]+50)
        PrevL.place(x=pad_position[0]-15, y=pad_position[1]-50)
        self.well_info.place(x=pad_position[0], y=pad_position[1]+10)
        SubW.place(x=pad_position[0]+70, y=pad_position[1]+60)
   
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._grid_main:
            Interface._grid_main.init_window(self)
        else:
            Interface._grid_main = MainGridInterface(self.Tk_root, grid=self.grid, camera=self.camera,  microscope=self.microscope)
    
    def go_start(self):
        start_position = load_parameters("Free")["start"]
        led = load_parameters("Free")["led"]
        self.microscope.go_absolute(start_position) #this function return only after arduin is ready
        self.microscope.set_ledpwr(led[0])
        self.microscope.set_led_state(led[1])


#main loop for testing only
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
    Interface._grid_main = MainGridInterface(Tk_root, last_window=None, microscope=microscope, grid=grid, camera=camera)

    #start picamPreview
    #previewPiCam(camera)

    Tk_root.mainloop()
