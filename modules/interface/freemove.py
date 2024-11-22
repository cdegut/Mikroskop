from customtkinter import CTkFrame, CTkButton, BOTH
from .super import Interface
from .popup import led_focus_zoom_buttons
from modules.controllers import MicroscopeManager

class FreeMovementInterface(Interface, CTkFrame):

    def __init__(self, Tk_root, microscope: MicroscopeManager, position_grid, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, position_grid=position_grid, camera=camera, parameters=parameters)

        self.init_window()
        self.start_position = self.parameters.get()["start"]

    ######Function called to open this window, generate an new object the first time, 
    ###### then recall the init_window function of the same object
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._freemove_main:
            Interface._freemove_main.init_window()
        else:
            Interface._freemove_main = FreeMovementInterface(self.Tk_root, self.microscope, self.position_grid, self.camera, self.parameters)
        
    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):

        #Title of the root
        self.Tk_root.title("Control Panel")
        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)
        self.show_record_label()

        ##Generic buttons
        self.back_to_main_button()
        self.coordinate_place()
        led_focus_zoom_buttons(self)
        self.XYsliders()

        ######### creating buttons instances      
        Start = CTkButton(self, width=80, fg_color='Green', text="Go Start", command=self.go_start)
        XY_center = CTkButton(self,width=80,  fg_color='Green', text="CentXY", command=self.go_centerXY)
        Save = CTkButton(self,width=80,  fg_color='Green', text="Save Start",command=lambda: self.save_positions(None))
        
        self.snap_button()
                
        ######## placing the elements
        ##Sliders
        Start.place(x=10,y=310)
        XY_center.place(x=110, y=310)
        #Park.place(x=140,y=300)
        
        Save.place(x=110,y=450)

 
    def go_start(self):
        start_position = self.parameters.get()["start"]
        self.microscope.request_XYF_travel(start_position, trajectory_corection=True) #this function return only after arduin is ready
