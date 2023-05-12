from smbus2 import SMBus, i2c_msg

addr = 0x8 # bus address
cmd = 0

def send_destination(motor, destination):
    if motor in [1,2,3]:
        destination_as_bytes = (destination).to_bytes(4, byteorder='big', signed=False)
        with SMBus(1) as bus:
            bus.write_i2c_block_data(addr, motor, destination_as_bytes)

def set_ledpwr(pwr):
    with SMBus(1) as bus:
        bus.write_i2c_block_data(addr, 4, [ 4 , pwr])

def send_simplecmd(cmd):
    with SMBus(1) as bus:
        print(cmd)
        bus.write_byte_data(addr, cmd, cmd)


while( True ):
    print(" 1 : X \n 2 : Y \n 3 :F")
    cmd_input = input("cmd:")
    if cmd_input != '':
        cmd = int(cmd_input)

    if cmd == 4:
        ledpwr_input = input("Led power (0 - 255):")
        set_ledpwr(int(ledpwr_input))

    if cmd in [1,2,3]:
        destination_input = input("destination in steps:")
        send_destination(int(cmd), int(destination_input))
  
    if cmd in [5, 6, 7, 8, 101, 102, 103, 255]:
        send_simplecmd(int(cmd))

