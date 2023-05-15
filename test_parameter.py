import json
import pathlib

def load_parameters(subset):
    current_path = str(pathlib.Path(__file__).parent.absolute())
    with open(current_path + "/tests/param.json", "r") as param_file:
        parameters = json.load(param_file)
    return parameters[subset]

def save_parameters(parameters):
    current_path = str(pathlib.Path(__file__).parent.absolute())
    with open(current_path + "/tests/param.json", "w") as param_file:
        json.dump(parameters, param_file)

parameters_plate = load_parameters("Plate")
print(parameters_plate["lines"])