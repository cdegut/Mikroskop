from tkinter import Frame, Button, BOTH, Label, StringVar, OptionMenu, Toplevel
from customtkinter import CTkFrame, CTkButton, CTkLabel, BOTH, CTkOptionMenu, N, StringVar, CTkToplevel
import os
from .super import Interface
import time
from modules.controllers import create_folder

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

        #Grid Recording parameters
        self.positions_list = None
        self.delay_value = None
        self.repeat_value = None
        self.done_repeat = 0
        self.index_position = 0
        self.pic_taken = False
        self.pre_pic_timer = 0
        self.grid_folder = None
        self.grid_subwells_value = None
        self.pause_timer =0
        self.is_regording = False



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
        self.clear_frame()

        self.pack(fill=BOTH, expand=1)
        self.current_parameters = self.parameters.get()

        if self.is_regording == False:
            #Set all menus on default options
            self.repeat.set(self.current_parameters["repeat"])
            self.delay.set(self.current_parameters["delay"])
            self.startcolumn.set(self.current_parameters["start_well"][1:])
            self.startline.set(self.current_parameters["start_well"][0])
            self.finishcolumn.set(self.current_parameters["finish_well"][1:])
            self.finishline.set(self.current_parameters["finish_well"][0])
            self.grid_subwells.set(self.current_parameters["grid_subwells"])

            column_list = [str(x) for x in range(1, self.current_parameters["columns"]+1) ]
            line_list = []
            for i in range(0, self.current_parameters["lines"]):
                line_list.append(self.position_grid.line_namespace[i])
            SubwellsList = [str(x) for x in range(1, self.position_grid.nb_of_subwells+1)]

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

        else:
            self.stop_window()

    def stop_window(self):

        Stop = CTkButton(self, fg_color='Red', text="Stop", command=self.stop_switch)
        self.well_info = CTkLabel(self, text="## - #")
        self.well_info.place(x=75, y=40)
        Stop.place(relx=0.5,y=90, anchor=N)

    def stop_switch(self):
        self.is_regording = False
        self.init_window()   

    def save_grid_parameters(self):
        self.parameters.update([ 
        ("start_well", str(self.startline.get()) + str(self.startcolumn.get()) ), 
        ("finish_well", str(self.finishline.get()) + str(self.finishcolumn.get())  ), 
        ("grid_subwells", int(self.grid_subwells.get())), 
        ("delay", int(self.delay.get())), 
        ("repeat", int(self.repeat.get())) ])
        
    def start_grid(self):
        #reset everything
        self.is_regording = True
        self.init_window()

        self.positions_list = None
        self.delay_value = None
        self.repeat_value = None
        self.done_repeat = 0
        self.index_position = 0
        self.pic_taken = False
        self.pre_pic_timer = 0
        self.grid_folder = None
        self.grid_subwells_value = None
        self.pause_timer =0

        #generate the positions list from the parameters in the window
        start_well = str(self.startline.get()) + str(self.startcolumn.get())
        finish_well = str(self.finishline.get()) + str(self.finishcolumn.get()) 
        self.grid_subwells_value = int(self.grid_subwells.get())
        
        self.positions_list = self.position_grid.generate_position_list(start_well, finish_well, self.grid_subwells_value)

        self.delay_value = int(self.delay.get())
        self.repeat_value = int(self.repeat.get())
        self.done_repeat = 0

        current_time = time.localtime()        
        date = str(current_time[0])[2:] + str(current_time[1]).zfill(2) + str(current_time[2]).zfill(2) + "_"  \
            + str(current_time[3]).zfill(2) + str(current_time[4]).zfill(2)

        data_dir = self.current_parameters["data_dir"]
        
        home = os.getenv("HOME")
        self.grid_folder = f"{home}/{data_dir}/grid-{date}/"
        create_folder(self.grid_folder)

        self.position_grid.go(self.positions_list[0][0])

        self.is_regording = True

        self.well_info.configure(text = f"{self.positions_list[0][0]} - 1" )

        Interface._grid_record_job = self.after(100, self.__record_grid)

    def __record_grid(self):
        if self.is_regording == False:
            return

        ### Delay after a repeat
        if  self.pause_timer <= self.delay_value * 10:
            self.pause_timer += 1
            Interface._grid_record_job = self.after(100, self.__record_grid)
            return

        if self.position_grid.at_position() == False: #return if not at position
            Interface._grid_record_job = self.after(100, self.__record_grid)
            return

        ### pre image delay 0.5s
        if self.pic_taken == False and self.pre_pic_timer < 5:        
            self.pre_pic_timer += 1
            Interface._grid_record_job = self.after(100, self.__record_grid)
            return

        # take picture
        if self.pic_taken == False:
            #generate a picture name, accounting for subwells or not
            if self.grid_subwells_value == 1:
                position = self.positions_list[self.index_position]
                picture_name = str(position[0]) + "_" + str(self.done_repeat+1).zfill(len(str(self.repeat_value)))
                self.well_info.configure(text = f"{position[0]} \n Repeat {self.done_repeat+1}" )
            else:
                picture_name = str(position[0]) + "-" + str(position[1]) + "_" + str(self.done_repeat+1).zfill(len(str(self.repeat_value)))
                self.well_info.configure(text = f"{position[0]} - {position[1]} \n Repeat {self.done_repeat+1}" )

            self.camera.capture_and_save(picture_name, self.grid_folder)
            self.pic_taken = True
            Interface._grid_record_job = self.after(100, self.__record_grid)
            return

        if self.camera.is_capturing == True:
            return

        #Next position
        self.pre_pic_timer = 0
        self.pic_taken = False
        self.index_position += 1

        if self.index_position >= len(self.positions_list):
            self.index_position = 0
            self.pause_timer = 0

            self.done_repeat += 1
            if self.done_repeat >= self.repeat_value: ## End
                position = self.positions_list[0]
                self.position_grid.go(position[0], position[1])
                return

        position = self.positions_list[self.index_position]
        self.position_grid.go(position[0], position[1])
        Interface._grid_record_job = self.after(100, self.__record_grid)
    


