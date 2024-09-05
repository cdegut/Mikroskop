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

def set_ledpwr(pwr):
    with SMBus(1) as bus:
        checksum = ((pwr + pwr)) % 256 
        bus.write_i2c_block_data(addr, 4, [ 4 , pwr, pwr,checksum])

def send_simplecmd(cmd):
    with SMBus(1) as bus:
        bus.write_byte_data(addr, cmd, cmd) #command is sent twice to be executed

def read_postions():
    # Read 12 bytes
    with SMBus(1) as bus:
        msg = bus.read_i2c_block_data(addr, 0, 15) #generate I²C msg instance as msg

    #parse the 12 bytes into 3*4 bytes values
    X_b = []
    Y_b = []
    Focus_b = []
    i = 1
    for value in msg: 
        if i <= 4:
            X_b.append(value) 
        if 5 <= i <= 8:
            Y_b.append(value) 
        if 9 <= i <= 12:
            Focus_b.append(value) 
        i = i+1

    X_pos = int.from_bytes(X_b, byteorder='little', signed=False)
    Y_pos = int.from_bytes(Y_b, byteorder='little', signed=False)
    Focus_pos = int.from_bytes(Focus_b, byteorder='little', signed=False)

    return X_pos, Y_pos, Focus_pos


while True:
    while not GPIO.input(4): # read position only if pin 4 is up = arduino is ready
        time.sleep(0.1)
    x_position, y_position, f_position = read_postions()

    
    print(" 1 : X (current : ", x_position, ") \n 2 : Y (current : ", y_position, ")\n 3 : F (current : ", f_position, ")")   
    cmd_input = input("cmd:")
    if cmd_input != '':
        
        for i,a in enumerate(['x','y','f']):
            if cmd_input == a:
                cmd_input = i+1

        cmd = int(cmd_input)

        if cmd == 4:
            ledpwr_input = input("Led power (0 - 255):")
            set_ledpwr(int(ledpwr_input))

        if cmd in [1,2,3]:
            destination_input = input("destination in steps:")
            send_destination(int(cmd), int(destination_input))

        if cmd in [101, 102, 103, 255]:
            send_simplecmd(int(cmd))


