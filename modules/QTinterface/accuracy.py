from PyQt5.QtWidgets import QApplication, QPushButton,  QWidget, QVBoxLayout, QMainWindow, QHBoxLayout, QDockWidget, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
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
        layout = QVBoxLayout()
        # Add widgets to the layout
        self.static = QPushButton("Static test")
        self.static.setCheckable(True)
        self.static.clicked.connect(self.static_test)
        layout.addWidget(self.static)

        self.accuracy = QPushButton("Accuracy test")
        self.accuracy.toggle()
        self.accuracy.clicked.connect(self.accuracy_test)
        layout.addWidget(self.accuracy)

        self.autotune = QPushButton("Autotune")
        #self.autotune.toggle()
        self.autotune.setCheckable(True)
        self.autotune.clicked.connect(self.accuracy_autotune)
        layout.addWidget(self.autotune)

        label = QLabel("--", parent=self)
        label.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Transparent background
        label.setFont(QFont("Arial", 12))
        label.setAlignment(Qt.AlignCenter)  # Align text
        layout.addWidget(label)
        self.setLayout(layout)

        self.tester = AccuracyTester(microscope=main_window.microscope, position_grid=main_window.position_grid, 
                                     camera=main_window.camera,  parameters=main_window.parameters, infobox=label)


    def static_test(self):
        if  self.static.isChecked():
            self.tester.initiate_files(f_name = "static_test")
            self.static.setText("Runing")
            self.tester.start_testing("static")
        else:
            self.static.setText("Static")
            self.tester.timer.disconnect()

    def accuracy_test(self):
        if  not self.accuracy.isChecked():
            self.tester.initiate_files(f_name = "accuracy_test")
            self.accuracy.setText("Runing")
            self.tester.start_testing("accuracy test")
        else:
            self.static.setText("Static")
            self.tester.timer.disconnect()

    
    def accuracy_autotune(self):
        if  self.autotune.isChecked():
            self.tester.initiate_files(f_name = "error_autotune")
            self.autotune.setText("Runing")
            self.microscope.config_trajectory_corection(0,0,0,0)
            self.tester.start_testing("accuracy autotune")
        else:
            self.autotune.setText("Autotune")
            self.tester.timer.disconnect()


    
 
