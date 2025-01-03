from RPi import GPIO
from os import environ
from PyQt5.QtWidgets import  QApplication 
from PyQt5 import QtCore

from modules.controllers import *
from modules.interface.main_menu import *
from modules.controllers.pins import *
from modules.QTinterface.main_app import MainApp
import customtkinter
import sys

def tk_loop():
    #Tkinter mainloop
    Tk_root.update_idletasks()
    Tk_root.update()
    if Interface._exit == True:
        app.quit()

if __name__ == "__main__": 
            
    
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
     
    ### Object for microscope to run
    app = QApplication(sys.argv)
    grid_parameters = GridParameters()
    grid_parameters.load_last_selected()
    microscope = MicroscopeManager(addr, ready_pin)
    position_grid = PositionsGrid(microscope, grid_parameters)
    micro_cam = Microscope_camera(microscope)
    controller = PhysicalController(microscope)
    preview_window = MainApp(microscope=microscope, position_grid=position_grid, camera=micro_cam,parameters=grid_parameters, export=export)

    Interface._main_menu = MainMenu(Tk_root, microscope=microscope, position_grid=position_grid, camera=micro_cam,  parameters=grid_parameters)


    # run the old Tk interace in a Qt timer
    tk_timer = QtCore.QTimer()
    tk_timer.timeout.connect(tk_loop)
    tk_timer.start(10)

    sys.exit(app.exec_())

    #GPIO cleanup
    GPIO.cleanup()
