import tkinter as tk
from .super import Interface
from ..parametersIO import load_parameters, update_parameters

class Plate_parameters(Interface,tk.Frame):
    def __init__(self, Tk_window, microscope, grid, last_window):
        tk.Frame.__init__(self, Tk_window)
        self.last_window = last_window
        self.microscope = microscope                 
        self.Tk_window = Tk_window
        self.grid = grid
        self.init_window()

   #Creation of init_window
    def init_window(self):
 
        self.Tk_window.title("Grid") 
        self.pack(fill=tk.BOTH, expand=1)
        self.lines = tk.StringVar()
        self.columns = tk.StringVar()
        self.subwells = tk.StringVar()

        self.parameters = load_parameters()

        self.lines.set(self.parameters["lines"])
        self.columns.set(self.parameters["columns"])
        self.subwells.set(self.parameters["subwells"])

        self.Xsteps = self.parameters["Xsteps"]
        self.Ysteps = self.parameters["Ysteps"]
        self.subwells_spacing = self.parameters["subwells_spacing"]

        #button definitions

        LinesLabel = tk.Label(self, text="Lines")
        LinesMenu = tk.OptionMenu(self, self.lines, *[4,8,16])
        ColumnsLabel = tk.Label(self, text="columns")
        ColumnsMenu = tk.OptionMenu(self, self.columns, *[6,12,24])

        SubWellsLabel = tk.Label(self, text="N# of subwell")
        SubWellsMenu = tk.OptionMenu(self, self.subwells, *[1,2,3,4])

        self.XstepsLabel = tk.Label(self, text="X steps:\n" + str(self.Xsteps))
        Xset =  tk.Button(self, text="Set", command=self.setXsteps)

        self.YstepsLabel = tk.Label(self, text="Y steps:\n" + str(self.Ysteps))
        Yset =  tk.Button(self, text="Set", command=self.setYsteps) 

        Save = tk.Button(self, text="Save", command=self.save_grid_param)
        Cancel =  tk.Button(self, text="Cancel", command=self.close)

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
        Yset.place(x=80,y=300)

        Save.place(x=10, y=160)
        Cancel.place(x=10,y=440)

    def save_grid_param(self):
        update_parameters([ 
        ("lines", int(self.lines.get())), 
        ("columns", int(self.columns.get())),
        ("subwells", int(self.subwells.get())) ])
        self.grid.generate_grid()
    
    def setXsteps(self):
        self.clear_frame()
        XYsteps_popup(self.microscope, self.grid, "X", 1, self.Xsteps, self, self.Tk_window)
    
    def setYsteps(self):
        self.clear_frame()
        XYsteps_popup(self.microscope, self.grid, "Y", 2, self.Ysteps, self, self.Tk_window)

    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._plate_parameters:
            Interface._plate_parameters.init_window()
        else:
            pass
            Interface._plate_parameters = Plate_parameters(self.Tk_root, last_window=self, grid=self.grid, microscope=self.microscope)

class XYsteps_popup(Interface, tk.Frame):

    def __init__(self, microscope, grid, axis_name, axis, steps, last_window, Tk_window):
        tk.Frame.__init__(self, Tk_window)
        self.microscope = microscope                 
        self.Tk_window = Tk_window
        self.axis_name = axis_name
        self.axis = axis
        self.old_steps = steps
        self.grid = grid
        self.last_window = last_window

        self.init_window()

   #Creation of init_window
    def init_window(self):

        self.Tk_window.title("Steps") 
        self.pack(fill=tk.BOTH, expand=1)
        self.start = load_parameters()["start"]   
        
        
        self.divisor = tk.StringVar()
        if self.axis_name is "X":
            self.divisor.set(7)
        elif self.axis_name is "Y":
            self.divisor.set(11)
    

        DivisorLabel = tk.Label(self, text="Divisor")
        DivisorMenu = tk.OptionMenu(self, self.divisor, *[1,2,3,4,5,6,7,8,9,10,11])

        A1 = tk.Button(self, text="go A1", command=lambda: self.grid.go("A1"))
        B1 = tk.Button(self, text="go B2", command=lambda: self.grid.go("B2"))
        H12 = tk.Button(self, text="go H12", command=lambda: self.grid.go("H12"))

        stepMax = tk.Button(self, text=self.axis_name + " Max", command=lambda:self.microscope.move_1axis(self.axis, 200000))
        stepMin = tk.Button(self, text=self.axis_name + " Min", command=lambda:self.microscope.move_1axis(self.axis, -200000))

        stepP1000 = tk.Button(self, text=self.axis_name + " +1000", command=lambda:self.microscope.move_1axis(self.axis, 1000))
        stepM1000 = tk.Button(self, text=self.axis_name + " -1000", command=lambda: self.microscope.move_1axis(self.axis,-1000))

        stepP100 = tk.Button(self, text=self.axis_name + " +200", command=lambda:self.microscope.move_1axis(self.axis, 200))
        stepM100 = tk.Button(self, text=self.axis_name + " -200", command=lambda: self.microscope.move_1axis(self.axis,-200))

        stepP25 = tk.Button(self, text=self.axis_name + " +50", command=lambda: self.microscope.move_1axis(self.axis,50))
        stepM25 = tk.Button(self, text=self.axis_name + " -50", command=lambda: self.microscope.move_1axis(self.axis,-50))

        stepP10 = tk.Button(self, text=self.axis_name + " +10", command=lambda: self.microscope.move_1axis(self.axis,10))
        stepM10 = tk.Button(self, text=self.axis_name + " -10", command=lambda: self.microscope.move_1axis(self.axis,-10))

        self.Steps = tk.Label(self, text="test")
        Accept =  tk.Button(self, text="Save " + self.axis_name + "  steps", command=self.save_measure)
        SaveA1 = tk.Button(self, text="Save A1 center", command=self.save_A1)
        Cancel =  tk.Button(self, text="Cancel", command=self.Tk_window.destroy)

        stepMax.place(x=10, y=70)
        stepMin.place(x=100, y=70)
        stepP1000.place(x=10, y=110)
        stepM1000.place(x=100, y=110)
        stepP100.place(x=10, y=155)
        stepM100.place(x=100, y=155)
        stepP25.place(x=10, y=200)
        stepM25.place(x=100, y=200)
        stepP10.place(x=10, y=245)
        stepM10.place(x=100, y=245)


        DivisorLabel.place(x=10, y=10)
        DivisorMenu.place(x=10, y=30)

        A1.place(x=0, y=300)
        B1.place(x=75, y=300)
        H12.place(x=150, y=300)

        SaveA1.place(x=10,y=360)
        Accept.place(x=10,y=400)
        self.Steps.place(x=10, y=440)
        Cancel.place(x=10,y=500)

        self.label_update()

    def save_A1(self):
        start = load_parameters()["start"]
        start[self.axis-1] = self.microscope.positions[self.axis-1]
        update_parameters([("start", start)])
        self.start = start
        self.grid.generate_grid()

    def measure(self):  
        self.steps = abs(int( (self.microscope.positions[self.axis-1] - self.start[self.axis-1]) / int(self.divisor.get())))
    
    def label_update(self):
        self.measure()
        self.Steps.configure(text="Current: " + str(self.old_steps)+ "\nNew:     " + str(self.steps))
        self.after(500, self.label_update)
    
    def save_measure(self):
        self.measure()
        update_parameters([(self.axis_name + "steps", self.steps)])
        self.grid.generate_grid()
        self.close()