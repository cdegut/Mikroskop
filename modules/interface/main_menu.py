from customtkinter import CTkFrame, CTkButton, CTkLabel, CENTER, BOTH
from .super import Interface
from .freemove import FreeMovementInterface 
from .grid_navigation import MainGridInterface 
from .plate_parameters import Plate_parameters
from .grid_record import GridRecord
from .video import Video_record_window
from .timelapse import Time_lapse_window
#from .popup import Zoom_popup
from modules.controllers.pins import *


class MainMenu(Interface, CTkFrame):

    def __init__(self, Tk_root, microscope, position_grid, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, position_grid=position_grid, camera=camera, parameters=parameters)
        self.init_window()
   
    ######Function called to open this window, generate an new object the first time, 
    ###### then recall the init_window function of the same object
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._main_menu:
            Interface._main_menu.init_window()
        else:
            pass
            Interface._main_menu = MainMenu(self.Tk_root, self.microscope, self.position_grid, self.camera, self.parameters)
        
    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):
        #Geometry and title of the root  
        self.Tk_root.title("Control Panel")

        self.pack(fill=BOTH, expand=1)

        #self.show_record_label()
        self.show_record_label()

        ######## Maine Menu buttons
        self.menu_button_w = 200
        self.menu_button_x = 0.5
        FreeMoveInterface = CTkButton(self, width=self.menu_button_w, text="Free Navigation", command=lambda: FreeMovementInterface.open(self))         
        GridNavigation = CTkButton(self, width=self.menu_button_w, text="Grid Navigation", command=lambda: MainGridInterface.open(self))
        GridRec = CTkButton(self, width=self.menu_button_w, text="Grid Record", command=lambda: GridRecord.open(self))
        VideoRecord = CTkButton(self, width=self.menu_button_w, text="Video", command=lambda: Video_record_window.open(self))
        TimeLapse = CTkButton(self, width=self.menu_button_w, text="Time lapse", command=lambda: Time_lapse_window.open(self))    

        Current_parameters_set = CTkLabel(self, text = f"Selected parameter set: \n {self.parameters.name}")
        GridParameters = CTkButton(self, width=self.menu_button_w, text="Change Parameters", command=lambda:  Plate_parameters.open(self))

        FreeMoveInterface.place(relx=self.menu_button_x, y=50, anchor=CENTER)
        GridNavigation.place(relx=self.menu_button_x, y=100, anchor=CENTER)
        GridRec.place(relx=self.menu_button_x, y=150, anchor=CENTER)
        VideoRecord.place(relx=self.menu_button_x, y=200, anchor=CENTER)
        TimeLapse.place(relx=self.menu_button_x, y=250, anchor=CENTER)


        Current_parameters_set.place(relx=self.menu_button_x, y=300, anchor=CENTER)
        GridParameters.place(relx=self.menu_button_x, y=350, anchor=CENTER)


        Quit = CTkButton(self, width=self.menu_button_w, text="Quit", command=self.exit)
        Quit.place(relx=self.menu_button_x, y=450, anchor=CENTER)
        ParknQuit = CTkButton(self, width=self.menu_button_w, text="Park and Quit", command=self.parknquit)
        ParknQuit.place(relx=self.menu_button_x, y=500, anchor=CENTER)

        #self.display_image_as_label()
    
    def objective_change(self):
        self.microscope.request_XYF_travel([self.microscope.parameters.Xmaxrange, self.microscope.parameters.Ymaxrange, 0])

    def parknquit(self):
        self.microscope.request_XYF_travel([self.microscope.parameters.Xmaxrange, self.microscope.parameters.Ymaxrange/2, 0])
        self.exit()