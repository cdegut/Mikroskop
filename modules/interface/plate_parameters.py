from customtkinter import CTkFrame, CTkButton, CTkLabel, BOTH, CTkOptionMenu, N, StringVar, CTk
from .super import Interface
from ..microscope import Microscope
from ..parametersIO import ParametersSets
from ..position_grid import PositionsGrid
from .popup import led_focus_zoom_buttons


class Plate_parameters(Interface,CTkFrame):
    def __init__(self, Tk_root, microscope, position_grid, camera, parameters: ParametersSets):
        Interface.__init__(self, Tk_root, microscope=microscope, position_grid=position_grid, camera=camera, parameters=parameters)
        self._param_config = None
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

        self.Xsteps = self.parameters.get()["Xsteps"]
        self.Ysteps = self.parameters.get()["Ysteps"]
        self.subwells_spacing = self.parameters.get()["subwells_spacing"]

        self.parameter_menu(20,10)
        self.lines_columns_subwels(20,80)
        self.XYstep_config_buttons(10,280)
        self.back_to_main_button([10, 480])

    def XYstep_config_buttons(self, x_p=20, y_p=220):

        TopLabel = CTkLabel(self, text="Grid distances:")
        XstepsLabel = CTkLabel(self, text="X steps:\n" + str(self.Xsteps))
        YstepsLabel = CTkLabel(self, text="Y steps:\n" + str(self.Ysteps))
        Configure_XY =  CTkButton(self, text="Configure X and Y step", command=self.set_steps)

        TopLabel.place(x=x_p, y=y_p)
        XstepsLabel.place(x=x_p+20, y=y_p+20)
        YstepsLabel.place(x=x_p+90, y=y_p+20)
        Configure_XY.place(x=x_p, y=y_p+60)

        A1X = self.parameters.get()["start"][0]
        A1Y = self.parameters.get()["start"][1]
        A1Label = CTkLabel(self, text=f"A1 position X: {A1X} Y: {A1Y}")
        A1position =  CTkButton(self, text="Change A1 position", command=self.set_A1_position)
        A1Label.place(x=x_p, y=y_p+110)
        A1position.place(x=x_p, y=y_p+140)
       
    def lines_columns_subwels(self, x_p=10, y_p=10):
        
        self.lines = StringVar()
        self.columns = StringVar()
        self.subwells = StringVar()


        TopLabel = CTkLabel(self, text="Grid characteristics:")
        LinesLabel = CTkLabel(self, text="Lines:")

        w=40
        LinesMenu = CTkOptionMenu(self, width=w, variable=self.lines, values=["4","8","16"])
        ColumnsLabel = CTkLabel(self, text="Columns:")
        ColumnsMenu = CTkOptionMenu(self, width=w, variable=self.columns, values=["6","12","24"])
        SubWellsLabel = CTkLabel(self, text="Subwells:")
        SubWellsMenu = CTkOptionMenu(self, width=w, variable=self.subwells, values=["1","2","3","4"])

        self.lines.set(self.parameters.get()["lines"])
        self.columns.set(self.parameters.get()["columns"])
        self.subwells.set(self.parameters.get()["subwells"])

        Save = CTkButton(self, text="Save changes", command=self.save_grid_param)
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
        Save.place(relx=0.5, y=y_p+60, anchor=N)
        New.place(relx=0.5, y=y_p+90, anchor=N)
        Delete.place(relx=0.5, y=y_p+120, anchor=N)

    def parameter_menu(self, x_p, y_p):
        self.parameters_selector = StringVar()
        self.parameters_selector.set(self.parameters.selected)
        parameters_set_list = self.parameters.list_all()

        ParametersSet = CTkOptionMenu(self, width=100, variable=self.parameters_selector, values=parameters_set_list,  command=self.parameter_set_changed)
        ParametersSet_label =  CTkLabel(self, text="Parameters set:")
        ParametersSet_label.place(x=x_p, y=y_p)
        ParametersSet.place(x=x_p, y=y_p+30)
    
    def parameter_set_changed(self, new_param):
        self.parameters.select(new_param)
        self.position_grid.generate_grid()
        endstops_dict = self.parameters.get()["dyn_endstops"] ## Load the specific dynamic endstops
        self.microscope.set_dynamic_endsotop(endstops_dict)
        self.init_window()

    def save_grid_param(self):
        self.parameters.update([ 
        ("lines", int(self.lines.get())), 
        ("columns", int(self.columns.get())),
        ("subwells", int(self.subwells.get())) ])
        self.position_grid.generate_grid()
    
    def new_grid_param(self):
        l = int(self.lines.get())
        c = int(self.columns.get())
        s = int(self.subwells.get())
        i=1
        name = f"{l}-{c}-{s}-({i})"

        while name in self.parameters.all_parameters_sets:
            i += 1
            name = f"{l}-{c}-{s}-({i})"
        self.parameters.copy("Default", name)
        self.parameters.select(name)
        self.parameters.update([("Protected", False)])
        self.save_grid_param()
        self.init_window()

    def delete_grid_param(self):
        self.parameters.delete(self.parameters.selected)
        self.parameters.select("Default")
        self.init_window()

    def set_steps(self):
        self.clear_frame()
        if self._param_config:
            self._param_config.step_mode = True
            self._param_config.A1_mode = False
            self._param_config.init_window()
        else:
            pass
            self._param_config = ParametersConfig(self.Tk_root, self.microscope, self.position_grid, self.Xsteps, self.Ysteps, self.parameters, self.camera)
            self._param_config.step_mode = True
            self._param_config.A1_mode = False
            self._param_config.init_window()
    
    def set_A1_position(self):
        self.clear_frame()
        if self._param_config:
            self._param_config.step_mode = False
            self._param_config.A1_mode = True
            self._param_config.init_window()
        else:
            pass
            self._param_config = ParametersConfig(self.Tk_root, self.microscope, self.position_grid, self.Xsteps, self.Ysteps, self.parameters, self.camera)
            self._param_config.step_mode = False
            self._param_config.A1_mode = True
            self._param_config.init_window()

    def set_dyn_endstop_position(self):
        self.clear_frame()
        if self._param_config:
            self._param_config.init_window()
        else:
            pass
            self._param_config = ParametersConfig(self.Tk_root, self.microscope, self.position_grid, self.Xsteps, self.Ysteps, self.parameters, self.camera)
            self._param_config.init_window()        

