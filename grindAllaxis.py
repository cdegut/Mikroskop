from modules.microscope import *
#main loop
if __name__ == "__main__": 

    microscope = Microscope(addr, ready_pin)
    while True:
        microscope.wait_ready()
        microscope.checked_send_motor_cmd(1, 30000)
        microscope.wait_ready()
        microscope.checked_send_motor_cmd(1, 00000)
        microscope.wait_ready()
