import tkinter as tk
from .super import Interface
from .freemove import FreeMovementInterface


class Plate_parameters(Interface,tk.Frame):
    def __init__(self, Tk_root, microscope, grid, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, grid=grid, parameters=parameters)
        self.init_window()

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):
 
        self.Tk_root.title("Grid") 
        self.pack(fill=tk.BOTH, expand=1)
        self.lines = tk.StringVar()
        self.columns = tk.StringVar()
        self.subwells = tk.StringVar()

        self.lines.set(self.parameters.get()["lines"])
        self.columns.set(self.parameters.get()["columns"])
        self.subwells.set(self.parameters.get()["subwells"])

        self.Xsteps = self.parameters.get()["Xsteps"]
        self.Ysteps = self.parameters.get()["Ysteps"]
        self.subwells_spacing = self.parameters.get()["subwells_spacing"]

        #button definitions

        LinesLabel = tk.Label(self, text="Lines")
        LinesMenu = tk.OptionMenu(self, self.lines, *[4,8,16])
        ColumnsLabel = tk.Label(self, text="columns")
        ColumnsMenu = tk.OptionMenu(self, self.columns, *[6,12,24])

        SubWellsLabel = tk.Label(self, text="N# of subwell")
        SubWellsMenu = tk.OptionMenu(self, self.subwells, *[1,2,3,4])

        self.XstepsLabel = tk.Label(self, text="X steps:\n" + str(self.Xsteps))
        Xset =  tk.Button(self, text="Set X and Y step", command=self.set_steps)

        self.YstepsLabel = tk.Label(self, text="Y steps:\n" + str(self.Ysteps))

        Save = tk.Button(self, text="Save", command=self.save_grid_param)

        self.back_to_main_button()
        #buttons organisation

        LinesLabel.place(x=10,y=10)
        LinesMenu.place(x=10,y=30)
        ColumnsLabel.place(x=80,y=10)
        ColumnsMenu.place(x=80, y=30)

        SubWellsLabel.place(x=10,y=80)
        SubWellsMenu.place(x=10, y=100)

        self.XstepsLabel.place(x=10,y=260)
        Xset.place(x=10,y=300)

        self.YstepsLabel.place(x=80,y=260)

        Save.place(x=10, y=160)
    
        self.parameter_menu()

    def parameter_menu(self):
        self.parameters_selector = tk.StringVar()
        self.parameters_selector.set(self.parameters.selected)
        parameters_set_list = self.parameters.list_all()

        ParametersSet = tk.OptionMenu(self, self.parameters_selector, *parameters_set_list,  command=self.parameters.select)
        ParametersSet.config(width=15)
        ParametersSet.place(x=20, y=350)


    def save_grid_param(self):
        self.parameters.update([ 
        ("lines", int(self.lines.get())), 
        ("columns", int(self.columns.get())),
        ("subwells", int(self.subwells.get())) ])
        self.grid.generate_grid()
    
    def set_steps(self):
        self.clear_frame()
        XYsteps_popup(self.Tk_root, self.microscope, self.grid, self.Xsteps, self.Ysteps, self.parameters)

    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._plate_parameters:
            Interface._plate_parameters.init_window()
        else:
            pass
            Interface._plate_parameters = Plate_parameters(self.Tk_root, self.microscope, self.grid, self.parameters)

class XYsteps_popup(Interface, tk.Frame):

    def __init__(self, Tk_root, microscope, grid, Xsteps, Ysteps, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, grid=grid, parameters=parameters)               
        self.Tk_window = Tk_root
        self.Xold_steps = Xsteps
        self.Yold_steps = Ysteps

        self.init_window()

   #Creation of init_window
    def init_window(self):

        self.Tk_window.title("Steps") 
        self.pack(fill=tk.BOTH, expand=1)
        self.show_record_label()
        self.start = self.parameters.get()["start"]   
            
        FreeMovementInterface.XYsliders(self)

        menus_position = (20,290)
        self.divisorX = tk.StringVar()
        self.divisorY = tk.StringVar()
        self.divisorX.set(7)
        self.divisorY.set(11)
        DivisorXLabel = tk.Label(self, text="Divisor X")
        DivisorXMenu = tk.OptionMenu(self,  self.divisorX, *["      1   ","      2   ","      5   ","      7    "])
        DivisorXMenu.config(width=4)
        DivisorYLabel = tk.Label(self, text="Divisor Y")
        DivisorYMenu = tk.OptionMenu(self,  self.divisorY, *["      1   ","      2   ","      5   ","      11   "])
        DivisorYMenu.config(width=4)
        DivisorXLabel.place(x=menus_position[0], y=menus_position[1])
        DivisorXMenu.place(x=menus_position[0], y=menus_position[1]+20)
        DivisorYLabel.place(x=menus_position[0]+125, y=menus_position[1])
        DivisorYMenu.place(x=menus_position[0]+125, y=menus_position[1]+20)

        self.XSteps_label = tk.Label(self, text="test")
        self.YSteps_label = tk.Label(self, text="test")
        self.XSteps_label.place(x=10, y=440)
        self.YSteps_label.place(x=130, y=440)

        SaveX =  tk.Button(self, text="Save X ", command=lambda:  self.save_measure(x=True))
        SaveY =  tk.Button(self, text="Save Y", command=lambda: self.save_measure(y=True))
        SaveA1 = tk.Button(self, text="Save A1 center", command=self.save_A1)
        Cancel =  tk.Button(self, text="Cancel", command=self.close_xy)

        SaveA1.place(x=10,y=410)
        SaveX.place(x=10,y=480)
        SaveY.place(x=100,y=480)

        Cancel.place(x=10,y=530)

        self.label_update()

    def save_A1(self):
        start = self.parameters.get()["start"]
        start[0] = self.microscope.positions[0]
        start[1] = self.microscope.positions[1]
        self.parameters.update([("start", start)])
        self.start = start
        self.grid.generate_grid()

    def measure(self):  
        self.Xsteps = abs(int( (self.microscope.positions[0] - self.start[0]) / int(self.divisorX.get())))
        self.Ysteps = abs(int( (self.microscope.positions[1] - self.start[1]) / int(self.divisorY.get())))
    
    def label_update(self):
        self.measure()
        self.XSteps_label.configure(text="Current X: " + str(self.Xold_steps)+ "\nNew:     " + str(self.Xsteps))
        self.YSteps_label.configure(text="Y: " + str(self.Yold_steps)+ "\n   " + str(self.Ysteps))
        Interface._job1 = self.after(500, self.label_update)
    
    def save_measure(self, x=False, y=False ):
        self.measure()
        if x:
            self.parameters.update([("X steps", self.Xsteps)])
        if y:
            self.parameters.update([("Y steps", self.Ysteps)])
        self.grid.generate_grid()
        self.close()
    
    def close_xy(self):
        self.clear_jobs()
        self.clear_frame()
        Interface._plate_parameters.init_window()

#main loop for testing only
if __name__ == "__main__": 
    from ..microscope import Microscope
    from ..position_grid import PositionsGrid
    from ..microscope_param import *

    ### Object for microscope to run
    microscope = Microscope(addr, ready_pin)
    grid = PositionsGrid(microscope)

    #Tkinter object
    Tk_root = tk.Tk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    Interface._plate_parameters = Plate_parameters(Tk_root, last_window=None, microscope=microscope, grid=grid)

    Tk_root.mainloop()
