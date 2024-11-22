import sys, os
from PyQt5.QtWidgets import QApplication, QPushButton,  QWidget, QVBoxLayout, QMainWindow
from picamera2.previews.qt import QGlPicamera2, QPicamera2
from PyQt5 import QtCore
from libcamera import Transform
import sys

from modules.controllers import *
from modules.controllers.microscope_param import *

class ScrollButton(QPushButton):

    def __init__(self, text:str, position: list[int,int], size:int, style:str, direction:str, 
                 coarse:int, fine:int, microscope:MicroscopeManager, parent:QWidget):
        super().__init__(parent)
        self.scrollTimer = QtCore.QTimer()
        self.setText(text)
        self.setGeometry(position[0],position[1], size, size)
        self.setStyleSheet(style)
        self.movement = [direction, coarse]
        self.pressed.connect(self.start_scroll)
        self.released.connect(self.stop_scroll)
        self.microscope = microscope
        self.coarse = coarse
        self.fine = fine
        self.fine_move = False

    def start_scroll(self):
        self.microscope.request_push_axis(self.movement[0] , self.movement[1])
        self.scrollTimer.timeout.connect(lambda: self.microscope.request_push_axis(self.movement[0] , self.movement[1]))
        self.scrollTimer.start(100)

    def stop_scroll(self):
        self.scrollTimer.stop()
        self.scrollTimer.timeout.disconnect()
    
    def toggle_fine_move(self):
        if self.fine_move == True:
            self.movement[1] = self.coarse
            self.fine_move = False
        else:
            self.movement[1] = self.fine
            self.fine_move = True

class PreviewWidget(QWidget): 
        
    def __init__(self, parent: QMainWindow, micro_cam: Microscope_camera, microscope: MicroscopeManager):
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
        self.layout.setContentsMargins(0, 0, 230, 0)
        self.setLayout(self.layout)
        micro_cam.start()


        button_size = 80
        half = int(button_size/2)
        button_style = f"border-radius : {button_size/2}; border : 2px solid black; background-color: rgba(94,150,174,128)"
        focus_button_style = f"border-radius : {button_size/2}; border : 2px solid black; background-color: rgba(241,224,176,128)"
        self.toggle_button_style = f"border-radius : {button_size/2}; border : 2px solid black; background-color: rgba(252,225,228,128)"
        self.toggle_button_style_off = f"border-radius : {button_size/2}; border : 2px solid black; background-color: rgba(252,225,0,128)"

        
        self.Fine = QPushButton(self)
        self.Fine.setCheckable(True)
        self.Fine.toggle()
        self.Fine.setGeometry(0,580 - button_size -15,80,80)
        self.Fine.setStyleSheet(self.toggle_button_style)
        self.Fine.clicked.connect(self.fine_toggle)
        self.Fine.setText("Coarse")

        Up = ScrollButton("X+", (int(preview_resolution[0]/2)-half,0), button_size, button_style, "X", 100, 10, self.microscope, self)
        Down = ScrollButton("X-", (int(preview_resolution[0]/2)-half, 580 - button_size -15), button_size, button_style, "X", -100, -10, self.microscope, self)
        Left = ScrollButton("Y-", (0,int(preview_resolution[1]/2)-half), button_size, button_style, "Y", -100, -10, self.microscope, self)
        Right = ScrollButton("Y+", (preview_resolution[0] - button_size -5,int(preview_resolution[1]/2)-half), button_size, button_style, "Y", 100, 10, self.microscope, self)
        Fplus = ScrollButton("F+", (0,0), button_size, focus_button_style, "F", 50, 5, self.microscope, self)
        Fminus = ScrollButton("F-", (0,button_size +10), button_size, focus_button_style, "F", -50, -5, self.microscope, self)
        self.scrollable = [Up, Down, Left, Right, Fplus, Fminus]
    
    def fine_toggle(self):
        if self.Fine.isChecked():
            self.Fine.setStyleSheet(self.toggle_button_style)
            for button in self.scrollable:
                button.toggle_fine_move()
                self.Fine.setText("Coarse")
        else:
            self.Fine.setStyleSheet(self.toggle_button_style_off)
            for button in self.scrollable:
                button.toggle_fine_move()
                self.Fine.setText("Fine")
 

if __name__ == '__main__':
    from os import environ



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
    microscope = MicroscopeManager(addr, ready_pin, parameters)

    ## this avoid an error with CV2 and Qt, it clear all the env starting with QT_
    for k, v in os.environ.items():
        if k.startswith("QT_") and "cv2" in v:
            del os.environ[k]

    from .main_app import MainApp

    app = QApplication([])
    ex = MainApp(micro_cam, microscope, export)
    sys.exit(app.exec_())
