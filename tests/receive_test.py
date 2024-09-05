from smbus2 import SMBus, i2c_msg
import time

addr = 0x8 # bus address

retry = 10
def read_positions(): #get position from the microscope


    with SMBus(1) as bus:
        msg = bus.read_i2c_block_data(addr, 0, 15) #generate I²C msg instance as msg
        print(msg)
    
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
            led1_b = value
        if i == 14:
            led2_b = value
        if i == 15:
            received_checksum = value
        i = i+1

    checksum = (sum(X_b) + sum(Y_b) + sum(Focus_b) + led1_b + led2_b) %256 #checksum on arduino side is an overflown byte, need to take modulo 256 to reproduce behaviour
    
    if checksum != received_checksum:
        print("Bad Checksum")
    
    #generate integer from the list of bytess.
    
    X_pos = int.from_bytes(X_b, byteorder='little', signed=False)
    Y_pos = int.from_bytes(Y_b, byteorder='little', signed=False)
    Focus_pos = int.from_bytes(Focus_b, byteorder='little', signed=False)
    
    positions = [X_pos, Y_pos, Focus_pos, led1_b, led2_b]
    return positions
        
print(read_positions())