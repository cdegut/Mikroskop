from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel
import time
import os
import random
import numpy as np
import cv2
import pandas as pd
from modules.controllers import *
import time

repeat_before_tune = 50
divider = 2 #convergence speed lower = faster
pixel_size = 0.56
um_per_steps = 1.25
autotune_source = "variability"

def multiscale_ecc_alignment(image1, image2, num_scales=3):
    # Create a list to store downscaled versions of the images
    image1_pyramid = [image1]
    image2_pyramid = [image2]
    
    for i in range(1, num_scales):
        image1_pyramid.append(cv2.pyrDown(image1_pyramid[i-1]))
        image2_pyramid.append(cv2.pyrDown(image2_pyramid[i-1]))
    
    # Start with the smallest scale
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    for scale in range(num_scales-1, -1, -1):
        # Resize images back to original scale
        scaled_image1 = image1_pyramid[scale]
        scaled_image2 = image2_pyramid[scale]
        
        # Run ECC algorithm at the current scale
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 1000, 1e-5)
        (cc, warp_matrix) = cv2.findTransformECC(scaled_image1, scaled_image2, warp_matrix, cv2.MOTION_TRANSLATION, criteria)
        
        # Scale the warp matrix to the next level if not at the last scale
        if scale != 0:
            warp_matrix[0, 2] *= 2
            warp_matrix[1, 2] *= 2
    
    return warp_matrix

def orb_alignment(image1, image2):    
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(image1, None)
    kp2, des2 = orb.detectAndCompute(image2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda   x: x.distance)

    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    matrix, mask = cv2.estimateAffine2D(src_pts,  dst_pts)

    return matrix


