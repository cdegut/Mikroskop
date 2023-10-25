from customtkinter import CTkFrame, CTkButton, CTkSlider, BOTH, N, CENTER, IntVar, CTkLabel
from .super import Interface
from .popup import led_focus_zoom_buttons


class FreeMovementInterface(Interface, CTkFrame):

    def __init__(self, Tk_root, microscope, grid, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, grid=grid, camera=camera, parameters=parameters)

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
            Interface._freemove_main = FreeMovementInterface(self.Tk_root, self.microscope, self.grid, self.camera, self.parameters)
        
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
        
        Save.place(x=80,y=450)

 
    def go_start(self):
        start_position = self.parameters.get()["start"]
        led = self.parameters.get()["led"]
        self.microscope.go_absolute(start_position) #this function return only after arduin is ready
        self.microscope.set_ledpwr(led[0])
        self.microscope.set_led_state(led[1])

#main loop
if __name__ == "__main__": 
    from modules.cameracontrol3 import Microscope_camera
    from modules.microscope import Microscope
    from modules.position_grid import PositionsGrid
    from modules.physical_controller import encoder_read, controller_startup
    from modules.interface.main_menu import *
    from modules.microscope_param import *
    from modules.parametersIO import ParametersSets, create_folder
    import customtkinter
    ### Object for microscope to run

    #Tkinter object
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin, parameters)
    grid = PositionsGrid(microscope, parameters)
    micro_cam = None

    #Tkinter object
    customtkinter.set_appearance_mode("dark")
    Tk_root = customtkinter.CTk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._freemove_main = FreeMovementInterface(Tk_root, microscope=microscope, grid=grid, camera=None, parameters=parameters)

    Tk_root.mainloop()

