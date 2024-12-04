from PyQt5.QtWidgets import QApplication, QPushButton,  QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QHBoxLayout, QDockWidget, QSlider, QDial
from PyQt5 import QtCore
from modules.controllers import *
from modules.controllers.cameracontrol import Microscope_camera
from modules.controllers.microscope import MicroscopeManager
from modules.controllers.pins import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main_app import MainApp

class LEDPanel(QWidget):
    def __init__(self, main_window: 'MainApp'):
        super(QWidget, self).__init__(main_window)
        self.camera: Microscope_camera = main_window.camera
        self.microscope: MicroscopeManager = main_window.microscope
        self.setGeometry(preview_resolution[0],0, 1024 - preview_resolution[0], 580)

        layout = QHBoxLayout()
        # Add widgets to the layout
        self.slider_led1 = QDial()
        self.slider_led1.setOrientation(QtCore.Qt.Horizontal)
        self.slider_led1.valueChanged.connect(self.set_LED_1)
        self.slider_led1.setRange(0,100)
        self.slider_led1.setValue(self.microscope.led1pwr)
        layout.addWidget(self.slider_led1)

        self.slider_led2 = QDial()
        self.slider_led2.setOrientation(QtCore.Qt.Horizontal)
        self.slider_led2.valueChanged.connect(self.set_LED_2)
        self.slider_led2.setRange(0,100)
        self.slider_led2.setValue(self.microscope.led2pwr)
        layout.addWidget(self.slider_led2)
        #self.slider.setGeometry(QRect(190, 100, 160, 16))
        self.setLayout(layout)

    def set_LED_1(self, value):
        self.microscope.request_ledspwr(value, None)

    def set_LED_2(self, value):
        self.microscope.request_ledspwr(None,value)
 

    
 
