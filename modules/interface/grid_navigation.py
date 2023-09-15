from tinker import Frame, Button, BOTH, Label
from .super import Interface
from .popup import led_focus_zoom_buttons

plate_name = "Plate" ##is a place holder to later add a plate type selector, maybe

class MainGridInterface(Interface, Frame): #main GUI window
    
    def __init__(self, Tk_root, microscope, grid, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, grid=grid, camera=camera, parameters=parameters)

        self.init_window()
        self.start_position = self.parameters.get()["start"]
    
    ######Function called to open this window, generate an new object the first time, 
    ###### then recall the init_window function of the same object
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._grid_main:
            Interface._grid_main.init_window()
        else:
            Interface._grid_main = MainGridInterface(self.Tk_root, self.microscope, self.grid, self.camera, self.parameters)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):
              
        #Title of the root  
        self.Tk_root.title("Control Panel")
        
        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

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
        A1 = Button(self, width=3, heigh=2,  fg='Green', text="A1", command=lambda: self.grid.go("A1"))
        A12 = Button(self, width=3, heigh=2, text="A12", command=lambda: self.grid.go("A12"))
        H1 = Button(self, width=3, heigh=2, text="H1", command=lambda: self.grid.go("H1"))
        H12 = Button(self, width=3, heigh=2, text="H12", command=lambda: self.grid.go("H12"))
        C6 = Button(self, width=3, heigh=2, text="C6", command=lambda: self.grid.go("C6"))
        ### Pad as relative position to pad_position       
        A1.place(x=pad_position[0]-90, y=pad_position[1]-50)
        A12.place(x=pad_position[0]+70, y=pad_position[1]-50)
        H1.place(x=pad_position[0]-90, y=pad_position[1])
        H12.place(x=pad_position[0]+70, y=pad_position[1])
        C6.place(x=pad_position[0]-10, y=pad_position[1]-25)
    
    def grid_navigation_pad(self, pad_position):
        NextC = Button(self, text="Col +",  width=5, heigh=2, command=lambda: self.grid.go_next_well("column", 1))
        NextL = Button(self, text="Line +", width=5, heigh=2, command=lambda:self.grid.go_next_well("line", 1))
        PrevC = Button(self, text="Col -",  width=5, heigh=2, command=lambda: self.grid.go_next_well("column", -1))
        PrevL = Button(self, text="Line -", width=5, heigh=2, command=lambda:self.grid.go_next_well("line", -1))
        SubW = Button(self, text="Sub", command=lambda:self.grid.switch_subwell())
        self.well_info = Label(self, text="## - #")

        PrevC.place(x=pad_position[0]-90, y=pad_position[1])
        NextC.place(x=pad_position[0]+60, y=pad_position[1])
        NextL.place(x=pad_position[0]-15, y=pad_position[1]+50)
        PrevL.place(x=pad_position[0]-15, y=pad_position[1]-50)
        self.well_info.place(x=pad_position[0], y=pad_position[1]+10)
        SubW.place(x=pad_position[0]+70, y=pad_position[1]+60)


    def go_start(self):
        start_position = self.parameters.get()["start"]
        led = self.parameters.get()["led"]
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
    from tinker import Tk

    ### Object for microscope to run
    microscope = Microscope(addr, ready_pin)
    grid = PositionsGrid(microscope)
    camera = picamera.PiCamera()

    #Tkinter object
    Tk_root = Tk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._grid_main = MainGridInterface(Tk_root, last_window=None, microscope=microscope, grid=grid, camera=camera)

    #start picamPreview
    #previewPiCam(camera)

    Tk_root.mainloop()
