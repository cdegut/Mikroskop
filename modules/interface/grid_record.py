import tkinter as tk
from .super import Interface
from ..parametersIO import load_parameters, update_parameters, create_folder
import time

plate_name = "Plate" ##is a place holder to later add a plate type selector, maybe

class GridRecord(Interface, tk.Frame):

    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        Interface.__init__(self, Tk_root, last_window=self, microscope=microscope, grid=grid, camera=camera)

        self.last_window = last_window

        self.repeat = tk.StringVar()
        self.delay = tk.StringVar()
        self.startcolumn = tk.StringVar()
        self.startline = tk.StringVar() 
        self.finishcolumn = tk.StringVar()
        self.finishline = tk.StringVar()
        self.grid_subwells = tk.StringVar()


        self.init_window()

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):

        self.pack(fill=tk.BOTH, expand=1)
        self.parameters = load_parameters(plate_name)

        #Set all menus on default options
        self.repeat.set(self.parameters["repeat"])
        self.delay.set(self.parameters["delay"])
        self.startcolumn.set(self.parameters["start_well"][1:])
        self.startline.set(self.parameters["start_well"][0])
        self.finishcolumn.set(self.parameters["finish_well"][1:])
        self.finishline.set(self.parameters["finish_well"][0])
        self.grid_subwells.set(self.parameters["grid_subwells"])

        column_list = range(1, self.parameters["columns"]+1)
        line_list = []
        for i in range(0, self.parameters["lines"]):
            line_list.append(self.grid.line_namespace[i])
        SubwellsList = range(1, self.grid.nb_of_subwells+1)

        RepeatLabel = tk.Label(self, text="Repeat")
        RepeatMenu = tk.OptionMenu(self, self.repeat, *[1,2,5,10,20,30,40,60,80,100,140,180,360])

        DelayLabel = tk.Label(self, text="Delay Sec")
        DelayMenu = tk.OptionMenu(self, self.delay, *[0,1,2,5,10,15,30,60,120,600])

        StartWellLabell = tk.Label(self, text ="Start Well")
        StartColumnMenu = tk.OptionMenu(self, self.startcolumn, *column_list)
        StartLineMenu = tk.OptionMenu(self, self.startline, *line_list)

        FinishWellLabell = tk.Label(self, text ="Finish Well")
        FinishColumnMenu = tk.OptionMenu(self, self.finishcolumn, *column_list)
        FinishLineMenu = tk.OptionMenu(self, self.finishline, *line_list)

        SubwellLabel = tk.Label(self, text ="N# of subwell")
        SubwellMenu = tk.OptionMenu(self, self.grid_subwells, *SubwellsList)

        Save = tk.Button(self, text="Save", command=self.save_grid_pareameters)
        Start = tk.Button(self, text="Image grid", command=self.start_grid)

        Quit = tk.Button(self, fg='Red', text="Return", command=self.close)

        RepeatLabel.place(x=10,y=10)
        RepeatMenu.place(x=10,y=30)

        DelayLabel.place(x=80,y=10)
        DelayMenu.place(x=80,y=30)

        StartWellLabell.place(x=10, y =80)
        StartColumnMenu.place(x=80, y =100)
        StartLineMenu.place(x=10, y=100)

        FinishWellLabell.place(x=10, y =140)
        FinishColumnMenu.place(x=80, y =160)
        FinishLineMenu.place(x=10, y=160)

        SubwellLabel.place(x=10, y =200)
        SubwellMenu.place(x=10, y =220)

        Save.place(x=10, y=260 )
        Start.place(x=10, y=300 )

        Quit.place(x=0,y=450)
    
    def save_grid_pareameters(self):
        update_parameters([ 
        ("start_well", str(self.startline.get()) + str(self.startcolumn.get()) ), 
        ("finish_well", str(self.finishline.get()) + str(self.finishcolumn.get())  ), 
        ("grid_subwells", int(self.grid_subwells.get())), 
        ("delay", int(self.delay.get())), 
        ("repeat", int(self.repeat.get())) ],
        plate_name)

    def refresh_popup(self, popup, abort): # refresh popup  return True if stop button is clicked
        popup.update_idletasks()
        popup.update()
        abort.well_info.configure(text=self.grid.current_grid_position)
        if abort.stop:
            return True
        return False
    
    
    def start_grid(self):
        #run the grid imaging

        #generate the positions list from the parameters in the window
        start_well = str(self.startline.get()) + str(self.startcolumn.get())
        finish_well = str(self.finishline.get()) + str(self.finishcolumn.get()) 
        grid_subwells = int(self.grid_subwells.get())
        positions_list = self.grid.generate_position_list(start_well, finish_well, grid_subwells)

        delay = int(self.delay.get())
        repeat = int(self.repeat.get())
        
        #make an abort button
        popup = tk.Toplevel()
        abort = Stop_popup(popup)

        current_time = time.localtime()        
        date = str(current_time[0])[2:] + str(current_time[1]).zfill(2) + str(current_time[2]).zfill(2) + "_"  \
            + str(current_time[3]).zfill(2) + str(current_time[4]).zfill(2)
        data_dir= load_parameters(plate_name)["data_dir"]

        grid_folder = data_dir + "grid-" + date + "/"
        create_folder(grid_folder)


        for rep in range(0, repeat):
            
            #sleep for the apptopriate delay if not the first repeat
            if rep:
                self.grid.go(positions_list[0][0])

                for t in range(0, delay*10):
                    if self.refresh_popup(popup, abort): 
                        popup.destroy()
                        return
                    time.sleep(0.1)

            #Actual start of the grid
            for position in positions_list:

                #check if stop button is clicked
                if self.refresh_popup(popup, abort): 
                    popup.destroy()
                    return

                self.grid.go(position[0], position[1])
                time.sleep(0.5)
                
                #generate a picture name, accounting for subwells or not
                if grid_subwells == 1:
                    picture_name = str(position[0]) + "_" + str(rep+1).zfill(len(str(repeat))) + ".jpg"
                else:
                    picture_name = str(position[0]) + "-" + str(position[1]) + "_" + str(rep+1).zfill(len(str(repeat))) + ".jpg"

                self.camera.capture(grid_folder + picture_name)

        
        popup.destroy()
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._grid_record:
            Interface._grid_record.init_window(self)
        else:
            pass
            Interface._grid_record = GridRecord(self.Tk_root, last_window=self, grid=self.grid, camera=self.camera,  microscope=self.microscope)


class Stop_popup(tk.Frame): #widget to fill popup window, show a stop button and a modifiable label

    stop = False
    def __init__(self, Tk_window):
        tk.Frame.__init__(self, Tk_window)                 
        self.Tk_window = Tk_window
        self.init_window()


    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):

        self.Tk_window.geometry("220x540+800+35")      
        self.Tk_window.title("Stop") 
        self.pack(fill=tk.BOTH, expand=1)
        Stop = tk.Button(self, fg='Red', text="Stop", command=self.stop_switch)

        self.well_info = tk.Label(self, text="## - #")

        self.well_info.place(x=75, y=40)
        Stop.place(x=75,y=80)
    
    def stop_switch(self):
        self.stop = True    


