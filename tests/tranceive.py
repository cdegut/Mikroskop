from smbus2 import SMBus, i2c_msg
import RPi.GPIO as GPIO
import time

# Use GPIO numbers not pin numbers
GPIO.setmode(GPIO.BCM)
# set up the GPIO channels - one input and one output
GPIO.setup(4, GPIO.IN)

# bus address
addr = 0x8 

#usefull var to init
cmd = 0
x_position, y_position, f_position = 0,0,0

def send_destination(motor, destination):
    if motor in [1,2,3]:
        destination_as_bytes = (destination).to_bytes(4, byteorder='big', signed=False)
        checksum = (sum(destination_as_bytes)+motor) % 256 #compute simple checksum
        destination_as_bytes += bytes([checksum])

        with SMBus(1) as bus:
            bus.write_i2c_block_data(addr, motor, destination_as_bytes)

def set_ledpwr(led1pwr, led2pwr):
    with SMBus(1) as bus:
        checksum = (led1pwr + led2pwr) % 256 
        bus.write_i2c_block_data(addr, 4, [ 4 , led1pwr, led2pwr,checksum])

def neoPixel_solid_color(R,G,B):
        checksum = (R + G +B ) % 256 
        with SMBus(1) as bus:
            bus.write_i2c_block_data(addr, 5, [ 5 , R, G, B, checksum])

def neoPixel_indexLed(index, R,G,B):
        checksum = (index + R + G +B ) % 256 
        with SMBus(1) as bus:
            bus.write_i2c_block_data(addr, 6, [ 6 ,index, R, G, B, checksum])

def send_simplecmd(cmd):
    with SMBus(1) as bus:
        bus.write_byte_data(addr, cmd, cmd) #command is sent twice to be executed

def read_positions(): #get position from the microscope

    retry = 10
    i=1
    while i <= retry: #do the comunication, but catch error and retry in case of problem          
        try:  # Read 15 bytes (last is checksum)
            with SMBus(1) as bus:
                msg = bus.read_i2c_block_data(addr, 0, 15) #generate I²C msg instance as msg

        except:
            time.sleep(0.5)
            i += 1
            print("At "+ time.strftime("%H:%M:%S", time.localtime()) +" read position: comunication error, retrying "+str(i)+" of "+ str(retry) +" times")                   
        
        else:
            checksum = (sum(msg[:14])) %256 
            if checksum == msg[14]:
                break

            time.sleep(0.5)
            i += 1
            print("At "+ time.strftime("%H:%M:%S", time.localtime()) +" read position: Bad checksum, retrying "+str(i)+" of "+ str(retry) +" times")
        

    #generate integer from the list of bytess.
    
    X_pos = int.from_bytes(msg[:4], byteorder='little', signed=False)
    Y_pos = int.from_bytes(msg[4:8], byteorder='little', signed=False)
    Focus_pos = int.from_bytes(msg[8:12], byteorder='little', signed=False)		
    led1 = msg[12]
    led2 = msg[13]

    return [X_pos, Y_pos, Focus_pos, led1, led2]

while True:
    while not GPIO.input(4): # read position only if pin 4 is up = arduino is ready
        time.sleep(0.1)
    positions = read_positions()
    print(positions)

    
    print(" 1 : X (current : ", positions[0], ") \n 2 : Y (current : ", positions[1], ")\n 3 : F (current : ", positions[2], ")")   
    cmd_input = input("cmd:")
    if cmd_input != '':
        
        for i,a in enumerate(['x','y','f']):
            if cmd_input == a:
                cmd_input = i+1

        cmd = int(cmd_input)

        if cmd == 4:
            led1pwr_input = input("Led 1 power (0 - 100):")
            led2pwr_input = input("Led 2 power (0 - 100):")
            set_ledpwr(int(led1pwr_input),int(led2pwr_input))

        if cmd == 5:
            R = input("Red Value:")
            G = input("Green Value:")
            B = input("Blue Value:")
            neoPixel_solid_color(int(R),int(G),int(B))

        if cmd == 6:
            index = input("Led Index:")
            R = input("Red Value:")
            G = input("Green Value:")
            B = input("Blue Value:")
            neoPixel_indexLed(int(index),int(R),int(G),int(B))
        
        if cmd == 7:
            R = input("Red Value:")
            G = input("Green Value:")
            B = input("Blue Value:")
            for i in range(0,8):
                neoPixel_indexLed(int(i),int(R),int(G),int(B))

        if cmd == 8:
            R = input("Red Value:")
            G = input("Green Value:")
            B = input("Blue Value:")
            for i in range(8,16):
                neoPixel_indexLed(int(i),int(R),int(G),int(B))

        if cmd == 9:
            R = input("Red Value:")
            G = input("Green Value:")
            B = input("Blue Value:")
            for i in range(0,5):
                neoPixel_indexLed(int(i),int(R),int(G),int(B))
        
        if cmd in [1,2,3]:
            destination_input = input("destination in steps:")
            send_destination(int(cmd), int(destination_input))

        if cmd in [101, 102, 103, 255]:
            send_simplecmd(int(cmd))


