from PyQt5.QtWidgets import QApplication, QPushButton,  QWidget, QVBoxLayout, QMainWindow, QHBoxLayout, QDockWidget
from modules.controllers import *
from modules.controllers.cameracontrol import Microscope_camera
from modules.controllers.microscope import MicroscopeManager
from modules.controllers.pins import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main_app import MainApp

class AccuracyPanel(QWidget):
    def __init__(self, main_window: 'MainApp'):
        super(QWidget, self).__init__(main_window)
        self.camera: Microscope_camera = main_window.camera
        self.microscope: MicroscopeManager = main_window.microscope
        self.setGeometry(preview_resolution[0],0, 1024 - preview_resolution[0], 580)
        self.tester = AccuracyTester(microscope=main_window.microscope, position_grid=main_window.position_grid, camera=main_window.camera,  parameters=main_window.parameters)

        layout = QVBoxLayout()
        # Add widgets to the layout
        self.static = QPushButton("Static test")
        self.static.toggle()
        self.static.clicked.connect(self.static_test)
        layout.addWidget(self.static)

        self.accuracy = QPushButton("Accuracy test")
        self.accuracy.toggle()
        self.accuracy.clicked.connect(self.accuracy_test)
        layout.addWidget(self.accuracy)

        self.autotune = QPushButton("Autotune")
        self.autotune.toggle()
        self.autotune.clicked.connect(self.accuracy_autotune)
        layout.addWidget(self.autotune)

        self.setLayout(layout)

    def static_test(self):
        if not self.static.isChecked():
            self.tester.initiate_files()
            self.static.setText("Runing")
            self.tester.start_testing("static")
        else:
            self.static.setText("Static")
            self.tester.timer.disconnect()

    def accuracy_test(self):
        self.tester.initiate_files()
        self.accuracy.setText("Runing")
        self.tester.start_testing("accuracy")
    
    def accuracy_autotune(self):
        self.tester.initiate_files()
        self.autotune.setText("Runing")
        self.microscope.config_trajectory_corection(0,0,0,0)
        self.tester.start_testing("accuracy autotune")


    
 
