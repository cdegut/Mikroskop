import json
import pathlib

def load_parameters():
    current_path = str(pathlib.Path(__file__).parent.absolute())
    with open(current_path + "/../param.json", "r") as param_file:
        parameters = json.load(param_file)
    return parameters

def save_parameters(parameters):
    current_path = str(pathlib.Path(__file__).parent.absolute())
    with open(current_path + "/../param.json", "w") as param_file:
        json.dump(parameters, param_file)

def update_parameters(param_list):
    parameters = load_parameters()
    for parameter in param_list:
        parameters[parameter[0]] = parameter[1]
    save_parameters(parameters)

def update_parameters_start(x,y,f):
    parameters = load_parameters()
    if x:    
        parameters["start"][0] = x
    if y:
        parameters["start"][1] = y
    if f:
        parameters["start"][2] = f
    save_parameters(parameters)

def update_parameters_led(pwr,state):
    parameters = load_parameters()
    if pwr:    
        parameters["start"][3] = pwr       
    if state:    
        parameters["start"][4] = state
    save_parameters(parameters)

def create_folder(new_folder_path):
    p = pathlib.Path(new_folder_path)
    if not p.exists():
        p.mkdir()
