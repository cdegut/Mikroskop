import tkinter as tk
from .super import Interface
from ..parametersIO import load_parameters
from ..microscope_param import Xmaxrange, Ymaxrange
from .popup import led_focus_zoom_buttons


class FreeMovementInterface(Interface, tk.Frame):
    
    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        Interface.__init__(self, Tk_root, last_window=self, microscope=microscope, grid=grid, camera=camera)

        self.init_window(last_window)
        self.start_position = load_parameters("Free")["start"]
        

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window):
        self.last_window = last_window

        #Title of the root
        self.Tk_root.title("Control Panel")
        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)
        self.show_record_label()

        ##Generic buttons
        self.back_to_main_button()
        self.coordinate_place()
        led_focus_zoom_buttons(self)
        self.XYsliders()

        ###### Load the proper dynamic endstop for the curent window
        self.microscope.set_dynamic_endsotop(load_parameters("Free")["dyn_endstops"])

        ######### creating buttons instances      
        Start = tk.Button(self, fg='Green', text="Go Start", command=self.go_start)
        XY_center = tk.Button(self, fg='Green', text="CentXY", command=self.go_centerXY)
        Save = tk.Button(self, fg='Green', text="Save Start", command=lambda: self.save_positions("Free"))
        
        self.snap_button()
        

        
        ######## placing the elements
        ##Sliders


        Start.place(x=10,y=310)
        XY_center.place(x=110, y=310)
        #Park.place(x=140,y=300)
        
        Save.place(x=80,y=450)

    def XYsliders(self, position=(0,10)): #### Place the two navigation sliders
        GoX =  tk.Button(self, width=5, height=2, text="Go X", command=lambda: self.microscope.checked_send_motor_cmd(1, self.Xaxis.get()*1000 ))
        GoY =  tk.Button(self, width=5, height=2,  text="Go Y", command=lambda: self.microscope.checked_send_motor_cmd(2, self.Yaxis.get()*1000 ))
        self.Xaxis = tk.Scale(self, from_=0, to=Xmaxrange/1000, length=220, width=60)  
        self.Yaxis = tk.Scale(self, from_=0, to=Ymaxrange/1000, length=220, width=60)
    
        self.Xaxis.place(x=position[0], y=position[1])
        self.Yaxis.place(x=position[0]+115, y=position[1])
        GoX.place(x=position[0]+ 15, y=position[1]+230)       
        GoY.place(x=position[0]+140, y=position[1]+230)


        self.last_positions = None ##For scale updates
        self.set_scale() ##Continuously update scales, if positions are changed

    def go_start(self):
        start_position = load_parameters("Free")["start"]
        led = load_parameters("Free")["led"]
        self.microscope.go_absolute(start_position) #this function return only after arduin is ready
        self.microscope.set_ledpwr(led[0])
        self.microscope.set_led_state(led[1])

    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._freemove_main:
            Interface._freemove_main.init_window(self)
        else:
            Interface._freemove_main = FreeMovementInterface(self.Tk_root, last_window=self, microscope=self.microscope, grid=self.grid, camera=self.camera)

#main loop for testing only
if __name__ == "__main__": 
    from ..microscope import Microscope
    from ..position_grid import PositionsGrid
    from ..microscope_param import *
    from ..cameracontrol import previewPiCam

    ### Object for microscope to run
    microscope = Microscope(addr, ready_pin)
    grid = PositionsGrid(microscope)
    #camera = picamera.PiCamera()

    #Tkinter object
    Tk_root = tk.Tk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._freemove_main = FreeMovementInterface(Tk_root, last_window=None, microscope=microscope, grid=grid)

    Tk_root.mainloop()
