import json
import pathlib
from os import getenv
from dataclasses import dataclass, asdict

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
        with open(path_and_name, "r") as param_file:
            loaded = json.load(param_file)
            self.__init__(**loaded)
