import json
import pathlib

class ParametersSets:

    def __init__(self):
        self.param_file_path = self.__param_file_path()
        self.all_parameters_sets = self.__load_all()
        self.selected = self.__get_selected()

    def __param_file_path(self):
        current_path = str(pathlib.Path(__file__).parent.absolute())
        path_and_name = current_path + "/../param.json"
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

    def get(self, subset = None):
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


    #### updaate parameter from a list of tuple with the format : [("keyA", value ), ("keyB", value)]
    def update(self, param_list, subset=None):
        if not subset:
            subset = self.selected
        for parameter in param_list:
            self.all_parameters_sets[subset][parameter[0]] = parameter[1]
        self.__save_all()

    def update_start(self, x,y,f,subset="Default"):
        if x:    
            self.all_parameters_sets[subset]["start"][0] = x
        if y:
            self.all_parameters_sets[subset]["start"][1] = y
        if f:
            self.all_parameters_sets[subset]["start"][2] = f
        self.__save_all()


def create_folder(new_folder_path):
    p = pathlib.Path(new_folder_path)
    if not p.exists():
        p.mkdir()

#main loop
if __name__ == "__main__": 
    p = ParametersSets()
    print(p.get_default())
    p.make_default("Default")
    print(p.get_default())
