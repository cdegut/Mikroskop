# import the necessary packages
import time
from smbus2 import SMBus, i2c_msg
import RPi.GPIO as GPIO
from .microscope_param import *
from .parametersIO import load_parameters

# Use GPIO numbers not pin numbers
GPIO.setmode(GPIO.BCM)

class Microscope:

    def __init__(self, addr, ready_pin):
        self.addr = addr
        self.ready_pin = ready_pin
        GPIO.setup(ready_pin, GPIO.IN) # set up the GPIO channels - one input for ready pin
        self.wait_ready()
        self.positions = self.checked_read_positions()
        endstops_dict = load_parameters()["dyn_endstops"]
        self.set_dynamic_endsotop(endstops_dict)

        #Dynamic endsotop these will be used to modify the movement according to etablished safe parameters
    def set_dynamic_endsotop(self, endstops_dict):
        self.dynamic_endstops = True
        self.dyn_Xmax = endstops_dict["dyn_Xmax"]
        self.dyn_Xmin = endstops_dict["dyn_Xmin"]
        self.dyn_Ymax = endstops_dict["dyn_Ymax"]
        self.dyn_Ymin = endstops_dict["dyn_Ymin"]
        self.dyn_maxFcs = endstops_dict["dyn_maxFcs"]
        self.safe_Fcs = endstops_dict["safe_Fcs"]
      

    def wait_ready(self): # wait until arduino is ready
        while not GPIO.input(self.ready_pin):  
            time.sleep(0.1)
    
    def is_ready(self): #check if arduino is ready
        return GPIO.input(self.ready_pin) 

    def send_motor_cmd(self, motor, destination):

        if self.is_ready: #nothing is done if arduino is not available
            destination_as_bytes = int(destination).to_bytes(4, byteorder='big', signed=False)
			
            checksum = (sum(destination_as_bytes)+motor) % 256 #compute simple checksum
            destination_as_bytes += bytes([checksum]) #add checksum byte to the destination bytes liste
			
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

    def checked_send_motor_cmd(self, motor, destination): 
	#use the software endstop if set
	#send command (including checksum)
	#wait for movement to be done
	#read position from arduino and check that movement was executed corectly
	#retry the movement if the position is not the expected one (with checksum added, this should never happen)
               
        destination = self.make_safe(motor, destination) #update destination with max value acccording to set soft endstop if needed

        if motor not in [1,2,3]: #simple check that motor havn't an abherant index
            return

        i = 1
        while i <= retry:
            if self.is_ready: #nothing is done if arduino is not available

                self.send_motor_cmd(motor, destination)
                self.wait_ready()

                #update position and check that it was corectly done
                self.positions = self.checked_read_positions()
                if self.positions[motor-1] == destination:
                    self.wait_ready()
                    return

            #Loop if the function was not returned after the check position (with checksum added to I²C communication, this should never happen)
            #May happen if axis maxrange are > to endstop set in arduino firmware
            print("At "+ time.strftime("%H:%M:%S", time.localtime()) +" motor did not move as expected, retrying "+str(i)+" of "+ str(retry) +" times") 
            time.sleep(0.5)
            i += 1

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

            if self.positions[2] >= self.safe_Fcs: ### Stop movement if the objective is to close to unsafe borders
                
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
             
            if motor == 3 and destination > self.safe_Fcs and (self.positions[0] < self.dyn_Xmin or self.positions[0] > self.dyn_Xmax or 
                                                            self.positions[1] >  self.dyn_Ymax or self.positions[1] < self.dyn_Ymin ):
                destination = self.safe_Fcs
            


        return destination

    def move_1axis(self, axis, movement): # for small axis movement 
	#convert a movement into a destination          
        motor_position = self.positions[axis-1]
        motor_destination = motor_position + movement
        if motor_destination < 0:
            return
        self.checked_send_motor_cmd(axis, motor_destination)           
        self.wait_ready()
        
    def go_absolute(self, destinations): #ordered movement of the 3 axis, move focus first of last depending on condition to avoid triggering dyn_endstop
        if destinations[2] < self.positions[2]: #move focus first if it's going down (park)
            self.checked_send_motor_cmd(3, destinations[2])
            self.wait_ready()    
            self.checked_send_motor_cmd(1, destinations[0])
            self.wait_ready()
            self.checked_send_motor_cmd(2, destinations[1])
            self.wait_ready()       
        else: #move focus last if it's going up (start)
            self.checked_send_motor_cmd(1, destinations[0])
            self.wait_ready()
            self.checked_send_motor_cmd(2, destinations[1])
            self.wait_ready()
            self.checked_send_motor_cmd(3, destinations[2])
            self.wait_ready()
   
    def set_ledpwr(self, pwr):
        if self.is_ready: #nothing is done if arduino is not available
            with SMBus(1) as bus:
                bus.write_i2c_block_data(addr, 4, [ 4 , pwr])

    def send_simplecmd(self, cmd):
        if self.is_ready: #nothing is done if arduino is not available
            with SMBus(1) as bus:
                bus.write_byte_data(addr, cmd, cmd) #command need to be sent twice to be executed (crude error check)
    
    def set_led_state(self, state):
        if state not in [0,1,2,3]:
            return
        
        if state == 0:
            self.send_simplecmd(8)
            self.positions[4] = 0
        elif state == 1:
            self.send_simplecmd(5)
            self.positions[4] = 1
        elif state == 2:
            self.send_simplecmd(6)
            self.positions[4] = 2
        elif state == 3:
            self.send_simplecmd(7)
            self.positions[4] = 3
         
    def read_positions(self): #get position from the microscope

        if self.is_ready: #nothing is done if arduino is not available
            i=1
            while i <= retry: #do the comunication, but catch error and retry in case of problem
           
                try:  # Read 15 bytes (last is checksum)
                    with SMBus(1) as bus:
                        msg = i2c_msg.read(self.addr, 15) #generate I²C msg instance as msg
                        bus.i2c_rdwr(msg)	#I²C transaction

                except:
                    time.sleep(1)
                    i += 1
                    print("At "+ time.strftime("%H:%M:%S", time.localtime()) +" read position: comunication error, retrying "+str(i)+" of "+ str(retry) +" times")
                    
                else:
                    break

            #parse the 14 bytes into 3*4 +2 bytes values (there is probably a better way to do it)
            X_b = []
            Y_b = []
            Focus_b = []
            i = 1

            for value in msg: #I²C msg instance can be iterated to get the byte one by one
                if i <= 4:
                    X_b.append(value)
            
                if 5 <= i <= 8:
                    Y_b.append(value) 

                if 9 <= i <= 12:
                    Focus_b.append(value) 

                if i == 13:
                    led_b = value
                if i == 14:
                    led_state_b = value
                if i == 15:
                    received_checksum = value
                i = i+1

            checksum = (sum(X_b) + sum(Y_b) + sum(Focus_b) + led_b + led_state_b) %256 #checksum on arduino side is an overflown byte, need to take modulo 256 to reproduce behaviour
            
            if checksum != received_checksum:
                return None
            
			#generate integer from the list of bytess.
			
            X_pos = int.from_bytes(X_b, byteorder='little', signed=False)
            Y_pos = int.from_bytes(Y_b, byteorder='little', signed=False)
            Focus_pos = int.from_bytes(Focus_b, byteorder='little', signed=False)
			
            positions = [X_pos, Y_pos, Focus_pos, led_b, led_state_b]
            return positions

    def checked_read_positions(self): #return position if read_postiions() is not none (=checksum match) or exit after 10 retry
        i=1
        while i <= read_retry:
            positions = self.read_positions()
            if positions is not None:
                return positions
            
            time.sleep(0.5)
            i += 1
        print("Unable to read position after " +str(read_retry)+ " attempents" )
        exit()
