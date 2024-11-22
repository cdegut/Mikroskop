from PyQt5 import QtCore
from .encoder_class import Encoder
from modules.controllers import MicroscopeManager
from .microscope_param import *

class PhysicalController:

    def __init__(self, microscope: MicroscopeManager):
        self.__encoder_X, self.__encoder_Y, self.__encoder_F = self.__controller_startup()
        self.microscope = microscope
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(100)

    def __encoder_read(self, encoder:Encoder, axis:str, short_steps:int, long_steps:int):
        value = encoder.internal_counter
        if value == 0:
            return
        ## Check state to know if doing large or small movement, calculate steps accordingly
        if encoder.sw_state:
            steps = short_steps * value
        else:
            steps = long_steps * value

        self.microscope.request_push_axis(axis , steps)
        encoder.internal_counter = 0

    def __controller_startup(self):
        
            #Generate the objects for the physical interface
        try:
            encoder_F = Encoder(F_controller_pinA, F_controller_pinB, "up", F_controller_Switch)
            encoder_Y = Encoder(Y_controller_pinA , Y_controller_pinB ,"up",Y_controller_Switch)
            encoder_X = Encoder(X_controller_pinA, X_controller_pinB,"up",X_controller_Switch)
        except: ##sometimes crash, try to redo it after gpio cleanup
            from RPi import GPIO
            GPIO.cleanup()
            GPIO.setmode(GPIO.BCM)
            print("Trying the controller set up again")
            encoder_F = Encoder(F_controller_pinA, F_controller_pinB, "up", F_controller_Switch)
            encoder_Y = Encoder(Y_controller_pinA , Y_controller_pinB ,"up",Y_controller_Switch)
            encoder_X = Encoder(X_controller_pinA, X_controller_pinB,"up",X_controller_Switch)
        
        return encoder_X, encoder_Y, encoder_F
    
    def run(self):
        self.__encoder_read(self.__encoder_X,"X",X_controller_short, X_controller_long)
        self.__encoder_read(self.__encoder_Y,"Y",Y_controller_short, Y_controller_long)
        self.__encoder_read(self.__encoder_F,"F",F_controller_short, F_controller_long)


