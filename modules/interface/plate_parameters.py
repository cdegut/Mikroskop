from customtkinter import CTkFrame, CTkButton, CTkLabel, BOTH, CTkOptionMenu, N, StringVar, CTk
from .super import Interface
from .popup import led_focus_zoom_buttons
from modules.controllers import *


class Plate_parameters(Interface,CTkFrame):
    def __init__(self, Tk_root, microscope:MicroscopeManager , position_grid, camera, parameters: GridParameters):
        Interface.__init__(self, Tk_root, microscope=microscope, position_grid=position_grid, camera=camera, parameters=parameters)
        self._param_config = ParametersConfig(self.Tk_root, self, self.microscope, self.position_grid, self.parameters, self.camera)
        self.init_window()

    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._plate_parameters:
            Interface._plate_parameters.init_window()
        else:
            pass
            Interface._plate_parameters = Plate_parameters(self.Tk_root, self.microscope, self.position_grid, self.camera, self.parameters)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):
 
        self.Tk_root.title("Grid") 
        self.pack(fill=BOTH, expand=1)

        self.Xsteps = self.parameters.Xsteps
        self.Ysteps = self.parameters.Ysteps
        self._param_config.Xold_steps = self.Xsteps
        self._param_config.Yold_steps = self.Ysteps

        self.subwells_spacing = self.parameters.subwells_spacing

        self.parameter_menu(20,10)
        self.lines_columns_subwels(20,80)
        self.XYstep_config_buttons(10,260)
        self.A1_button(10,350)
        self.focus_button(10,420)
        self.back_to_main_button([10, 520])

    def XYstep_config_buttons(self, x_p, y_p):

        TopLabel = CTkLabel(self, text="Grid distances:")
        stepsLabel = CTkLabel(self, text=f"X steps: {str(self.Xsteps)}     Y steps: {str(self.Ysteps)}")
        Configure_XY =  CTkButton(self, text="Configure X and Y step", command=self.set_steps)

        TopLabel.place(x=x_p, y=y_p)
        stepsLabel.place(x=x_p, y=y_p+20)
        Configure_XY.place(relx=0.5, y=y_p+50, anchor=N)

    def A1_button(self, x_p, y_p):
        A1X = self.parameters.start[0]
        A1Y = self.parameters.start[1]
        A1Label = CTkLabel(self, text=f"A1 position X: {A1X} Y: {A1Y}")
        A1position =  CTkButton(self, text="Change A1 position", command=self.set_A1_position)
        A1Label.place(x=x_p, y=y_p)
        A1position.place(relx=0.5, y=y_p+30, anchor=N)
    
    def focus_button(self, x_p, y_p):
        FocusX = self.parameters.XYFocusDrift[0]
        FocusY = self.parameters.XYFocusDrift[1]
        DriftX = self.parameters.XYaxisSkew[0]
        DriftY = self.parameters.XYaxisSkew[1]
        Label = CTkLabel(self, text=f"Focus drift X: {FocusX} Y: {FocusY}\nAxes skew X: {DriftX} Y: {DriftY}")
        fs =  CTkButton(self, text="Set Focus drift \nand axes skew", command=self.set_focus_drift)
        Label.place(x=x_p, y=y_p)
        fs.place(relx=0.5, y=y_p+40, anchor=N)
       
    def lines_columns_subwels(self, x_p=10, y_p=10):
        
        self.lines = StringVar()
        self.columns = StringVar()
        self.subwells = StringVar()


        TopLabel = CTkLabel(self, text="Grid characteristics:")
        LinesLabel = CTkLabel(self, text="Lines:")

        w=40
        LinesMenu = CTkOptionMenu(self, width=w, variable=self.lines, values=["2","3","4","8","16"])
        ColumnsLabel = CTkLabel(self, text="Columns:")
        ColumnsMenu = CTkOptionMenu(self, width=w, variable=self.columns, values=["3","4","6","12","24"])
        SubWellsLabel = CTkLabel(self, text="Subwells:")
        SubWellsMenu = CTkOptionMenu(self, width=w, variable=self.subwells, values=["1","2","3","4"])

        self.lines.set(self.parameters.lines)
        self.columns.set(self.parameters.columns)
        self.subwells.set(self.parameters.subwells)

        #Save = CTkButton(self, text="Save changes", command=self.save_grid_param)
        New = CTkButton(self, text="New Parameter Set",  command=self.new_grid_param)
        Delete = CTkButton(self, text="Delete Current",  command=self.delete_grid_param)
        
        TopLabel.place(x=x_p, y=y_p)
        y_p = y_p +20
        LinesLabel.place(x=x_p+5, y=y_p)
        LinesMenu.place(x=x_p, y=y_p+20)
        ColumnsLabel.place(x=x_p+70, y=y_p)
        ColumnsMenu.place(x=x_p+70, y=y_p+20)
        SubWellsLabel.place(x=x_p+140, y=y_p)
        SubWellsMenu.place(x=x_p+140, y=y_p+20)
        #Save.place(relx=0.5, y=y_p+60, anchor=N)
        New.place(relx=0.5, y=y_p+60, anchor=N)
        Delete.place(relx=0.5, y=y_p+90, anchor=N)

    def parameter_menu(self, x_p, y_p):
        self.parameters_selector = StringVar()
        self.parameters_selector.set(self.parameters.name)
        parameters_set_list = list_all_parameters()

        ParametersSet = CTkOptionMenu(self, width=100, variable=self.parameters_selector, values=parameters_set_list,  command=self.parameter_set_changed)
        ParametersSet_label =  CTkLabel(self, text="Parameters set:")
        ParametersSet_label.place(x=x_p, y=y_p)
        ParametersSet.place(x=x_p, y=y_p+30)
    
    def parameter_set_changed(self, new_param):
        self.parameters.load(new_param)
        self.position_grid.generate_grid()
        endstops_dict = self.parameters.dyn_endstops ## Load the specific dynamic endstops
        self.microscope.set_dynamic_endsotop(endstops_dict)
        self.clear_frame()
        self.init_window()

    def save_grid_param(self):
        self.parameters.lines = int(self.lines.get())
        self.parameters.columns= int(self.columns.get())
        self.parameters.subwells=int(self.subwells.get())
        self.parameters.save()
        self.position_grid.generate_grid()
    
    def new_grid_param(self):
        l = int(self.lines.get())
        c = int(self.columns.get())
        s = int(self.subwells.get())
        i=1
        name = f"{l}-{c}-{s}-({i})"

        while name in list_all_parameters():
            i += 1
            name = f"{l}-{c}-{s}-({i})"
        
        self.parameters.save(name)
        self.parameters.load(name)

        Y_ratio = self.parameters.columns/c
        X_ratio = self.parameters.lines/l

        self.parameters.name
        oldX = self.parameters.Xsteps
        oldY = self.parameters.Ysteps
        self.parameters.protected = False
        self.parameters.Xsteps =  int(oldX * X_ratio)
        self.parameters.Ysteps = int(oldY * Y_ratio)

        self.save_grid_param()
        self.init_window()

    def delete_grid_param(self):
        self.parameters.delete(self.parameters.name)
        self.parameters.load("Default")
        self.init_window()

    def set_steps(self):
        self.clear_frame()
        self._param_config.mode = "steps"
        self._param_config.init_window()
    
    def set_A1_position(self):
        self.clear_frame()
        self._param_config.mode = "A1"
        self._param_config.init_window()
    
    def set_focus_drift(self):
        self.clear_frame()
        self._param_config.mode = "Focus"
        self._param_config.init_window()

    def set_dyn_endstop_position(self):
        self.clear_frame()
        self._param_config.init_window()        

