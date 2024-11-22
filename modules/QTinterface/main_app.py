from PyQt5.QtWidgets import QMainWindow

from modules.controllers import position_grid
from .picameraQT import PreviewWidget
from PyQt5 import QtCore

from modules.controllers.microscope_param import *
from modules.controllers import *

class MainApp(QMainWindow):

    def __init__(self, microscope: MicroscopeManager, position_grid: PositionsGrid, camera: Microscope_camera,  parameters: ParametersSets, export: bool):
        super().__init__()
        self.setGeometry(0, 0, 1024, 580)
        self.export = export
        self.setWindowTitle("PiCameraPreview")
        self.main_widget = PreviewWidget(self, camera, microscope)
        self.main_widget.resize(preview_resolution[0], preview_resolution[1])
        self.setCentralWidget(self.main_widget)
        if not export:
            self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint));             
        self.show()