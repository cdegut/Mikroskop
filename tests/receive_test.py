from smbus2 import SMBus, i2c_msg
import time

addr = 0x8 # bus address

retry = 10
def read_positions(): #get position from the microscope


    with SMBus(1) as bus:
        msg = bus.read_i2c_block_data(addr, 0, 15) #generate I²C msg instance as msg
        print(msg)
    
    led1_b = msg[12]
    led2_b = msg[13]

    checksum = (sum(msg[:14])) %256 #checksum on arduino side is an overflown byte, need to take modulo 256 to reproduce behaviour.
    print(f"Actual checksum : {checksum}\nReceived checksum: {msg[14]}")
    
    if checksum != msg[14]:
        print("Bad Checksum")
    
    #generate integer from the list of bytess.
    
    X_pos = int.from_bytes(msg[:4], byteorder='little', signed=False)
    Y_pos = int.from_bytes(msg[4:8], byteorder='little', signed=False)
    Focus_pos = int.from_bytes(msg[8:12], byteorder='little', signed=False)
    
    positions = [X_pos, Y_pos, Focus_pos, led1_b, led2_b]
    return positions
        
print(read_positions())