class AccuracyTester():
    def __init__(self, microscope: MicroscopeManager, position_grid: PositionsGrid, camera: Microscope_camera,  parameters: GridParameters, infobox: QLabel):
        self.microscope: MicroscopeManager = microscope
        self.position_grid: PositionsGrid = position_grid
        self.camera: Microscope_camera = camera
        self.parameters: GridParameters = parameters
        self.infobox = infobox

        self.timer = QtCore.QTimer()
        self.camera.switch_mode(self.camera.full_res_config, signal_function=self.camera.qpicamera.signal_done)

        #Tester
        self.done_repeat = 0

        self.distance_X =  0
        self.distance_Y =  0
        self.last_X_error = None
        self.last_Y_error = None

        self.start_image = None
        self.current_image = None
        self.last_image = None

        self.overshoot_X = 0
        self.undershoot_X = 0
        self.overshoot_Y = 0
        self.undershoot_Y = 0

        self.start = self.microscope.XYFposition
        self.target_position = self.start


        if self.microscope.led1pwr == 0:
            self.microscope.request_ledspwr(50,0)

    def initiate_files(self, f_name):
        current_time = time.localtime()        
        date = str(current_time[0])[2:] + str(current_time[1]).zfill(2) + str(current_time[2]).zfill(2) + "_"  \
            + str(current_time[3]).zfill(2) + str(current_time[4]).zfill(2)
        data_dir = self.parameters.get()["data_dir"]      
        home = os.getenv("HOME")

        self.test_data_folder = f"{home}/{data_dir}/accuracy_tests/{f_name}-{date}/"
        create_folder(self.test_data_folder)


        open(f"{self.test_data_folder}/data.txt", "x")
        with open(f"{self.test_data_folder}/data.txt", "a") as data_file:
            data_file.write("Repeat\tX error(first image)\tX variability(last image)\tX distance\tY error(first image)\tY variability(last image)\tY distance\n")
        
        open(f"{self.test_data_folder}/autotune.txt", "x")
        with open(f"{self.test_data_folder}/autotune.txt", "a") as data_file:
            data_file.write("Repeat\tX overshoot\tX undershoot\tX std error\tX std variability\tY overshoot\tY undershoot\tY std error\tY std variability\n")

    
    def get_X_Y_error(self,array1,array2):
        image1 = cv2.cvtColor(array1, cv2.COLOR_BGR2GRAY)
        image2 = cv2.cvtColor(array2, cv2.COLOR_BGR2GRAY)

        # Align images using multiscale ECC
        #warp_matrix = multiscale_ecc_alignment(image1, image2)
        warp_matrix = orb_alignment(image1, image2)

        # Apply the warp transformation
        aligned_image2 = cv2.warpAffine(image2, warp_matrix, (image1.shape[1], image1.shape[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
       
        # (Optional) Align image2 using the homography matrix and display
        aligned_image2 = cv2.warpAffine(image2, warp_matrix, (image1.shape[1], image1.shape[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        difference = cv2.absdiff(image1, aligned_image2)
        scale_factor = 0.1
        difference_resized = cv2.resize(difference, (0, 0), fx=scale_factor, fy=scale_factor)
        cv2.imwrite(f"{self.test_data_folder}/{self.done_repeat}.jpg", difference_resized)

        Y_error = warp_matrix[0, 2]
        X_error = warp_matrix[1, 2]
        return round(X_error,1), round(Y_error,1)

    def process_difference(self):
        X_error, Y_error = self.get_X_Y_error(self.start_image, self.current_image)
        if not self.last_X_error:
            X_drift = X_error
            Y_drift = Y_error
        else:
            X_drift =  X_error - self.last_X_error
            Y_drift = Y_error - self.last_Y_error 

        data = f"{self.done_repeat}\t{X_error}\t{X_drift}\t{self.distance_X}\t{Y_error}\t{Y_drift}\t{self.distance_Y}\n"

        
        with open(f"{self.test_data_folder}/data.txt", "a") as data_file:
            data_file.write(data)

        
        print(f"\nRepeat n {self.done_repeat}")
        print(f"Translation error in pixels X axis: {X_error:.2f} for this image, and drift {X_drift:.2f} from last image")
        print(f"Translation error in pixels Y axis: {Y_error:.2f} for this image and drift {Y_drift:.2f} from last image")

        self.last_X_error = X_error
        self.last_Y_error = Y_error
        self.infobox.setText(f"Repeat n {self.done_repeat}\nImage to image drift:\nX = {X_drift:.2f}px\nY = {Y_drift:.2f}px")

    def self_tune(self):


        data = pd.read_csv(f"{self.test_data_folder}/data.txt", sep='\t')
        df_sliced = data.loc[self.done_repeat - repeat_before_tune: self.done_repeat]
        if autotune_source == "variability":
            median_X_positive = df_sliced[df_sliced['X distance'] > 0]['X variability(last image)'].median() * pixel_size /um_per_steps
            median_X_negative = df_sliced[df_sliced['X distance'] < 0]['X variability(last image)'].median() * pixel_size /um_per_steps
            median_Y_positive = df_sliced[df_sliced['Y distance'] > 0]['Y variability(last image)'].median() * pixel_size /um_per_steps
            median_Y_negative = df_sliced[df_sliced['Y distance'] < 0]['Y variability(last image)'].median() * pixel_size /um_per_steps       
        else:
            median_X_positive = df_sliced[df_sliced['X distance'] > 0]['X error(first image)'].median() * pixel_size /um_per_steps
            median_X_negative = df_sliced[df_sliced['X distance'] < 0]['X error(first image)'].median() * pixel_size /um_per_steps
            median_Y_positive = df_sliced[df_sliced['Y distance'] > 0]['Y error(first image)'].median() * pixel_size /um_per_steps
            median_Y_negative = df_sliced[df_sliced['Y distance'] < 0]['Y error(first image)'].median() * pixel_size /um_per_steps


        std_error_X = df_sliced['X error(first image)'].std()
        std_variability_X = df_sliced['X variability(last image)'].std()
        std_error_Y = df_sliced['Y error(first image)'].std()
        std_variability_Y = df_sliced['Y variability(last image)'].std()
        data = f"{self.done_repeat}\t{self.overshoot_X}\t{self.undershoot_X}\t{std_error_X}\t{std_variability_X }\t" + \
        f"{self.overshoot_Y}\t{self.undershoot_Y}\t{std_error_Y}\t{std_variability_Y }\n"

        print(f"Medians of errors in steps X+ {median_X_positive:.2f}, X- {median_X_negative:.2f}, Y+ {median_Y_positive:.2f}, Y- {median_Y_negative:.2f},")
        self.overshoot_X = self.overshoot_X + int(median_X_positive /divider)
        self.undershoot_X = self.undershoot_X + int(median_X_negative /divider)
        self.overshoot_Y = self.overshoot_Y + int(median_Y_positive /divider)
        self.undershoot_Y = self.undershoot_Y + int(median_Y_negative /divider)

        self.microscope.config_trajectory_corection(self.overshoot_X,self.undershoot_X,self.overshoot_Y,self.undershoot_Y)

        with open(f"{self.test_data_folder}/autotune.txt", "a") as data_file:
            data_file.write(data)

        dataframe: pd.DataFrame = pd.read_csv(f"{self.test_data_folder}/autotune.txt", sep='\t')
        if dataframe.shape[0] < 2:
            return
       
        if autotune_source == "variability":
            lowest_row_X =dataframe.loc[dataframe.iloc[:, 4].idxmin()]
            lowest_row_Y =dataframe.loc[dataframe.iloc[:, 8].idxmin()]
        else:
            lowest_row_X =dataframe.loc[dataframe.iloc[:, 3].idxmin()]
            lowest_row_Y =dataframe.loc[dataframe.iloc[:, 7].idxmin()]

        microscope_parameters = MicroscopeParameters()
        microscope_parameters.load()
        microscope_parameters.overshoot_X = lowest_row_X["X overshoot"]
        microscope_parameters.undershoot_X = lowest_row_X["X undershoot"]
        microscope_parameters.overshoot_Y = lowest_row_Y["Y overshoot"]
        microscope_parameters.undershoot_Y = lowest_row_Y["Y undershoot"] 
        microscope_parameters.save()

 
###################
###Testing loop ####

    def start_testing(self, mode:str, wiggle = False):
        self.__timer = 0
        self.__mode: str =  mode
        self.done_repeat = 0
        if wiggle:
            self.timer.timeout.connect(self.__wiggle)
        else:
            self.timer.timeout.connect(self.__get_start_image)
        self.timer.start(100)
        self.start = self.microscope.XYFposition
        self.__wiggle_count = 0
    
    def __wiggle(self):
        if self.microscope.at_position == False: #return if not at position
            return
        x = self.start[0]
        y = self.start[1]
        f = self.start[2]
        
        if self.__wiggle_count == 0:
            self.microscope.request_XYF_travel([x+100, y+100, f])
            self.microscope.run()
            self.__wiggle_count += 1
            return
        
        if self.__wiggle_count == 1:
            self.microscope.request_XYF_travel([x-100, y-100, f])
            self.microscope.run()
            self.__wiggle_count += 1
            return
        
        if self.__wiggle_count == 2:
            self.microscope.request_XYF_travel([x+100, y+100, f])
            self.microscope.run()
            self.__wiggle_count += 1
            return

        if self.__wiggle_count == 3:
            self.microscope.request_XYF_travel([x-200, y-200, f])
            self.microscope.run()
            self.__wiggle_count += 1
            return

        if self.__wiggle_count == 4:
            self.microscope.request_XYF_travel([x+200, y+200, f])
            self.microscope.run()
            self.__wiggle_count += 1
            return
        

        self.microscope.request_XYF_travel([x, y, f])
        self.microscope.run()
        self.timer.timeout.disconnect()
        self.timer.timeout.connect(self.__get_start_image)

        
    def __get_start_image(self):     
        if self.microscope.at_position == False: #return if not at position
            return

        if self.__timer < 20:
            self.__timer += 1
            return
        
        self.timer.timeout.disconnect()
        print("getting start image")
        self.camera.create_main_array()
        self.camera.auto_exp_enable(False)
        self.timer.timeout.connect(self.__record_start_image)
        self.__timer =0

    def __record_start_image(self):    
        if self.camera.full_image_array is not None:
            self.timer.timeout.disconnect()
            self.start_image: np.ndarray = self.camera.full_image_array.copy()
            self.last_image: np.ndarray = self.camera.full_image_array.copy()
            self.camera.full_image_array = None
            self.__mode_switch()
    
    def __mode_switch(self):
        if self.__mode == "static":
            self.timer.timeout.connect(self.__long_delay)
        
        if self.__mode == "accuracy test":
            self.__go_random()

        if self.__mode == "accuracy autotune":
            if self.done_repeat != 0 and self.done_repeat%repeat_before_tune == 0:
                self.self_tune()
            self.__go_random()

    def __long_delay(self):
        if self.__timer < 3000:
            self.__timer += 1
            return
        self.timer.timeout.disconnect()
        self.__timer = 0
        self.timer.timeout.connect(self.__next_image)
    
    def __go_random(self):

        new_X = random.randrange(5000, 60000)
        new_Y = random.randrange(5000, 80000)
        new_F = self.start[2]
        self.distance_X =  new_X - self.start[0]
        self.distance_Y =  new_Y - self.start[1]
        self.target_position = [new_X,new_Y,new_F]
        self.microscope.request_XYF_travel(self.target_position)
        self.timer.timeout.connect(self.__go_back)
    
    def __go_back(self):
        if self.microscope.at_position == False: #return if not at position
            return
        
        self.timer.timeout.disconnect()
        self.microscope.request_XYF_travel(position=self.start, trajectory_corection = True)      
        self.timer.timeout.connect(self.__next_image)

    def __next_image(self):
        if self.microscope.at_position == False: #return if not at position
            return

        if self.__timer < 20:        
            self.__timer  += 1
            return
        
        self.timer.timeout.disconnect()
        self.camera.create_main_array()
        self.timer.timeout.connect(self.__process_new)
        self.__timer = 0
    
    def __process_new(self):

        if self.camera.full_image_array is not None:
            self.timer.timeout.disconnect()
            self.current_image = self.camera.full_image_array.copy()
            self.camera.full_image_array = None
            self.process_difference()
            self.done_repeat += 1
            self.__mode_switch()
        