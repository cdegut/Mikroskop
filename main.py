from RPi import GPIO
from os import environ
from PyQt5.QtWidgets import  QApplication 
from PyQt5 import QtCore

from modules.cameracontrol import Microscope_camera
from modules.microscope import Microscope
from modules.position_grid import PositionsGrid
from modules.physical_controller import encoder_read, controller_startup
from modules.interface.main_menu import *
from modules.microscope_param import *
from modules.parametersIO import ParametersSets
#from modules.interface.control_overlay import Overlay
from modules.interface.picameraQT import MainApp
import customtkinter
import sys

def tk_loop():
    ##Read physical interface
    encoder_read(microscope, encoder_X,1,X_controller_short, X_controller_long)
    encoder_read(microscope, encoder_Y,2,Y_controller_short, Y_controller_long)
    encoder_read(microscope, encoder_F,3,F_controller_short, F_controller_long)

    #Tkinter mainloop
    Tk_root.update_idletasks()
    Tk_root.update()
    if Interface._exit == True:
        app.quit()

if __name__ == "__main__": 

    encoder_X, encoder_Y, encoder_F = controller_startup()                
    ### Object for microscope to run
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin, parameters)
    grid = PositionsGrid(microscope, parameters)
    micro_cam = Microscope_camera(microscope)
    
    #Tkinter object
    customtkinter.set_appearance_mode("dark")
    Tk_root = customtkinter.CTk()
    Tk_root.geometry("230x564+804+36")

    ### Don't display border if on the RPi display
    display = environ.get('DISPLAY')
    if display == ":0.0" or display == ":0": ## :0.0 in terminal and :0 without terminal
        Tk_root.overrideredirect(1)
        export = False
    else:
        export = True

    ## this avoid an error with CV2 and Qt, it clear all the env starting with QT_
    for k, v in environ.items():
        if k.startswith("QT_") and "cv2" in v:
            del environ[k]   
    
    Interface._main_menu = MainMenu(Tk_root, microscope=microscope, grid=grid, camera=micro_cam,  parameters=parameters)
    
    app = QApplication(sys.argv)
    preview_window = MainApp(micro_cam, microscope, export)

    #access neede to interact with preview when doing captures
    micro_cam.qpicamera = preview_window.main_widget.qpicamera2 

    # run the old Tk interace in a Qt timer
    timer = QtCore.QTimer()
    timer.timeout.connect(tk_loop)
    timer.start(10)

    sys.exit(app.exec_())

    #GPIO cleanup
    GPIO.cleanup()
