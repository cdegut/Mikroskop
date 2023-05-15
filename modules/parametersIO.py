import json
import pathlib

def load_parameters(subset = "Default"):
    current_path = str(pathlib.Path(__file__).parent.absolute())
    with open(current_path + "/../param.json", "r") as param_file:
        parameters = json.load(param_file)
    return parameters[subset]

def load_all_parameters():
    current_path = str(pathlib.Path(__file__).parent.absolute())
    with open(current_path + "/../param.json", "r") as param_file:
        parameters = json.load(param_file)
    return parameters

def save_all_parameters(parameters):
    current_path = str(pathlib.Path(__file__).parent.absolute())
    with open(current_path + "/../param.json", "w") as param_file:
        json.dump(parameters, param_file)


#### updaate parameter from a list of tuple with the format : [("keyA", value ), ("keyB", value)]
def update_parameters(param_list, subset="Default"):
    all_parameters = load_all_parameters()
    for parameter in param_list:
        all_parameters[subset][parameter[0]] = parameter[1]
    save_all_parameters(all_parameters)

def update_parameters_start(x,y,f,subset="Default"):
    all_parameters = load_all_parameters()
    if x:    
        all_parameters[subset]["start"][0] = x
    if y:
        all_parameters[subset]["start"][1] = y
    if f:
        all_parameters[subset]["start"][2] = f
    save_all_parameters(all_parameters)


def create_folder(new_folder_path):
    p = pathlib.Path(new_folder_path)
    if not p.exists():
        p.mkdir()
