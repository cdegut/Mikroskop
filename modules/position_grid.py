#generate a list of named absolute position as dictionary
from .parametersIO import *
from .microscope import *

class PositionsGrid:

    def __init__(self, microscope: MicroscopeManager, parameters: ParametersSets):
        self.microscope = microscope
        self.current_grid_position = ["##",1]
        self.line_namespace = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.parameters = parameters
        self.absolute_grid = self.generate_grid()
        self.find_current_position()



    def generate_grid(self):
        # generate the position grid of all the well and subwell based onthe parameter file
        # the grid is a dictionary of well, containing dictionary of subwell
        absolute_grid = {}
        parameters =  self.parameters.get()
        fx = parameters["XYFocusDrift"][0]
        fy = parameters["XYFocusDrift"][1]
        sx = parameters["XYaxisSkew"][0]
        sy = parameters["XYaxisSkew"][1]

        for l in range (0, parameters["lines"]):
            
            for c in range(0, parameters["columns"]):

                x = parameters['start'][0] + parameters['Xsteps']*l + (sx * c)

                y = parameters['start'][1] + parameters['Ysteps']*c + (sy * l)

                f = parameters['start'][2] +  (fx * l ) + (fy * c)

                sub_position = {}
                for s in range (0, parameters["subwells"]):
                    sub_position[s+1] = [x + parameters["subwells_spacing"][0] * s, y + parameters["subwells_spacing"][1] * s, f + parameters["subwells_spacing"][2] * s]

                absolute_grid[str(self.line_namespace[l])+str(c+1)] = sub_position


        #initialise nb_of_subwell for subwell switching fct
        self.nb_of_subwells = self.parameters.get()["subwells"]

        self.absolute_grid = absolute_grid
        return absolute_grid
    
    def go(self, well, subwell=1):
        self.microscope.request_XYF_travel(self.absolute_grid[well][subwell], trajectory_corection=True)
        self.current_grid_position = [well, subwell]
    
    def at_position(self):
        return self.microscope.at_position
 
    def go_next_well(self, direction="line", value_move=1):

        self.find_current_position()

        if self.current_grid_position == ["##",1]:
            return
        
        if direction == "line":
            #find the next letter in the namspace

            next_well = self.line_namespace[self.line_namespace.index(self.current_grid_position[0][0]) + value_move] + self.current_grid_position[0][1:] 
            if next_well in self.absolute_grid:
                self.go(str(next_well),self.current_grid_position[1])
        
        if direction == "column":
            #find the next letter in the namspace

            next_well = self.current_grid_position[0][0] + str(int(self.current_grid_position[0][1:]) + value_move)
            if next_well in self.absolute_grid:
                self.go(str(next_well),self.current_grid_position[1])
    
    def find_current_position(self):
        #iterate through all the possible well position to find a match

        X_range = range(self.microscope.XYFposition[0] + undershoot_X , self.microscope.XYFposition[0] + overshoot_X+1)
        Y_range = range(self.microscope.XYFposition[1] + undershoot_Y , self.microscope.XYFposition[1] + overshoot_Y+1)
        F_range = range(self.microscope.XYFposition[2] - 15 , self.microscope.XYFposition[2] + 15)

        for well in self.absolute_grid:
            for subwell in self.absolute_grid[well]:
                if self.absolute_grid[well][subwell][0] in (X_range) and self.absolute_grid[well][subwell][1] in (Y_range):

                    self.current_grid_position = [well, subwell]
                    return [well, subwell]
        
        return ["##", 1]
    
    def switch_subwell(self, value=1):

        next_subwell = (self.current_grid_position[1] + value) % self.nb_of_subwells
        if next_subwell == 0: 
            next_subwell = self.nb_of_subwells
        self.go(self.current_grid_position[0], next_subwell)

    def generate_position_list(self, start="A1", finish="H12", subwell=1):
    #make a recantgle selection of the position between start and finish and generate a list.
        lines = self.line_namespace[self.line_namespace.index(start[0]):self.line_namespace.index(finish[0])+1]
        columns = range(int(start[1:]), int(finish[1:])+1)

        positions = []
        for l in lines:
            for c in columns:
                for s in range(1, subwell+1):
                    position = [(str(l) + str(c)), s]
                    positions.append(position)


        return positions

