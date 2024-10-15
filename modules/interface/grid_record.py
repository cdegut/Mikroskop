from tkinter import Frame, Button, BOTH, Label, StringVar, OptionMenu, Toplevel
from customtkinter import CTkFrame, CTkButton, CTkLabel, BOTH, CTkOptionMenu, N, StringVar, CTkToplevel

from .super import Interface
from ..parametersIO import create_folder
import time

plate_name = "Plate" ##is a place holder to later add a plate type selector, maybe

class GridRecord(Interface, CTkFrame):

    def __init__(self, Tk_root, microscope, position_grid, camera, parameters):
        Interface.__init__(self, Tk_root, microscope=microscope, position_grid=position_grid, camera=camera, parameters=parameters)


        self.repeat = StringVar()
        self.delay = StringVar()
        self.startcolumn = StringVar()
        self.startline = StringVar() 
        self.finishcolumn = StringVar()
        self.finishline = StringVar()
        self.grid_subwells = StringVar()


        self.init_window()

    ######Function called to open this window, generate an new object the first time, 
    ###### then recall the init_window function of the same object    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._grid_record:
            Interface._grid_record.init_window()
        else:
            pass
            Interface._grid_record = GridRecord(self.Tk_root, self.microscope, self.position_grid, self.camera, self.parameters)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):

        self.pack(fill=BOTH, expand=1)
        self.parameters = self.parameters.get()

        #Set all menus on default options
        self.repeat.set(self.parameters["repeat"])
        self.delay.set(self.parameters["delay"])
        self.startcolumn.set(self.parameters["start_well"][1:])
        self.startline.set(self.parameters["start_well"][0])
        self.finishcolumn.set(self.parameters["finish_well"][1:])
        self.finishline.set(self.parameters["finish_well"][0])
        self.grid_subwells.set(self.parameters["grid_subwells"])

        column_list = [str(x) for x in range(1, self.parameters["columns"]+1) ]
        line_list = []
        for i in range(0, self.parameters["lines"]):
            line_list.append(self.position_grid.line_namespace[i])
        SubwellsList = [str(x) for x in range(1, self.grid.nb_of_subwells+1)]

        RepeatLabel = CTkLabel(self, text="Repeat")
        RepeatMenu = CTkOptionMenu(self, width = 80, variable=self.repeat, values=["1","2","5","10","20","30","40","60","80","100","140","180","360"])

        DelayLabel = CTkLabel(self, text="Delay Sec")
        DelayMenu = CTkOptionMenu(self, width = 80,variable=self.delay, values=["0","1","2","5","10","15","30","60","120","600"])

        StartWellLabell = CTkLabel(self, text ="Start Well")
        StartColumnMenu = CTkOptionMenu(self, width = 80, variable=self.startcolumn, values=column_list)
        StartLineMenu = CTkOptionMenu(self, width = 80, variable=self.startline, values=line_list)

        FinishWellLabell = CTkLabel(self, text ="Finish Well")
        FinishColumnMenu = CTkOptionMenu(self, width = 80, variable=self.finishcolumn, values=column_list)
        FinishLineMenu = CTkOptionMenu(self, width = 80, variable=self.finishline, values=line_list)

        SubwellLabel = CTkLabel(self, text ="N# of subwell")
        SubwellMenu = CTkOptionMenu(self,width = 80, variable=self.grid_subwells, values=SubwellsList)

        Save = CTkButton(self, text="Save", command=self.save_grid_parameters)
        Start = CTkButton(self, text="Image grid", command=self.start_grid)

        self.back_to_main_button()

        RepeatLabel.place(x=10,y=10)
        RepeatMenu.place(x=10,y=30)

        DelayLabel.place(x=100,y=10)
        DelayMenu.place(x=100,y=30)

        StartWellLabell.place(x=10, y =80)
        StartColumnMenu.place(x=100, y =100)
        StartLineMenu.place(x=10, y=100)

        FinishWellLabell.place(x=10, y =140)
        FinishColumnMenu.place(x=100, y =160)
        FinishLineMenu.place(x=10, y=160)

        SubwellLabel.place(x=10, y =200)
        SubwellMenu.place(x=10, y =220)

        Save.place(x=10, y=260 )
        Start.place(x=10, y=300 )
    
    def save_grid_parameters(self):
        self.parameters.update([ 
        ("start_well", str(self.startline.get()) + str(self.startcolumn.get()) ), 
        ("finish_well", str(self.finishline.get()) + str(self.finishcolumn.get())  ), 
        ("grid_subwells", int(self.grid_subwells.get())), 
        ("delay", int(self.delay.get())), 
        ("repeat", int(self.repeat.get())) ])

    def refresh_popup(self, popup, abort): # refresh popup  return True if stop button is clicked
        popup.update_idletasks()
        popup.update()
        abort.well_info.configure(text=self.position_grid.current_grid_position)
        if abort.stop:
            return True
        return False
    
    
    def start_grid(self):
        #run the grid imaging

        #generate the positions list from the parameters in the window
        start_well = str(self.startline.get()) + str(self.startcolumn.get())
        finish_well = str(self.finishline.get()) + str(self.finishcolumn.get()) 
        grid_subwells = int(self.grid_subwells.get())
        positions_list = self.position_grid.generate_position_list(start_well, finish_well, grid_subwells)

        delay = int(self.delay.get())
        repeat = int(self.repeat.get())
        
        #make an abort button
        popup = CTkToplevel()
        abort = Stop_popup(popup)

        current_time = time.localtime()        
        date = str(current_time[0])[2:] + str(current_time[1]).zfill(2) + str(current_time[2]).zfill(2) + "_"  \
            + str(current_time[3]).zfill(2) + str(current_time[4]).zfill(2)
        data_dir= self.parameters.get()["data_dir"]

        grid_folder = data_dir + "grid-" + date + "/"
        create_folder(grid_folder)


        for rep in range(0, repeat):
            
            #sleep for the apptopriate delay if not the first repeat
            if rep:
                self.position_grid.go(positions_list[0][0])

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

                self.position_grid.go(position[0], position[1])
                time.sleep(0.5)
                
                #generate a picture name, accounting for subwells or not
                if grid_subwells == 1:
                    picture_name = str(position[0]) + "_" + str(rep+1).zfill(len(str(repeat))) + ".jpg"
                else:
                    picture_name = str(position[0]) + "-" + str(position[1]) + "_" + str(rep+1).zfill(len(str(repeat))) + ".jpg"

                self.camera.capture(grid_folder + picture_name)

        
        popup.destroy()
    


class Stop_popup(CTkFrame): #widget to fill popup window, show a stop button and a modifiable label

    stop = False
    def __init__(self, Tk_window):
        CTkFrame.__init__(self, Tk_window)                 
        self.Tk_window = Tk_window
        self.init_window()


    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self):

        self.Tk_window.geometry("220x540+800+35")      
        self.Tk_window.title("Stop") 
        self.pack(fill=BOTH, expand=1)
        Stop = CTkButton(self, fg='Red', text="Stop", command=self.stop_switch)

        self.well_info = CTkLabel(self, text="## - #")

        self.well_info.place(x=75, y=40)
        Stop.place(x=75,y=80)
    
    def stop_switch(self):
        self.stop = True    


