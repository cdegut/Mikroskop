from RPi import GPIO
from os import environ
from PyQt5.QtWidgets import  QApplication 
from PyQt5 import QtCore
from modules.interface.main_menu import *
from modules.QTinterface.main_app import MainApp
import sys
from modules.controllers import *
repeat_before_tune = 50


if __name__ == "__main__": 
 
    ### Don't display border if on the RPi display
    display = environ.get('DISPLAY')
    if display == ":0.0" or display == ":0": ## :0.0 in terminal and :0 without terminal
        export = False
    else:
        export = True

    ## this avoid an error with CV2 and Qt, it clear all the env starting with QT_
    for k, v in environ.items():
        if k.startswith("QT_") and "cv2" in v:
            del environ[k]   
    
    app = QApplication(sys.argv)
    parameters = ParametersSets()
    microscope = MicroscopeManager(addr, ready_pin, parameters)
    position_grid = PositionsGrid(microscope, parameters)
    micro_cam = Microscope_camera(microscope)
    main_window = MainApp(microscope=microscope, position_grid=position_grid, camera=micro_cam,parameters=parameters, export=export, special_mode= "accuracy_test")

    sys.exit(app.exec_())

    #GPIO cleanup
    GPIO.cleanup()
