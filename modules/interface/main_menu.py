import tkinter as tk
from .super import Interface
from .freemove import FreeMovementInterface
from .grid_navigation import MainGridInterface
from .plate_parameters import Plate_parameters
from .grid_record import GridRecord
from .video import Video_record_window
from .popup import Zoom_popup
from ..microscope_param import Xmaxrange, Ymaxrange


class MainMenu(Interface, tk.Frame):

    def __init__(self, Tk_root, microscope, grid, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, grid=grid, camera=camera, parameters=parameters)
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
            Interface._main_menu = MainMenu(self.Tk_root, self.microscope, self.grid, self.camera, self.parameters)
        
    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):
        #Geometry and title of the root  
        self.Tk_root.title("Control Panel")

        self.pack(fill=tk.BOTH, expand=1)

        #self.show_record_label()
        self.show_record_label()

        ######## Maine Menu buttons
        self.menu_button_w = 20
        self.menu_button_x = 20
        FreeMoveInterface = tk.Button(self, width=self.menu_button_w, text="Free Navigation", command=lambda: FreeMovementInterface.open(self))         
        GridNavigation = tk.Button(self, width=self.menu_button_w, text="Grid Navigation", command=lambda: MainGridInterface.open(self))
        GridRec = tk.Button(self, width=self.menu_button_w, text="Grid Record", command=lambda: GridRecord.open(self))
        VideoRecord = tk.Button(self, width=self.menu_button_w, text="Video", command=lambda: Video_record_window.open(self))       

        Current_parameters_set = tk.Label(self, text = f"Selected parameter set: \n {self.parameters.selected}")
        GridParameters = tk.Button(self, width=self.menu_button_w, text="Change Parameters", command=lambda:  Plate_parameters.open(self))

        FreeMoveInterface.place(x=self.menu_button_x, y=50)
        GridNavigation.place(x=self.menu_button_x, y=100)
        GridRec.place(x=self.menu_button_x, y=150)
        VideoRecord.place(x=self.menu_button_x, y=200)

        Current_parameters_set.place(x=self.menu_button_x+15, y=300)
        GridParameters.place(x=self.menu_button_x, y=350)


        Quit = tk.Button(self, width=self.menu_button_w, fg='Red', text="Quit", command=self.exit)
        Quit.place(x=self.menu_button_x, y=450)
        ParknQuit = tk.Button(self, width=self.menu_button_w, fg='Red', text="Park and Quit", command=self.parknquit)
        ParknQuit.place(x=self.menu_button_x, y=500)
    
    def parknquit(self):
        self.microscope.go_absolute([Xmaxrange, Ymaxrange/2, 0])
        self.micrscope.set_ledpwr(0)
        self.micrscope.set_led_state(0)
        self.exit()