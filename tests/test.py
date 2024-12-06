from dataclasses import dataclass, asdict, field
import pathlib
import json
import os 

path = f"{str(pathlib.Path(__file__).parent.absolute())}/grids_parameters/"

@dataclass
class test_grid_param:
    name: str = "Default"
    columns: int =  6
    lines:int = 4
    start: list = field(default_factory=lambda: [7200,81950, 24980])
    data_dir: str = "/microscope_data/"
    selected: bool = True
    protected: bool = False
    subwells_spacing: list = field(default_factory=lambda: [3000,0,0])
    Xsteps: int = -29000
    Ysteps: int = -7200
    XYFocusDrift: list = field(default_factory=lambda: [0,0])
    XYaxisSkew: list = field(default_factory=lambda: [0,0])
    dyn_endstops: dict = field(default_factory=lambda: {
        "dyn_maxFcs": 28000,
        "dyn_Xmax": 70000,
        "dyn_Xmin": 2000,
        "dyn_Ymax": 90000,
        "dyn_Ymin": 1550,
        "safe_Fcs": 10000 })
    
    delay: int = 2
    start_well: str = "A1"
    finish_well: str = "B2"
    grid_subwells: int = 1
    led: list = field(default_factory=lambda:  [50,0])
    repeat: int = 2
    subwells: int = 1

    def load(self, name:str):
        path_and_name = f"{path}{name}.json"
        self.selected = False
        self.save()
        try:
            with open(path_and_name, "r") as param_file:
                loaded = json.load(param_file)
                self.__init__(**loaded)
                self.selected = True
                self.name = name #override name with file name
                self.save()
            return
        except FileNotFoundError:
            print(f"File {path_and_name} does not exist yet, creating it with current parameters")
            self.save(name)
            self.load(name)

    def save(self, name = None):
        if not name:
            path_and_name = f"{path}{self.name}.json"
        else:
            path_and_name = f"{path}{name}.json"
        with open(path_and_name, "w") as param_file:
            json.dump(asdict(self), param_file)
    
    
    def delete(self):
        if not self.Protected:
            os.remove(f"{path}{self.name}.json")
 
    def load_last_selected(self):
        for parameter in list_all_parameters():
            if parameter != "Default":
                if read_parameter_value(parameter, "selected") == True:
                    self.load(parameter)
                    return
        
        self.load("Default")

    

def list_all_parameters():
    name_list: list = []
    for param in os.listdir(path):
        name_list.append(param.split(sep = ".")[0])
    return name_list

def read_parameter_value(name, value):
    path_and_name = f"{path}{name}.json"
    with open(path_and_name, "r") as param_file:
        loaded = json.load(param_file)
    return loaded[value]

grid_parameters = test_grid_param()
grid_parameters.load_last_selected()
print(grid_parameters.name)





