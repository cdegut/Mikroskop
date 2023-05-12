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

    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        Interface.__init__(self, Tk_root, microscope=microscope, grid=grid, camera=camera)
        self.init_window()

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window=None):
        #Geometry and title of the root  
        self.Tk_root.title("Control Panel")

        self.pack(fill=tk.BOTH, expand=1)

        #self.show_record_label()
        self.show_record_label()

        ######## Maine Menu buttons
        menu_button_w = 20
        menu_button_x = 20
        FreeMoveInterface = tk.Button(self, width=menu_button_w, text="Free Navigation", command=lambda: FreeMovementInterface.open(self))         
        GridNavigation = tk.Button(self, width=menu_button_w, text="Grid Navigation", command=lambda: MainGridInterface.open(self))
        GridRec = tk.Button(self, width=menu_button_w, text="Grid Record", command=lambda: GridRecord.open(self))
        GridParameters = tk.Button(self, width=menu_button_w, text="Plate Parameters", command=lambda:  Plate_parameters.open(self))
        VideoRecord = tk.Button(self, width=menu_button_w, text="Video", command=lambda: Video_record_window.open(self))
        Zoom = tk.Button(self, width=menu_button_w, text="Zoom", command=lambda: Zoom_popup.open(self))   
        

        FreeMoveInterface.place(x=menu_button_x, y=50)
        GridNavigation.place(x=menu_button_x, y=100)
        GridRec.place(x=menu_button_x, y=150)
        GridParameters.place(x=menu_button_x, y=200)
        VideoRecord.place(x=menu_button_x, y=250)
        Zoom.place(x=menu_button_x, y=300)

        Quit = tk.Button(self, width=menu_button_w, fg='Red', text="Quit", command=self.exit)
        Quit.place(x=menu_button_x, y=400)
        ParknQuit = tk.Button(self, width=menu_button_w, fg='Red', text="Park and Quit", command=self.parknquit)
        ParknQuit.place(x=menu_button_x, y=480)
    
    def parknquit(self):
        self.go_all_axis([Xmaxrange, Ymaxrange/2, 0,0,0])
        self.exit()
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._main_menu:
            Interface._main_menu.init_window(self)
        else:
            pass
            Interface._main_menu = MainMenu(self.Tk_root, grid=self.grid, camera=self.camera, microscope=self.microscope)