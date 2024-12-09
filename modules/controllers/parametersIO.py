import json
import pathlib
import os
from dataclasses import dataclass, asdict, field

'''
class ParametersSets:

    def __init__(self):
        self.param_file_path = self.__param_file_path()
        self.all_parameters_sets: dict = self.__load_all()
        self.selected = self.__get_selected()
        self.home = getenv('HOME')

    def __param_file_path(self):
        current_path = str(pathlib.Path(__file__).parent.absolute())
        path_and_name = current_path + "/../grids_params.json"
        return path_and_name

    def __load_all(self):
        with open(self.param_file_path, "r") as param_file:
            parameters = json.load(param_file)
        return parameters

    def __save_all(self):
        with open(self.param_file_path, "w") as param_file:
            json.dump(self.all_parameters_sets, param_file)
    
    def __get_selected(self):
        for parameters_set in self.all_parameters_sets:
            if self.all_parameters_sets[parameters_set]["Selected"]:
                return(parameters_set)          
        return "Default"

    def get(self, subset = None) -> dict:# -> Dictionary of the current parameter set:
        if not subset:
            subset = self.selected
        return self.all_parameters_sets[subset]
    
    def list_all(self):
        parameters_list = []
        for parameter_set in self.all_parameters_sets:
            parameters_list.append(parameter_set)
        return parameters_list

    def select(self, new_selection):
        self.selected = new_selection
        for parameters_set in self.all_parameters_sets:
            if parameters_set == new_selection:
                self.all_parameters_sets[parameters_set]["Selected"] = True
            else:
                self.all_parameters_sets[parameters_set]["Selected"] = False
        self.__save_all()


    def copy(self, source, target):
        self.all_parameters_sets[target] = self.all_parameters_sets[source]
        self.__save_all()
    
    def delete(self, target):
        if not self.all_parameters_sets[target]["Protected"]:
            self.all_parameters_sets.pop(target)
            self.__save_all()
    
    #### updaate parameter from a list of tuple with the format : [("keyA", value ), ("keyB", value)]
    def update(self, param_list, subset=None):
        if not subset:
            subset = self.selected
        for parameter in param_list:
            self.all_parameters_sets[subset][parameter[0]] = parameter[1]
        self.__save_all()

    def update_start(self, x,y,f,subset=None):
        if not subset:
            subset = self.selected
        if x:    
            self.all_parameters_sets[subset]["start"][0] = x
        if y:
            self.all_parameters_sets[subset]["start"][1] = y
        if f:
            self.all_parameters_sets[subset]["start"][2] = f
        self.__save_all()
'''

def create_folder(new_folder_path):
    p = pathlib.Path(new_folder_path)
    p.mkdir(parents=True, exist_ok=True)

@dataclass
class MicroscopeParameters:
    software_endstops: bool = True
    Xmaxrange: int = 70000
    Ymaxrange: int = 93000
    Fmaxrange: int = 30000

    overshoot_X: int = 0
    undershoot_X: int = 0
    overshoot_Y: int = 0
    undershoot_Y: int = 0

    #fluorescent gain value
    awbR_fluo: float = 1
    awbB_fluo: float = 0.35
    awbR_white: float = 3
    awbB_white: float = 0.8

    def save(self):
        current_path = str(pathlib.Path(__file__).parent.absolute())
        path_and_name = current_path + "/../microscope_param.json"
        with open(path_and_name, "w") as param_file:
            json.dump(asdict(self), param_file)

    def load(self):
        current_path = str(pathlib.Path(__file__).parent.absolute())
        path_and_name = current_path + "/../microscope_param.json"
        print(path_and_name)
        try:
            with open(path_and_name, "r") as param_file:
                loaded = json.load(param_file)
                self.__init__(**loaded)
        except FileNotFoundError:
            print(f"File {path_and_name} does not exist yet, creating it with default parameters")
            self.save()

grid_param_path = f"{str(pathlib.Path(__file__).parent.absolute())}/../grids_parameters/"

@dataclass
class GridParameters:
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
        path_and_name = f"{grid_param_path}{name}.json"
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
            path_and_name = f"{grid_param_path}{self.name}.json"
        else:
            path_and_name = f"{grid_param_path}{name}.json"
        with open(path_and_name, "w") as param_file:
            json.dump(asdict(self), param_file)
    
    
    def delete(self):
        if not self.protected:
            os.remove(f"{grid_param_path}{self.name}.json")
 
    def load_last_selected(self):
        for parameter in list_all_parameters():
            if parameter != "Default":
                if read_parameter_value(parameter, "selected") == True:
                    self.load(parameter)
                    return
        
        self.load("Default")

    
def list_all_parameters():
    name_list: list = []
    for param in os.listdir(grid_param_path):
        name_list.append(param.split(sep = ".")[0])
    return name_list

def read_parameter_value(name, value):
    path_and_name = f"{grid_param_path}{name}.json"
    with open(path_and_name, "r") as param_file:
        loaded = json.load(param_file)
    return loaded[value]
