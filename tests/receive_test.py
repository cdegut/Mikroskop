from smbus2 import SMBus, i2c_msg
from time import sleep

addr = 0x8 # bus address

def read_postions():

    with SMBus(1) as bus:
        #bus.pec =1
        msg = i2c_msg.read(addr, 15) #generate I²C msg instance as msg
        bus.i2c_rdwr(msg)
	#I²C transaction
        #msg = bus.read_block_data(addr, 0xff, 15)

    X_b = []
    Y_b = []
    Focus_b = []
    i = 1
    print(msg)
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

a,b,c = read_postions()
print(a,'  ', b , '  ', c)