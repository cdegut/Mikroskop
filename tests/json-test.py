import json
import pathlib

#parameter = { "lines": 2 , "columns" : 2, "repeat" :  10, "delay" : 20, "xstep" :1790,"ystep" : 7250,"hyst" : 10 }
with open(str(pathlib.Path(__file__).parent.absolute()) + "/param.json", "r") as grid_param:
    parameters = json.load(grid_param)

print(parameters["start"][1])