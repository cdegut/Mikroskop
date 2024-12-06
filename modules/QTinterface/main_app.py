from PyQt5.QtWidgets import QMainWindow, QHBoxLayout

from modules.controllers import *
from .picameraQT import PreviewWidget
from PyQt5 import QtCore
from modules.controllers.pins import *
from modules.controllers import *
from modules.QTinterface import AccuracyPanel, LEDPanel

class MainApp(QMainWindow):

    def __init__(self, microscope: MicroscopeManager, position_grid: PositionsGrid, camera: Microscope_camera,  parameters: GridParameters, export: bool, special_mode:str = None, video:bool =True):
        super().__init__()

        self.microscope: MicroscopeManager = microscope
        self.camera: Microscope_camera = camera
        self.parameters: GridParameters = parameters
        self.position_grid: PositionsGrid = position_grid

        self.setGeometry(0, 0, 1024, 580)

        #main_layout = QHBoxLayout()

        self.export = export
        self.setWindowTitle("PiCameraPreview")

        if video:
            self.preview_widget = PreviewWidget(self, camera, microscope)
            #main_layout.addWidget(self.preview_widget)
            self.preview_widget.resize(preview_resolution[0], preview_resolution[1])
            self.camera.qpicamera = self.preview_widget.qpicamera2 #access neede to interact with preview when doing captures
            self.setCentralWidget(self.preview_widget)

        if special_mode == "accuracy_test":
            self.side_panel = AccuracyPanel(main_window=self)      

        if special_mode == "LED":
            self.side_panel = LEDPanel(main_window=self)     

        if not export:
            self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint));             
        self.show()