class ParametersConfig(Interface, CTkFrame):

    def __init__(self, Tk_root, microscope, position_grid, Xsteps, Ysteps, parameters, camera):
        Interface.__init__(self, Tk_root, microscope=microscope, position_grid=position_grid, camera=camera, parameters=parameters)             
        self.Tk_window = Tk_root
        self.Xold_steps = Xsteps
        self.Yold_steps = Ysteps
        self.A1_mode = False
        self.step_mode = False

   #Creation of init_window
    def init_window(self):

        self.Tk_window.title("Steps") 
        self.pack(fill=BOTH, expand=1)
        self.show_record_label()
        self.start = self.parameters.get()["start"]   
            
        self.XYsliders(l=200)

        Cancel =  CTkButton(self, text="Back", command=self.close_xy)
        

        if self.step_mode:
            self.grid_go_pad((100,340))
            self.save_XY_buttons(menus_position= (10,380))
            Cancel.place(x=10,y=520)
        if self.A1_mode:
            self.A1_config_button()
            Cancel.place(x=10,y=450)
    
    def grid_go_pad(self, pad_position):
        w = 65
        h = 30
        A1 = CTkButton(self, width=w,text="A1", command=lambda: self.position_grid.go("A1"))        
        B2 = CTkButton(self, width=w, text="B2", command=lambda: self.go_and_change_divisor("B2", (1,1)))
        H1 = CTkButton(self, width=w, text="H1", command=lambda: self.go_and_change_divisor("H1", (7,1)))
        A12 = CTkButton(self, width=w, text="A12", command=lambda: self.go_and_change_divisor("A12", (1,11)))
        H12 = CTkButton(self, width=w, text="H12", command=lambda: self.go_and_change_divisor("H12", (7,11)))

        A1.place(x=pad_position[0]-90, y=pad_position[1]-50)
        A12.place(x=pad_position[0]+60, y=pad_position[1]-50)
        H1.place(x=pad_position[0]-90, y=pad_position[1])
        H12.place(x=pad_position[0]+60, y=pad_position[1])
        B2.place(x=pad_position[0]-15, y=pad_position[1]-25)
    
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
        DivisorXMenu = CTkOptionMenu(self, width=40,  variable=self.divisorX, values=["      1   ","      2   ","      5   ","      7    "])
        DivisorYLabel = CTkLabel(self, text="Divisor Y")
        DivisorYMenu = CTkOptionMenu(self,  width=40, variable=self.divisorY, values=["      1   ","      2   ","      5   ","      11   "])
        
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

    ### Panel only for setting up A1 position
    def A1_config_button(self):

        A1 = CTkButton(self, width=40,text="Go Current A1", command=lambda: self.position_grid.go("A1"))

        self.A1Label = CTkLabel(self, text=f"Current A1 position:\nX: {self.parameters.get()['start'][0]} Y: {self.parameters.get()['start'][1]} F: {self.parameters.get()['start'][2]}")       
        self.A1Label.place(x=10, y=280)
        A1.place(x=10, y=320)

        self.coordinate_place()

        SaveA1 = CTkButton(self, text="Save A1 center", command=self.save_A1)
        SaveA1.place(x=10,y=400)
        led_focus_zoom_buttons(self, 360)

    def save_A1(self):
        self.microscope.update_real_state()
        start = self.microscope.XYFposition
        self.parameters.update([("start", start)])
        self.start = start
        self.A1Label.configure(text=f"Current A1 position:\nX: {self.parameters.get()['start'][0]} Y: {self.parameters.get()['start'][1]} F: {self.parameters.get()['start'][2]}")
        self.position_grid.generate_grid()

    def measure(self):
        self.microscope.update_real_state() 
        self.Xsteps = abs(int( (self.microscope.XYFposition[0] - self.start[0]) / int(self.divisorX.get())))
        self.Ysteps = abs(int( (self.microscope.XYFposition[1] - self.start[1]) / int(self.divisorY.get())))
    
    def label_update(self):
        self.measure()
        self.XSteps_label.configure(text="Current X: " + str(self.Xold_steps)+ "\nNew:     " + str(self.Xsteps))
        self.YSteps_label.configure(text="Y: " + str(self.Yold_steps)+ "\n   " + str(self.Ysteps))
        Interface._job1 = self.after(500, self.label_update)
    
    def save_measure(self, x=False, y=False ):
        self.measure()
        if x:
            self.Xold_steps = self.Xsteps
            self.parameters.update([("Xsteps", self.Xsteps)])
        if y:
            self.Yold_steps = self.Ysteps
            self.parameters.update([("Ysteps", self.Ysteps)])
        self.position_grid.generate_grid()
    
    def close_xy(self):
        self.clear_jobs()
        self.clear_frame()
        Interface._plate_parameters.init_window()

#main loop for testing only
#main loop
if __name__ == "__main__": 
    from modules.cameracontrol import Microscope_camera
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
    position_grid = PositionsGrid(microscope, parameters)
    micro_cam = Microscope_camera(microscope)

    #Tkinter object
    customtkinter.set_appearance_mode("dark")
    Tk_root = customtkinter.CTk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._plate_parameters = Plate_parameters(Tk_root, microscope=microscope, position_grid=position_grid, parameters=parameters, camera=micro_cam)
    Tk_root.mainloop()

