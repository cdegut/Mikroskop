import picamera
import tkinter as tk
from RPi import GPIO
from os import environ

from modules.cameracontrol import previewPiCam
from modules.microscope import Microscope
from modules.position_grid import PositionsGrid
from modules.physical_controller import encoder_read, controller_startup
from modules.interface.main_menu import *
from modules.microscope_param import *
from modules.parametersIO import ParametersSets


#main loop
if __name__ == "__main__": 


    ### Object for microscope to run
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin, parameters)
    grid = PositionsGrid(microscope, parameters)
    camera = picamera.PiCamera()

    #Tkinter object
    Tk_root = tk.Tk()
    Tk_root.geometry("230x560+800+35")   
    
    ### Don't display border if on the RPi display
    display = environ.get('DISPLAY')
    if display == ":0.0" or display == ":0": ## :0.0 in terminal and :0 without terminal
        Tk_root.overrideredirect(1) ### not working with remote display !!
    Interface._main_menu = MainMenu(Tk_root, microscope=microscope, grid=grid, camera=camera,  parameters=parameters)

    #start picamPreview
    previewPiCam(camera)


    encoder_X, encoder_Y, encoder_F = controller_startup()

    ## Microscope controller main loop
    while not Interface._exit:

        ##Read physical interface
        encoder_read(microscope, encoder_X,1,X_controller_short, X_controller_long)
        encoder_read(microscope, encoder_Y,2,Y_controller_short, Y_controller_long)
        encoder_read(microscope, encoder_F,3,F_controller_short, F_controller_long)


        #Tkinter mainloop
        Tk_root.update_idletasks()
        Tk_root.update()

    Tk_root.destroy()

    #GPIO cleanup
    GPIO.cleanup()