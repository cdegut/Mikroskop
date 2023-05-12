import tkinter as tk
from ..parametersIO import load_parameters
from .super import Interface
from ..microscope_param import Xmaxrange, Ymaxrange
from .popup import Led_popup, Focus_popup


class MainGridInterface(Interface, tk.Frame): #main GUI window
    
    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        tk.Frame.__init__(self, Tk_root)
        Interface.__init__(self, Tk_root, last_window=self, microscope=microscope, grid=grid, camera=camera)

        self.init_window(last_window)
        self.start_position = load_parameters()["start"]

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window):
        self.last_window = last_window
              
        #Title of the root  
        self.Tk_root.title("Control Panel")
        
        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        ##Generic buttons
        self.back_to_main_button()
        self.coordinate_place()

        # creating buttons instances           

        Focus = tk.Button(self, text="Focus", command=lambda: Focus_popup.open(self))
        ObjOn = tk.Button(self, text="ObjOn", command=lambda: self.microscope.checked_send_motor_cmd(3, self.start_position[2] ))
        ObjOff = tk.Button(self, text="ObjOff", command=lambda: self.microscope.checked_send_motor_cmd(3, 0 ))
        
        Ledbutton = tk.Button(self, text="Led", command=lambda: Led_popup.open(self))

        Start = tk.Button(self, fg='Green', text="Start", command=self.go_start)
        H12 = tk.Button(self, text="go H12", command=lambda: self.grid.go("H12"))
        C6 = tk.Button(self, text="go C6", command=lambda: self.grid.go("C6"))

        NextC = tk.Button(self, text="Col +", command=lambda: self.grid.go_next_well("column", 1))
        NextL = tk.Button(self, text="Line +", command=lambda:self.grid.go_next_well("line", 1))
        PrevC = tk.Button(self, text="Col -", command=lambda: self.grid.go_next_well("column", -1))
        PrevL = tk.Button(self, text="Line -", command=lambda:self.grid.go_next_well("line", -1))

        SubW = tk.Button(self, text="Sub", command=lambda:self.grid.switch_subwell())

        Park = tk.Button(self, fg='Green', text="Park", command=lambda: self.go_all_axis([Xmaxrange, Ymaxrange/2, 0,0]))

        Snap = tk.Button(self, text="Snap!", command=self.snap_grid)

        self.well_info = tk.Label(self, text="## - #")
        
        
        # placing the elements
        Start.place(x=0,y=10)
        H12.place(x=150, y=10)
        C6.place(x=75, y=10)

        PrevC.place(x=10, y=100)
        NextC.place(x=150, y=100)
        NextL.place(x=75, y=60)
        PrevL.place(x=75, y=140)
        self.well_info.place(x=90, y=105)
        SubW.place(x=150, y=140)


        Park.place(x=0,y=190)

        ObjOff.place(x=70, y=360)
        ObjOn.place(x=140, y=360)
        Focus.place(x=0, y=360)

        Ledbutton.place(x=0, y=400)

        Snap.place(x=135,y=450)

    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._grid_main:
            Interface._grid_main.init_window(self)
        else:
            Interface._grid_main = MainGridInterface(self.Tk_root, grid=self.grid, camera=self.camera,  microscope=self.microscope)
    