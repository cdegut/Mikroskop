from customtkinter import CTkFrame, CTkButton, CTkLabel, BOTH, CTkOptionMenu, N
from .super import Interface
from .popup import led_focus_zoom_buttons
from .plate_parameters import Plate_parameters, ParametersConfig


class MainGridInterface(Interface, CTkFrame): #main GUI window
    
    def __init__(self, Tk_root, microscope, position_grid, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, position_grid=position_grid, camera=camera, parameters=parameters)
        self._param_config = None

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
            Interface._grid_main = MainGridInterface(self.Tk_root, self.microscope, self.position_grid, self.camera, self.parameters)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):
              
        #Title of the root  
        self.Tk_root.title("Control Panel")
        self.pack(fill=BOTH, expand=1)
        ##Generic buttons
        self.back_to_main_button()
        led_focus_zoom_buttons(self)

        ##Navigation pads as function
        self.grid_position_pad((20,20))
        self.grid_navigation_pad((20,160))
        self.coordinate_place()

        # creating buttons instances          
        self.snap_button()
        Adjust_A1 = CTkButton(self, width=80, text="Adjust A1 position", command=self.adjust_A1)
        Adjust_A1.place(x=10, y=300)

        # placing the elements

    def adjust_A1(self):
        self.clear_jobs()
        self.clear_frame()
        if self._param_config:
            self._param_config.init_window()
        else:
            pass
            self._param_config = ParametersConfig(self.Tk_root, self, self.microscope, self.position_grid, self.parameters, self.camera)
            self._param_config.mode = "A1"
            self._param_config.init_window()

    def grid_position_pad(self, pad_position):
        w = 65
        h = 30
        nlines = self.parameters.get()['lines']
        last_line = f"{self.position_grid.line_namespace[nlines-1]}1"
        last_column = f"A{self.parameters.get()['columns']}"
        opposite = f"{self.position_grid.line_namespace[nlines-1]}{self.parameters.get()['columns']}"
        center = f"{self.position_grid.line_namespace[int(nlines / 2)]}{int(self.parameters.get()['columns']/2)}"

        A1 = CTkButton(self, width=w, fg_color='Green', text="A1", command=lambda: self.position_grid.go("A1"))

        last_columnB = CTkButton(self, width=w, text=last_column, command=lambda: self.position_grid.go(last_column))
        last_lineB = CTkButton(self, width=w, text=last_line, command=lambda: self.position_grid.go(last_line))
        oppositeB = CTkButton(self, width=w, text=opposite, command=lambda: self.position_grid.go(opposite))
        centerB = CTkButton(self, width=w, text=center, command=lambda: self.position_grid.go(center))
        ### Pad as relative position to pad_position       
        A1.place(x=pad_position[0], y=pad_position[1])
        last_columnB.place(x=pad_position[0]+w*2, y=pad_position[1])
        centerB.place(x=pad_position[0]+w, y=pad_position[1]+h)
        last_lineB.place(x=pad_position[0], y=pad_position[1]+h*2)
        oppositeB.place(x=pad_position[0]+w*2, y=pad_position[1]+h*2)

    
    def grid_navigation_pad(self, pad_position):
        w = 65
        h = 40
        NextC = CTkButton(self, text="Col +",  width=w, command=lambda: self.position_grid.go_next_well("column", 1))
        NextL = CTkButton(self, text="Line +", width=w, command=lambda:self.position_grid.go_next_well("line", 1))
        PrevC = CTkButton(self, text="Col -",  width=w, command=lambda: self.position_grid.go_next_well("column", -1))
        PrevL = CTkButton(self, text="Line -", width=w, command=lambda:self.position_grid.go_next_well("line", -1))
        SubW = CTkButton(self, text="Sub", width=w, command=lambda:self.position_grid.switch_subwell())
        self.well_info = CTkLabel(self, text="## - #", font=("arial", 15))

        PrevL.place(x=pad_position[0]+w, y=pad_position[1]+h*2 )
        PrevC.place(x=pad_position[0]+w*2, y=pad_position[1]+h)
        NextC.place(x=pad_position[0], y=pad_position[1]+h)
        NextL.place(x=pad_position[0]+w, y=pad_position[1])
        self.well_info.place(x=pad_position[0]+w+w/2, y=pad_position[1]+h, anchor=N)
        SubW.place(x=pad_position[0]+w*2, y=pad_position[1]+h*2)


    def go_start(self):
        start_position = self.parameters.get()["start"]
        led = self.parameters.get()["led"]
        self.microscope.request_XYF_travel(start_position, trajectory_corection=True) #this function return only after arduin is ready