class ParametersConfig(Interface, CTkFrame):

    def __init__(self, Tk_root, last_window, microscope, position_grid, parameters, camera, Xsteps= None, Ysteps = None):
        Interface.__init__(self, Tk_root, last_window, microscope=microscope, position_grid=position_grid, camera=camera, parameters=parameters)
        self.last_window = last_window      
        self.Tk_window = Tk_root
        self.Xold_steps = Xsteps
        self.Yold_steps = Ysteps
        self.XFocusold_steps = None
        self.YFocusold_steps = None
        self.mode = None

   #Creation of init_window
    def init_window(self):

        self.Tk_window.title("Steps") 
        self.pack(fill=BOTH, expand=1)
        self.show_record_label()
        self.start = self.parameters.start 
            
        Cancel = CTkButton(self, text="Back", command=self.close)
        
        if self.mode == "steps":
            self.grid_go_pad((100,340))
            self.XYsliders(l=200)
            self.save_XY_buttons(menus_position= (10,380))
            Cancel.place(x=10,y=520)
        if self.mode == "A1":
            self.XYsliders(l=200)
            self.A1_config_button()
            Cancel.place(x=10,y=450)
            self.coordinate_place()
        if self.mode == "Focus":
            self.focus_skew_buttons((10,10))
            Cancel.place(x=10,y=450)
            self.coordinate_place()
    
    def grid_go_pad(self, pad_position):
        w = 65
        A1 = CTkButton(self, width=w,text="A1", command=lambda: self.position_grid.go("A1"))        
        w = 65
        h = 30
        nlines = self.parameters.lines
        ncolumns = self.parameters.columns
        last_line = f"{self.position_grid.line_namespace[nlines-1]}1"
        last_column = f"A{ncolumns}"
        opposite = f"{self.position_grid.line_namespace[nlines-1]}{ncolumns}"
        center = f"{self.position_grid.line_namespace[int(nlines / 2)]}{int(ncolumns/2)}"

        A1 = CTkButton(self, width=w, fg_color='Green', text="A1", command=lambda: self.position_grid.go("A1"))
        last_columnB = CTkButton(self, width=w, text=last_column, command=lambda: self.go_and_change_divisor(last_column, [1,ncolumns-1]))
        last_lineB = CTkButton(self, width=w, text=last_line, command=lambda: self.go_and_change_divisor(last_line, [nlines -1, 1]))
        oppositeB = CTkButton(self, width=w, text=opposite, command=lambda: self.go_and_change_divisor(opposite, [nlines -1, ncolumns -1] ))
        centerB = CTkButton(self, width=w, text=center, command=lambda: self.position_grid.go(center))
        
        ### Pad as relative position to pad_position       
        A1.place(x=pad_position[0]-90, y=pad_position[1]-50)
        last_columnB.place(x=pad_position[0]+60, y=pad_position[1]-50)
        last_lineB.place(x=pad_position[0]-90, y=pad_position[1])
        oppositeB.place(x=pad_position[0]+60, y=pad_position[1])
        centerB.place(x=pad_position[0]-15, y=pad_position[1]-25)
    
    def go_and_change_divisor(self, position, div):      
        self.position_grid.go(position)
        self.divisorX.set(div[0])
        self.divisorY.set(div[1])
       
    ### Panel only for setting up X Y steps
    def save_XY_buttons(self, menus_position):
        self.divisorX = StringVar()
        self.divisorY = StringVar()
        self.divisorX.set(7)
        self.divisorY.set(11)
 
        DivisorXLabel = CTkLabel(self, text="Divisor X")
        DivisorXMenu = CTkOptionMenu(self, width=40,  variable=self.divisorX, values=["      1   ","      2   ","      5   ","      7    ", "      15    ",])
        DivisorYLabel = CTkLabel(self, text="Divisor Y")
        DivisorYMenu = CTkOptionMenu(self,  width=40, variable=self.divisorY, values=["      1   ","      2   ","      5   ","      11   ","      23   "])
        
        self.XSteps_label = CTkLabel(self, text="test")
        self.YSteps_label = CTkLabel(self, text="test")
        SaveX =  CTkButton(self, text="Save X",  width=80, command=lambda:  self.save_measure(x=True))
        SaveY =  CTkButton(self, text="Save Y",  width=80, command=lambda: self.save_measure(y=True))

        DivisorXLabel.place(x=menus_position[0], y=menus_position[1])
        DivisorXMenu.place(x=menus_position[0], y=menus_position[1]+20)
        DivisorYLabel.place(x=menus_position[0]+125, y=menus_position[1])
        DivisorYMenu.place(x=menus_position[0]+125, y=menus_position[1]+20)       
        self.XSteps_label.place(x=menus_position[0], y=menus_position[1]+60)
        self.YSteps_label.place(x=menus_position[0]+125, y=menus_position[1]+60)
        SaveX.place(x=menus_position[0], y=menus_position[1]+100)
        SaveY.place(x=menus_position[0]+125, y=menus_position[1]+100)
        
        self.label_update()

    def focus_skew_buttons(self, menus_position):
        w = 90
        nlines = self.parameters.lines
        last_line = f"{self.position_grid.line_namespace[nlines-1]}1"
        last_column = f"A{self.parameters.columns}"

        ExplanationLabel = CTkLabel(self, text="Use the button to go to end of line \n Adjust focus, position, and save. \nRepeat for columns")
        ExplanationLabel.place(relx=0.5,y=menus_position[1])

        Xlabel = CTkLabel(self, text="Focus drift and skew in X:")
        goX = CTkButton(self, width=w,text=f"go to {last_line} (last line)", command=lambda: self.position_grid.go(last_line))
        saveXdrift = CTkButton(self, width=w,text=f"Save X \nFocus drift", command=lambda: self.save_focus_drift("X"))
        saveYskew = CTkButton(self, width=w,text=f"Save Y \naxis skew", command=lambda: self.save_axis_skew("Y"))



        Ylabel = CTkLabel(self, text="Focus drift and skew in Y:")
        goY = CTkButton(self, width=w,text=f"go to {last_column} (last column)", command=lambda: self.position_grid.go(last_column))
        saveYdrift = CTkButton(self, width=w,text=f"Save Y \nFocus drift", command=lambda: self.save_focus_drift("Y"))
        saveXskew = CTkButton(self, width=w,text=f"Save X \naxis skew", command=lambda: self.save_axis_skew("X"))

        offset = 5
        Xlabel.place(x=menus_position[0],y=menus_position[1]+60)
        goX.place(relx=0.5,y=menus_position[1]+90, anchor=N)
        saveXdrift.place(x=menus_position[0] + offset,y=menus_position[1]+130)
        saveYskew.place(x=menus_position[0]+ w +20 + offset,y=menus_position[1]+130)
        
        Ylabel.place(x=menus_position[0],y=menus_position[1]+180)
        goY.place(relx=0.5,y=menus_position[1]+210, anchor=N)
        saveYdrift.place(x=menus_position[0] + offset,y=menus_position[1]+250)
        saveXskew.place(x=menus_position[0]+ w +20 + offset,y=menus_position[1]+250)


        Fp25 = CTkButton(self, width=80,text="Fcs +25 ", command=lambda: self.microscope.request_push_axis("F",25))
        Fm25 = CTkButton(self, width=80,text="Fcs -25 ", command=lambda: self.microscope.request_push_axis("F",-25))

        Fp5 = CTkButton(self, width=80,text="Fcs +5  ", command=lambda: self.microscope.request_push_axis("F",5))
        Fm5 = CTkButton(self, width=80,text="Fcs -5  ", command=lambda: self.microscope.request_push_axis("F",-5))

        Fp25.place(x=menus_position[0],y=menus_position[1]+350)
        Fm25.place(x=menus_position[0]+100,y=menus_position[1]+350)
        Fp5.place(x=menus_position[0],y=menus_position[1]+390)
        Fm5.place(x=menus_position[0]+100,y=menus_position[1]+390)

    def save_focus_drift(self, axis):
        if axis == "X":
            divisor = self.parameters.lines -1
        if axis == "Y":
            divisor = self.parameters.columns - 1

        drift = int( (self.microscope.XYFposition[2] - self.start[2]) / divisor)
        
        if axis == "X":
            XYdrift = drift, self.parameters.XYFocusDrift[1]
            self.parameters.XYFocusDrift =  XYdrift
        if axis == "Y":
            XYdrift = self.parameters.XYFocusDrift[0] = drift
            self.parameters.XYFocusDrift = XYdrift
        
        self.parameters.save()
        self.position_grid.generate_grid()
    
    def save_axis_skew(self, axis):
        if axis == "X":
            divisor = self.parameters.lines -1.
            skew = int( (self.microscope.XYFposition[0] - self.start[0]) / divisor)
        if axis == "Y":
            divisor = self.parameters.columns - 1
            skew = int( (self.microscope.XYFposition[1] - self.start[1]) / divisor)
        
        if axis == "X":
            XYskew = skew, self.parameters.XYaxisSkew[1]
            self.parameters.XYaxisSkew = XYskew
        if axis == "Y":
            XYskew = self.parameters.XYaxisSkew[0] = skew
            self.parameters.XYaxisSkew = XYskew
        
        self.parameters.save()
        self.position_grid.generate_grid()
    
        
    ### Panel only for setting up A1 position
    def A1_config_button(self):

        A1 = CTkButton(self, width=40,text="Go Current A1", command=lambda: self.position_grid.go("A1"))

        self.A1Label = CTkLabel(self, text=f"Current A1 position:\nX: {self.parameters.start[0]} Y: {self.parameters.start[1]} F: {self.parameters.start[2]}")       
        self.A1Label.place(x=10, y=280)
        A1.place(x=10, y=320)


        SaveA1 = CTkButton(self, text="Save A1 center", command=self.save_A1)
        SaveA1.place(x=10,y=400)
        led_focus_zoom_buttons(self, 360)

    def save_A1(self):
        self.microscope.update_real_state()
        start = self.microscope.XYFposition
        self.parameters.start =start
        self.start = start
        self.A1Label.configure(text=f"Current A1 position:\nX: {self.parameters.start[0]} Y: {self.parameters.start[1]} F: {self.parameters.start[2]}")
        self.parameters.save()
        self.position_grid.generate_grid()

    def measure(self):
        self.microscope.update_real_state() 
        self.Xsteps = int( (self.microscope.XYFposition[0] - self.start[0]) / int(self.divisorX.get()))
        self.Ysteps = int( (self.microscope.XYFposition[1] - self.start[1]) / int(self.divisorY.get()))
    
    def measure_focus(self):
        self.microscope.update_real_state() 
        self.Fsteps = int( (self.microscope.XYFposition[2] - self.start[2]) / int(self.divisorX.get()))
    
    def label_update(self):
        self.measure()
        self.XSteps_label.configure(text="Current X: " + str(self.Xold_steps)+ "\nNew:     " + str(self.Xsteps))
        self.YSteps_label.configure(text="Y: " + str(self.Yold_steps)+ "\n   " + str(self.Ysteps))
        Interface._job1 = self.after(500, self.label_update)
    
    def save_measure(self, x=False, y=False ):
        self.measure()
        if x:
            self.Xold_steps = self.Xsteps
            self.parameters.Xsteps = self.Xsteps
        if y:
            self.Yold_steps = self.Ysteps
            self.parameters.Ysteps = self.Ysteps
        self.parameters.save()
        self.position_grid.generate_grid()
    
    def close_xy(self):
        self.clear_jobs()
        self.clear_frame()
        Interface._plate_parameters.init_window()
