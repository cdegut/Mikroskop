#Software Endstop (need to be =< to hardware set endstop)
from dataclasses import dataclass, asdict
import json

software_endstops = True
Xmaxrange = 70000
Ymaxrange = 93000
Fmaxrange = 30000

overshoot_X = -16
undershoot_X = -4
overshoot_Y = -100
undershoot_Y = +40

#fluorescent gain value
awbR_fluo = 1
awbB_fluo = 0.35
awbR_white = 3
awbB_white = 0.8

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
        with open("microscope_param.json", "w") as param_file:
            json.dump(asdict(self), param_file)

    def load(self):
        try:
            with open("microscope_param.json", "r") as param_file:
                loaded = json.load(param_file)
                self.__init__(**loaded)
        except:
            self.save()

    

param = MicroscopeParameters()
param.load()





