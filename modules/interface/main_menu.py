import tkinter as tk
from .super import Interface
from .freemove import FreeMovementInterface
from .grid_navigation import MainGridInterface
from .plate_parameters import Plate_parameters
from .grid_record import GridRecord
from .video import Video_record_window
from .popup import Zoom_popup


class MainMenu(Interface, tk.Frame):

    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        tk.Frame.__init__(self, Tk_root)
        Interface.__init__(self, Tk_root, microscope=microscope, grid=grid, camera=camera)
        self.init_window()

    #Creation of init_window
    def init_window(self, last_window=None):
        #Geometry and title of the root  
        self.Tk_root.title("Control Panel")

        self.pack(fill=tk.BOTH, expand=1)

        FreeMoveInterface = tk.Button(self, text="Free Navigation", command=lambda: FreeMovementInterface.open(self))         
        GridNavigation = tk.Button(self, text="Grid Navigation", command=lambda: MainGridInterface.open(self))
        GridRec = tk.Button(self, text="Grid Record", command=lambda: GridRecord.open(self))
        GridParameters = tk.Button(self, text="Plate Parameters", command=lambda:  Plate_parameters.open(self))
        VideoRecord = tk.Button(self, text="Video", command=lambda: Video_record_window.open(self))

        Zoom = tk.Button(self, text="Zoom", command=lambda: Zoom_popup.open(self))
       
        Quit = tk.Button(self, fg='Red', text="Quit", command=self.exit)

        FreeMoveInterface.place(x=50, y=50)
        GridNavigation.place(x=50, y=100)
        GridRec.place(x=50, y=150)
        GridParameters.place(x=50, y=200)
        VideoRecord.place(x=50, y=250)
        Zoom.place(x=50, y=300)

        Quit.place(x=10, y=400)
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._main_menu:
            Interface._main_menu.init_window(self)
        else:
            pass
            Interface._main_menu = MainMenu(self.Tk_root, grid=self.grid, camera=self.camera, microscope=self.microscope)