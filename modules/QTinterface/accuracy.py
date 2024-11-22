from PyQt5.QtWidgets import QApplication, QPushButton,  QWidget, QVBoxLayout, QMainWindow
from controllers import *




class AccuracyPanel(QWidget):
    def __init__(self, parent: QMainWindow, micro_cam, microscope: MicroscopeManager):
        super(QWidget, self).__init__(parent)
        self.micro_cam = micro_cam
        self.microscope = microscope
        tester = AccuracyTester(microscope=microscope, position_grid=position_grid, camera=micro_cam,  parameters=parameters)
