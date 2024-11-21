# import the necessary packages
import time
from typing import Self
from attr import dataclass
from smbus2 import SMBus, i2c_msg
import RPi.GPIO as GPIO
from .microscope_param import *
from .parametersIO import ParametersSets
from PyQt5 import QtCore
from dataclasses import dataclass

# Use GPIO numbers not pin numbers
GPIO.setmode(GPIO.BCM)


class Microscope:

    def __init__(self, addr, ready_pin, parameters=None):
        self.addr = addr
        self.ready_pin = ready_pin
        GPIO.setup(ready_pin, GPIO.IN) # set up the GPIO channels - one input for ready pin
        self.wait_ready()
        self.XYFposition = [0,0,0]
        self.led1pwr = 0
        self.led2pwr = 0
        self.runing = False
        self.update_real_state()
        
        if parameters: ## if no parameter set are given, dynamic endstop are disabled
            endstops_dict = parameters.get()["dyn_endstops"]
        else:
            endstops_dict = None

        self.set_dynamic_endsotop(endstops_dict)

        #Dynamic endsotop these will be used to modify the movement according to established safe parameters
    def set_dynamic_endsotop(self, endstops_dict):
        if endstops_dict:
            self.dynamic_endstops = True
            self.dyn_Xmax = endstops_dict["dyn_Xmax"]
            self.dyn_Xmin = endstops_dict["dyn_Xmin"]
            self.dyn_Ymax = endstops_dict["dyn_Ymax"]
            self.dyn_Ymin = endstops_dict["dyn_Ymin"]
            self.dyn_maxFcs = endstops_dict["dyn_maxFcs"]
            self.safe_Fcs = endstops_dict["safe_Fcs"]
        else:
            self.dynamic_endstops = False    

    def wait_ready(self): # wait until arduino is ready
        while not GPIO.input(self.ready_pin):  
            time.sleep(0.1)
    
    def is_ready(self): #check if arduino is ready
        return GPIO.input(self.ready_pin) 

    def send_motor_cmd(self, motor, destination):

        #Generate the message
        destination_as_bytes = int(destination).to_bytes(4, byteorder='big', signed=False)        
        checksum = (sum(destination_as_bytes)+motor) % 256
        destination_as_bytes += bytes([checksum])
                
        i=0
        while i <= retry: #do the comunication, but catch error and retry in case of problem
            try:
                with SMBus(1) as bus: #open I²C bus, and do the proper comunication
                    bus.write_i2c_block_data(self.addr, motor, destination_as_bytes)
            except:
                time.sleep(1)
                i=i+1
                print("At "+ time.strftime("%H:%M:%S", time.localtime()) +" motor comunication error, retrying "+str(i)+" of "+ str(retry) +" times")
            else:
                break

        if i > retry:
                print("At "+ time.strftime("%H:%M:%S", time.localtime()) + "motor comunication error, exit after "+str(i)+"retry")
                exit()

    def push_axis(self, motor, amount):
        with SMBus(1) as bus: #open I²C bus, and do the proper comunication
            #bus.write_i2c_block_data(self.addr, motor + 10, 100)
            #bus.write_byte_data(self.addr, motor + 0x10, amount)

            steps = abs(amount)
            if amount > 0:
                cmd =  motor + 0x10
            else:
                cmd =  motor + 0x20
            if steps > 255:
                steps = 255
            data = bytes([steps, steps])
            bus.write_i2c_block_data(self.addr, cmd, data)

    def move_single_axis(self, motor, destination):
        i = 1
        while i <= retry:

            destination = self.make_safe(motor, destination)

            if not self.is_ready():
                return False

            if self.XYFposition[motor-1] == destination:
                return True
            
            self.send_motor_cmd(motor, destination)
            return True

    def move_focus(self, destination):
        F_done =self.move_single_axis(3, destination)
        return F_done
    
    def move_X_Y(self, destination_X, destination_Y):

        X_done = self.move_single_axis(1,destination_X)
        Y_done = self.move_single_axis(2,destination_Y)
        return X_done , Y_done

    def make_safe(self, motor, destination): #Software and dynamic endstops, update destination to avoid collision or out of range

        if software_endstops:
            if motor == 1 and destination > Xmaxrange:
                destination = Xmaxrange            
            if motor == 2 and destination > Ymaxrange:
                destination = Ymaxrange
            if motor == 3 and destination > Fmaxrange:
                destination = Fmaxrange   

        #Dynamic endstops should be used to delimite a safe area coresponding to the observation window
        if self.dynamic_endstops:

            if self.XYFposition[2] >= self.safe_Fcs: ### Stop movement if the objective is to close to unsafe borders
                
                if motor == 1 and destination < self.dyn_Xmin:
                    destination = self.dyn_Xmin
                if motor == 1 and destination >  self.dyn_Xmax:
                    destination = self.dyn_Xmax
                
                if motor == 2 and destination <  self.dyn_Ymin:
                    destination = self.dyn_Ymin
                if motor == 2 and destination >  self.dyn_Ymax:
                    destination = self.dyn_Ymax
            
            if motor == 3 and destination > self.dyn_maxFcs:
                destination = self.dyn_maxFcs   
             
            if motor == 3 and destination > self.safe_Fcs and (self.XYFposition[0] < self.dyn_Xmin or self.XYFposition[0] > self.dyn_Xmax or 
                                                            self.XYFposition[1] >  self.dyn_Ymax or self.XYFposition[1] < self.dyn_Ymin ):
                destination = self.safe_Fcs
            
        return destination

    def move_1axis(self, axis, movement): # for small axis movement 
	#convert a movement into a destination          
        motor_position = self.XYFposition[axis-1]
        motor_destination = motor_position + movement
        if motor_destination < 0:
            return
        self.move_single_axis(axis, motor_destination)           
        
    def go_absolute(self, destinations: list[int,int,int]): #ordered movement of the 3 axis, move focus first of last depending on condition to avoid triggering dyn_endstop
        if destinations[2] < self.XYFposition[2]: #move focus first if it's going down (park)
            F_done = self.move_focus(destinations[2]) 
            X_done , Y_done =self.move_X_Y(destinations[0],destinations[1])
        else: #move focus last if it's going up (start)
            X_done , Y_done = self.move_X_Y(destinations[0],destinations[1])    
            F_done = self.move_focus(destinations[2])

        return all([F_done, X_done , Y_done])  # return false if any is false
   
    def set_ledspwr(self, led1pwr, led2pwr):
        with SMBus(1) as bus:
            checksum = (led1pwr + led2pwr) % 256 
            bus.write_i2c_block_data(addr, 4, [ 4 , led1pwr, led2pwr,checksum])
            self.led1pwr = led1pwr
            self.led2pwr = led2pwr

    def send_simplecmd(self, cmd):
        with SMBus(1) as bus:
            bus.write_byte_data(addr, cmd, cmd) #command need to be sent twice to be executed (crude error check)
         
    def read_positions(self): #get position from the microscope   
        try:  # Read 15 bytes (last is checksum)
            with SMBus(1) as bus:
                msg = bus.read_i2c_block_data(addr, 0, 15) #generate I²C msg instance as msg
                
        except:
            time.sleep(0.5)
            print("At "+ time.strftime("%H:%M:%S", time.localtime()) +" read position: comunication error")                   
            return False
        
        checksum = (sum(msg[:14])) %256 
        if checksum != msg[14]:
            return False
        
        #generate integer from the list of bytess.
        
        X_pos = int.from_bytes(msg[:4], byteorder='little', signed=False)
        Y_pos = int.from_bytes(msg[4:8], byteorder='little', signed=False)
        Focus_pos = int.from_bytes(msg[8:12], byteorder='little', signed=False)		
        led1 = msg[12]
        led2 = msg[13]

        positions = [X_pos, Y_pos, Focus_pos, led1, led2]
        return positions

    def update_real_state(self): #return position if read_postiions() is not none (=checksum match) or exit after 10 retry
        positions = self.read_positions()
        if positions:
            self.XYFposition = positions[:3]
            self.led1pwr = positions[3]
            self.led2pwr = positions[4]
            return True
        else:
            return False
    
    def adressable_LED_solid_color(self, R,G,B):
            checksum = (R + G +B ) % 256 
            with SMBus(1) as bus:
                bus.write_i2c_block_data(addr, 5, [ 5 , R, G, B, checksum])

    def adressable_LED_indexLed(self, index, R,G,B):

        checksum = (index + R + G +B ) % 256 
        with SMBus(1) as bus:
            bus.write_i2c_block_data(addr, 6, [ 6 ,index, R, G, B, checksum])


