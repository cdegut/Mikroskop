from smbus2 import SMBus, i2c_msg
from time import time


addr = 0x8 # bus address


t = time()
print("\n")
def read_postions():


    with SMBus(1) as bus:
        #bus.pec =1
        msg = i2c_msg.read(addr, 15) #generate I²C msg instance as msg
        bus.i2c_rdwr(msg)
        return msg
old_string = ""
repeat = 0
while True:
    X_b = []
    Y_b = []
    Focus_b = []
    i = 1
    msg = read_postions()
    for value in msg:
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

    X_pos = int.from_bytes(X_b, byteorder='little', signed=False)
    Y_pos = int.from_bytes(Y_b, byteorder='little', signed=False)
    Focus_pos = int.from_bytes(Focus_b, byteorder='little', signed=False)
    checksum = (sum(X_b) + sum(Y_b) + sum(Focus_b) + led_b + led_state_b)

    string = f"X: {X_pos}  Y:{Y_pos}  Focus:{Focus_pos} Checksum: {received_checksum} Actual: {checksum %256}      " 
    if string != old_string:
        print("\033[F\033[F" +string)
        print(f"Repeat number: {repeat} runing for {round(time() - t)}s")
    else:
        print(f"\033[FRepeat number: {repeat} runing for {round(time() - t)}s")
    old_string = string
    repeat += 1