from smbus2 import SMBus, i2c_msg
from time import sleep

addr = 0x8 # bus address

def read_postions():

    with SMBus(1) as bus:
        #bus.pec =1
        msg = i2c_msg.read(addr, 15) #generate I²C msg instance as msg
        bus.i2c_rdwr(msg)

i = 0
while True:
    print(i)
    read_postions()
    sleep(0.1)
    i += 1