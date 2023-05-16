#generate a list of named absolute position as dictionary
import tkinter as tk
from .parametersIO import *
from .microscope import *
from .cameracontrol import *


class PositionsGrid:

    def __init__(self, microscope, parameters):
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

        for l in range (0, parameters["lines"]):
            x = parameters['start'][0] + parameters['Xsteps']*l

            for c in range(0, parameters["columns"]):
                y = parameters['start'][1] + parameters['Ysteps']*c

                z = parameters['start'][2]

                sub_position = {}
                for s in range (0, parameters["subwells"]):
                    sub_position[s+1] = [x + parameters["subwells_spacing"][0] * s, y + parameters["subwells_spacing"][1] * s, z + parameters["subwells_spacing"][2] * s]

                absolute_grid[str(self.line_namespace[l])+str(c+1)] = sub_position

        #initialise nb_of_subwell for subwell switching fct
        self.nb_of_subwells = self.parameters.get()["subwells"]

        self.absolute_grid = absolute_grid
        return absolute_grid
    
    def go(self, well, subwell=1):
        self.microscope.go_absolute(self.absolute_grid[well][subwell])
        self.current_grid_position = [well, subwell]
    
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
        microscope_position = self.microscope.checked_read_positions()[:3]

        for well in self.absolute_grid:
            for subwell in self.absolute_grid[well]:
                if self.absolute_grid[well][subwell] == microscope_position:
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


#main loop
if __name__ == "__main__":
    from .cameracontrol import *
    import picamera

    microscope = Microscope(addr, ready_pin)

    #start picamPreview
    camera = picamera.PiCamera()
    #previewPiCam(camera)
    Tk_root = tk.Tk()
    grid = PositionsGrid(microscope)
    #interface = Grid_popup(microscope, grid, camera, Tk_root)
    #microscope.set_ledpwr(200)
    #Tk_root.mainloop()

