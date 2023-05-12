import tkinter as tk
from .super import Interface
from ..parametersIO import load_parameters
from ..microscope_param import Xmaxrange, Ymaxrange
from .popup import Led_popup, Focus_popup


class FreeMovementInterface(Interface, tk.Frame):
    
    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        tk.Frame.__init__(self, Tk_root)
        Interface.__init__(self, Tk_root, last_window=self, microscope=microscope, grid=grid, camera=camera)

        self.init_window(last_window)
        self.start_position = load_parameters()["start"]
        

    #Creation of init_window
    def init_window(self, last_window):
        self.last_window = last_window

        #Title of the root
        self.Tk_root.title("Control Panel")
        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        ##Generic buttons
        self.back_to_main_button()
        self.coordinate_place()

        ######### creating buttons instances      
        
        Focus = tk.Button(self, text="Focus", command=lambda: Focus_popup.open(self))

        ObjOn = tk.Button(self, text="ObjOn", command=lambda: self.microscope.checked_send_motor_cmd(3, self.start_position[2] ))
        ObjOff = tk.Button(self, text="ObjOff", command=lambda: self.microscope.checked_send_motor_cmd(3, 0 ))
        Ledbutton = tk.Button(self, text="Led", command=lambda: Led_popup.open(self))

        GoX =  tk.Button(self, text="Go X", command=lambda: self.microscope.checked_send_motor_cmd(1, self.Xaxis.get()*1000 ))
        GoY =  tk.Button(self, text="Go Y", command=lambda: self.microscope.checked_send_motor_cmd(2, self.Yaxis.get()*1000 ))


        Start = tk.Button(self, fg='Green', text="Start", command=self.go_start)
        Park = tk.Button(self, fg='Green', text="Park", command=lambda: self.go_all_axis([Xmaxrange, Ymaxrange/2, 0,0,0]))
        XY_center = tk.Button(self, fg='Green', text="CentXY", command=self.go_centerXY)
        Save = tk.Button(self, fg='Green', text="Save", command=self.save_positions)


        
        #Sliders
        self.Xaxis = tk.Scale(self, from_=0, to=Xmaxrange/1000, length=220, width=60)  
        self.Yaxis = tk.Scale(self, from_=0, to=Ymaxrange/1000, length=220, width=60)
        
        ######## placing the elements
        ##Sliders
        self.Xaxis.place(x=0, y=20)
        GoX.place(x=20, y=260)
        
        self.Yaxis.place(x=115, y=20)
        GoY.place(x=135, y=260)

        Start.place(x=0,y=300)
        XY_center.place(x=70, y=300)
        Park.place(x=140,y=300)
        
        Save.place(x=75,y=400)
        ObjOff.place(x=70, y=360)
        ObjOn.place(x=140, y=360)
        Focus.place(x=0, y=360)

        Ledbutton.place(x=0, y=400)

        self.last_positions = None ##For scale updates
        self.set_scale() ##Continuously update scales, if positions are changed


    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._freemove_main:
            Interface._freemove_main.init_window(self)
        else:
            Interface._freemove_main = FreeMovementInterface(self.Tk_root, last_window=self, microscope=self.microscope, grid=self.grid, camera=self.camera)