# import the necessary packages
import time
from smbus2 import SMBus, i2c_msg
import RPi.GPIO as GPIO
from .microscope_param import *

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
            
    #def safe_destination_update(self, motor, destination):
    #           
    #    destination = self.make_safe(motor, destination) #update destination with max value acccording to set soft endstop if needed      
        

    def move_single_axis(self, motor, destination):
        i = 1
        while i <= retry:

            destination = self.make_safe(motor, destination)
            self.send_motor_cmd(motor, destination)
            time.sleep(0.1)

            if not self.is_ready():
                return
            
            self.update_real_state()
            if self.XYFposition[motor-1] == destination:
                return

            print("At "+ time.strftime("%H:%M:%S", time.localtime()) +" motor did not move as expected, retrying "+str(i)+" of "+ str(retry) +" times") 
            time.sleep(0.5)
            i += 1

    def move_focus(self, destination):
        self.move_single_axis(3, destination)
    
    def move_X_Y(self, destination_X, destination_Y):

        self.move_single_axis(1,destination_X)
        self.move_single_axis(2,destination_Y)

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
        
    def go_absolute(self, destinations): #ordered movement of the 3 axis, move focus first of last depending on condition to avoid triggering dyn_endstop
        if destinations[2] < self.XYFposition[2]: #move focus first if it's going down (park)
            self.move_focus(destinations[2]) 
            self.move_X_Y(destinations[0],destinations[1])
        else: #move focus last if it's going up (start)
            self.move_X_Y(destinations[0],destinations[1])    
            self.move_focus(destinations[2])
   
    def set_ledspwr(self, led1pwr, led2pwr):
        with SMBus(1) as bus:
            checksum = (led1pwr + led2pwr) % 256 
            bus.write_i2c_block_data(addr, 4, [ 4 , led1pwr, led2pwr,checksum])

    def send_simplecmd(self, cmd):
        with SMBus(1) as bus:
            bus.write_byte_data(addr, cmd, cmd) #command need to be sent twice to be executed (crude error check)
         
    def read_positions(self): #get position from the microscope
        i=1
        while i <= retry: #do the comunication, but catch error and retry in case of problem          
            try:  # Read 15 bytes (last is checksum)
                with SMBus(1) as bus:
                    msg = bus.read_i2c_block_data(addr, 0, 15) #generate I²C msg instance as msg

            except:
                time.sleep(0.5)
                i += 1
                print("At "+ time.strftime("%H:%M:%S", time.localtime()) +" read position: comunication error, retrying "+str(i-1)+" of "+ str(retry) +" times")                   
            
            else:
                break

            checksum = (sum(msg[:14])) %256 
            if checksum != msg[14]:
                return None
            
        #generate integer from the list of bytess.
        
        X_pos = int.from_bytes(msg[:4], byteorder='little', signed=False)
        Y_pos = int.from_bytes(msg[4:8], byteorder='little', signed=False)
        Focus_pos = int.from_bytes(msg[8:12], byteorder='little', signed=False)		
        led1 = msg[12]
        led2 = msg[13]

        positions = [X_pos, Y_pos, Focus_pos, led1, led2]
        return positions

    def update_real_state(self): #return position if read_postiions() is not none (=checksum match) or exit after 10 retry
        i=1
        while i <= read_retry:
            positions = self.read_positions()
            if positions is not None:
                self.XYFposition = positions[:3]
                self.led1pwr = positions[3]
                self.led2pwr = positions[4]
                return
        
            time.sleep(0.1)
            i += 1
        print("Unable to read position after " +str(read_retry)+ " attempents" )
        exit()