@dataclass
class LED:
    index: int = 0 
    R: int = 0
    G: int = 0
    B: int = 0

class LEDArray:
    def __init__(self, R=0,G=0,B=0, num = 16):
        self.leds = [LED(i, R,G,B) for i in range(num)]
    def half(self,R,G,B, start: int=0):
        for led in self.leds[start:start + int(len(self.leds)/2)]:
            led.R , led.G , led.B = R,G,B
    def quarter(self,R,G,B, start:int =0):
        for led in self.leds[start:start + int(len(self.leds)/4)]:
            led.R , led.G , led.B = R,G,B


class MicroscopeManager:

    """Create the manager instead of creating the Microscope class
        Use request method to set up next movement
        data will be sent at the next run()
    """  
    def __init__(self, addr, ready_pin, parameters: ParametersSets =None):
        self.__microscope: Microscope = Microscope(addr, ready_pin, parameters)
        self.__microscope.update_real_state()
        self.__active_target: list[int,int,int] = self.__microscope.XYFposition
        self.__requested_target: list[int,int,int] = self.__microscope.XYFposition
        self.__request_leds_pwr: list[int,int] = [self.__microscope.led1pwr,self.__microscope.led2pwr]
        self.__led_array: LEDArray = None

        self.at_position:bool = True
        self.XYFposition = self.__microscope.XYFposition
        self.led1pwr: int = self.__microscope.led1pwr
        self.led2pwr: int = self.__microscope.led2pwr

        self.micromanager_timer = QtCore.QTimer()
        self.micromanager_timer.timeout.connect(self.run)
        self.micromanager_timer.start(50)
    
    def run(self):
        """run the management task,
        get the microscope to update its position info
        send new position target
        set leds powers
        """
        self.__microscope.update_real_state()
        self.XYFposition = self.__microscope.XYFposition
        self.led1pwr = self.__microscope.led1pwr
        self.led2pwr = self.__microscope.led2pwr
        
        if self.__microscope.XYFposition == self.__active_target:
            self.at_position = True

        if self.__requested_target != self.__active_target:
            self.__activate_target()
     
        if self.__request_leds_pwr != [self.led1pwr, self.led2pwr]:
            self.__set_led_pwr()
        
        if self.__led_array is not None:
            self.__set_led_array()
        

    def __activate_target(self):
        request_accepeted = self.__microscope.go_absolute(self.__requested_target)
        if request_accepeted:
            self.__active_target = self.__requested_target
    
    def __set_led_pwr(self):
        self.__microscope.set_ledspwr(self.__request_leds_pwr[0], self.__request_leds_pwr[1])
    
    def __set_led_array(self):
        for led in self.__led_array.leds:
            self.__microscope.adressable_LED_indexLed(int(led.index),int(led.R),int(led.G),int(led.B))
        self.__led_array = None

    def request_led_array(self, led_array: LEDArray):
        """send led array request to the microscope

        Args:
            led_array (LEDArray): an array of LED in RGB format
        """
        self.__led_array: LEDArray = led_array
        

    def request_push_axis(self, axis: str, amount: int):
        """Push axis by a specific amount in steps
            will be sent to the microscope at the next exection of run()

        Args:
            axis (str): X , Y or F
            amount (int): amount of steps
        """
        aX = self.__requested_target[0]
        aY = self.__requested_target[1]
        aF = self.__requested_target[2]
        if axis == "X":
            self.__requested_target =  [aX + amount, aY, aF]

        if axis == "Y":
            self.__requested_target =  [aX , aY + amount, aF]

        if axis == "F":
            self.__requested_target =  [aX , aY , aF + amount]
        
        
    def request_XYF_travel(self, position: list[int,int,int], trajectory_corection: bool = False):
        """request a full destination in XYF
            will be sent to the microscope at the next exection of run()

        Args:
            position (list[int,int,int]): [DestinationX, Y, F] -1 to any axis keep it in current position
            trajectory_corection: bool = True change the destination to account to microscope error

        """

        if position[0] < 0:
            position[0] = self.XYFposition[0]
        if position[1] < 0:
            position[1] = self.XYFposition[1]
        if position[2] < 0:
            position[2] = self.XYFposition[2]

        if trajectory_corection:
            position = self.__corect_trajectory(position)

        self.__requested_target = position

    def request_ledspwr(self, led1pwr: int, led2pwr:int):
        """request a leds power 0 to 100%
            will be sent to the microscope at the next exection of run()
        Args:
            led1pwr (int): leds 1 power 0 to 100%
            led2pwr (int): leds 2 power 0 to 100%
        """
      
        self.__request_leds_pwr = [led1pwr, led2pwr]

    
    def __corect_trajectory(self, position):
        cX = self.XYFposition[0] # current
        cY = self.XYFposition[1]
        cF = self.XYFposition[2]

        tX = position[0] # request
        tY = position[1]
        tF = position[2]

        if cX - tX > 0:   
            tX = tX + overshoot_X  # target
        elif cX - tX < 0:
            tX = tX + undershoot_X  # target

        if cY - tY > 0:
            tY = tY + overshoot_Y  # target
        elif cY - tY < 0:
            tY = tY + undershoot_Y  # target
        
        return [tX, tY, tF]


    
