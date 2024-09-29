import sys, os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QLabel, QCheckBox, QWidget, QTabWidget, QVBoxLayout, QGridLayout)
from picamera2.previews.qt import QGlPicamera2, QPicamera2
from PyQt5 import QtCore
from ..microscope_param import preview_resolution
from libcamera import Transform
import sys

preview_resolution = (804, 580)
class MainApp(QMainWindow):

    def __init__(self, micro_cam, microscope, export=False):
        super().__init__()
        self.setGeometry(0, 0, preview_resolution[0], preview_resolution[1])
        self.export = export
        self.setWindowTitle("PiCameraPreview")
        self.main_widget = PreviewWidget(self, micro_cam, microscope, export)
        self.setCentralWidget(self.main_widget)
        if not export:
            self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint));             
        self.show()


class PreviewWidget(QWidget): 
        
    def __init__(self, parent, micro_cam, microscope, export):
        super(QWidget, self).__init__(parent)
        self.micro_cam = micro_cam
        self.microscope = microscope

        # Preview qpicamera2  
        '''
        if export:
            self.qpicamera2 = QPicamera2(self.micro_cam,
                            width=preview_resolution[0], height=preview_resolution[1],
                            keep_ar=False)
        else:
            self.qpicamera2 = QGlPicamera2(micro_cam,
                            width=preview_resolution[0], height=preview_resolution[1],
                            keep_ar=False)
        '''
        #QGL Picamera supposed to be better, but bug with button tranparancy
        self.qpicamera2 = QPicamera2(self.micro_cam, width=preview_resolution[0], height=preview_resolution[1], keep_ar=False, transform=Transform(vflip=1))

        
 
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.qpicamera2)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.overlay()
        micro_cam.start()

    def overlay(self):

        class ScrollButton(QPushButton):

            def __init__(self, text, position, size, style, direction, microscope, parent):
                super().__init__(parent)
                self.scrollTimer = QtCore.QTimer()
                self.setText(text)
                self.setGeometry(position[0],position[1], size, size)
                self.setStyleSheet(style)
                self.pressed.connect(lambda: self.start_scroll(direction))
                self.released.connect(self.stop_scroll)
                self.microscope = microscope

            def start_scroll(self, direction):
                self.microscope.push_axis(direction[0] , direction[1])
                self.scrollTimer.timeout.connect(lambda: self.microscope.push_axis(direction[0] , direction[1]))
                self.scrollTimer.start(200)

            def stop_scroll(self):
                self.scrollTimer.stop()
                self.scrollTimer.timeout.disconnect()

        button_size = 80
        half = int(button_size/2)
        button_style = f"border-radius : {button_size/2}; border : 2px solid black; background-color: rgba(94,150,174,128)"
        focus_button_style = f"border-radius : {button_size/2}; border : 2px solid black; background-color: rgba(241,224,176,128)"

        Up = ScrollButton("X+", (int(preview_resolution[0]/2)-half,0), button_size, button_style, (1, 100), self.microscope, self)
        Down = ScrollButton("X-", (int(preview_resolution[0]/2)-half, preview_resolution[1] - button_size -10), button_size, button_style, (1, -100), self.microscope, self)
        Left = ScrollButton("Y-", (0,int(preview_resolution[1]/2)-half), button_size, button_style, (2, -100), self.microscope, self)
        Right = ScrollButton("Y+", (preview_resolution[0] - button_size -5,int(preview_resolution[1]/2)-half), button_size, button_style, (2, 100), self.microscope, self)
        Fplus = ScrollButton("F+", (0,0), button_size, focus_button_style, (3, 50), self.microscope, self)
        Fminus = ScrollButton("F-", (0,button_size +10), button_size, focus_button_style, (3, -50), self.microscope, self)


if __name__ == '__main__':
    from os import environ
    from ..microscope import Microscope
    from ..microscope_param import *
    from ..parametersIO import ParametersSets
    from PyQt5 import QtCore


    from picamera2 import Picamera2

    def timer_exec():
        print(micro_cam.metadata)

    #micro_cam = Picamera2()

    display = environ.get('DISPLAY')
    if display == ":0.0" or display == ":0": ## :0.0 in terminal and :0 without terminal
        export = False
    else:
        export = True
    
    micro_cam =  Picamera2()
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin, parameters)

    ## this avoid an error with CV2 and Qt, it clear all the env starting with QT_
    for k, v in os.environ.items():
        if k.startswith("QT_") and "cv2" in v:
            del os.environ[k]

    app = QApplication([])
    ex = MainApp(micro_cam, microscope, export)
    sys.exit(app.exec_())
