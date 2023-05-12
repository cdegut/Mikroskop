from smbus2 import SMBus, i2c_msg

addr = 0x8 # bus address

def read_postions():

    with SMBus(1) as bus:
        # Read 64 bytes from address 80
        msg = i2c_msg.read(addr, 12)
        bus.i2c_rdwr(msg)

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

a,b,c = read_postions()
print(a,'  ', b , '  ', c)