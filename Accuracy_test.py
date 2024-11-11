from RPi import GPIO
from os import environ
from PyQt5.QtWidgets import  QApplication 
from PyQt5 import QtCore

from modules.cameracontrol import Microscope_camera
from modules.microscope import Microscope
from modules.position_grid import PositionsGrid
from modules.physical_controller import encoder_read, controller_startup
import time
import os
from modules.interface.main_menu import *
from modules.microscope_param import *
from modules.parametersIO import ParametersSets, create_folder
import random
import numpy as np
#from modules.interface.control_overlay import Overlay
from modules.interface.picameraQT import MainApp
import customtkinter
import sys
import cv2

class Accuracy_tester():
    def __init__(self, microscope: Microscope, position_grid: PositionsGrid, camera: Microscope_camera,  parameters: ParametersSets):
        self.microscope = microscope
        self.position_grid = position_grid
        self.camera = camera
        self.parameters = parameters

        self.execute_function = self.testing_loop
        self.loop_progress = 'init'

        #Grid Recording parameters
        self.positions_list = None
        self.delay_value = None
        self.repeat_value = None
        self.done_repeat = 0
        self.index_position = 0
        self.pic_taken = False
        self.pre_pic_timer = 0
        self.grid_folder = None
        self.grid_subwells_value = None
        self.pause_timer =0
        self.is_regording = False
        self.camera_is_init = False

        self.start_image = None
        self.current_image = None

        self.errors_list = np.empty((0,2))

        self.start = self.parameters.get()["start"]
        self.target_position = self.parameters.get()["start"]

        self.microscope.go_absolute(self.target_position)

            #reset everything
        self.is_regording = True

        self.positions_list = None
        self.done_repeat = 0
        self.pic_taken = False
        self.pre_pic_timer = 0
        self.grid_subwells_value = None
        self.pause_timer =0

        if self.microscope.led1pwr ==0:
            self.microscope.set_ledspwr(50,0)

        current_time = time.localtime()        
        date = str(current_time[0])[2:] + str(current_time[1]).zfill(2) + str(current_time[2]).zfill(2) + "_"  \
            + str(current_time[3]).zfill(2) + str(current_time[4]).zfill(2)
        data_dir = self.parameters.get()["data_dir"]      
        home = os.getenv("HOME")
        self.test_folder = f"{home}/{data_dir}/accuracy_test-{date}/"

        #create_folder(self.test_folder)


    def at_position(self)  -> bool:
        self.microscope.update_real_state()
        if self.microscope.XYFposition == self.target_position:
            return True
        else:
            return False
    
    def process_difference(self):
        gray1 = cv2.cvtColor(self.start_image, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        # Detect ORB features and descriptors
        orb = cv2.ORB_create()
        keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
        keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)

        # Use BFMatcher to find matches
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptors1, descriptors2)

        # Sort the matches based on distance (best matches first)
        matches = sorted(matches, key=lambda x: x.distance)

        # Extract the matched keypoints
        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        # Find the homography matrix (in this case, we only need the translation)
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Extract translation values from the homography matrix
        translation_x = H[0, 2]  # Translation in X
        translation_y = H[1, 2]  # Translation in Y

        Y_error = np.around(H[0, 2], 3) # image X are axis Y
        X_error = np.around(H[1, 2],3)

        self.errors_list = np.append(self.errors_list, [[X_error ,Y_error]], axis=0)
       
        colX = self.errors_list[:, 0]
        colY = self.errors_list[:, 1]

        if len(self.errors_list) < 2:
            print(f"\nTranslation error in pixels X axis: {X_error}; Y axis: {Y_error}")
            return
        
        


        print(colX)
        print(colY)
        average_X_abs = np.mean(np.abs(colX))
        average_Y_abs = np.mean(np.abs(colY))
        std_X = np.std(colX)
        std_Y = np.std(colY)

        average_X_plus = np.mean(colX[colX > 0])
        average_X_minus  = np.mean(colX[colX < 0])

        average_Y_plus = np.mean(colY[colY > 0])
        average_Y_minus  = np.mean(colY[colY < 0])
        np.set_printoptions(precision=2)
        
        print(f"\nTranslation error in pixels X axis: {X_error} for this image")
        print(f"X abolute value average {average_X_abs} std {std_X}, negative average {average_X_minus}, positive {average_X_plus} ")
        print(f"\nTranslation error in pixels Y axis: {Y_error} for this image")
        print(f"Y abolute value average {average_Y_abs} std {std_Y},, negative average {average_Y_minus}, positive {average_Y_plus} ")

    
    def testing_loop(self):   

        if self.at_position() == False: #return if not at position
            return
     
        match self.loop_progress :

            case 'init':
                if self.pic_taken == False and self.pre_pic_timer < 100:        
                    self.pre_pic_timer += 1
                    return
                else:
                    self.camera.create_full_res_array()
                    self.camera.auto_exp_enable(False)
                    self.loop_progress = "save start array"
                    return
                
            case "save start array":

                if self.camera.full_image_array is not None:
                    self.start_image = self.camera.full_image_array.copy()
                    self.camera.full_image_array = None
                    self.loop_progress = "main loop"
                    return
            
            case "save current array":

                if self.camera.full_image_array is not None:
                    self.current_image = self.camera.full_image_array.copy()
                    self.camera.full_image_array = None
                    self.loop_progress = "process difference"
                    return

            case "process difference":
                self.process_difference()
                self.loop_progress = "main loop"
                return
            
            case "take image":

                ### pre image delay 10s
                if self.pic_taken == False and self.pre_pic_timer < 30:        
                    self.pre_pic_timer += 1
                    return
                
                self.camera.create_full_res_array()
                self.camera.auto_exp_enable(False)
                self.loop_progress = "save current array"
                self.pic_taken = True
                return
            
            case "main loop":

                if self.target_position == self.start:
                    self.camera.auto_exp_enable(False)
                    new_X = random.randrange(10000, 50000)
                    new_Y = random.randrange(10000, 50000)
                    new_F = self.start[2]
                    self.target_position = [new_X,new_Y,new_F]
                    self.microscope.go_absolute(self.target_position)

                else:
                    self.pic_taken = False
                    self.pre_pic_timer = 0
                    self.target_position = self.start
                    self.done_repeat += 1 
                    self.microscope.go_absolute(self.target_position)
                    self.loop_progress = "take image"

if __name__ == "__main__": 

    encoder_X, encoder_Y, encoder_F = controller_startup()                
    ### Object for microscope to run
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin, parameters)
    position_grid = PositionsGrid(microscope, parameters)
    micro_cam = Microscope_camera(microscope)
    
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
    
    Interface._main_menu = MainMenu(Tk_root, microscope=microscope, position_grid=position_grid, camera=micro_cam,  parameters=parameters)
    
    app = QApplication(sys.argv)
    preview_window = MainApp(micro_cam, microscope, export)

    #access neede to interact with preview when doing captures
    micro_cam.qpicamera = preview_window.main_widget.qpicamera2 

    # run the old Tk interace in a Qt timer
    timer = QtCore.QTimer()
    tester = Accuracy_tester(microscope=microscope, position_grid=position_grid, camera=micro_cam,  parameters=parameters)
    timer.timeout.connect(tester.execute_function)
    timer.start(10)

    sys.exit(app.exec_())

    #GPIO cleanup
    GPIO.cleanup()
