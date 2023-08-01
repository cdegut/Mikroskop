from .encoder_class import Encoder

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val     
    
def encoder_read(microscope, encoder, axis, short_steps, long_steps):
    value = encoder.internal_counter
    if value == 0:
        return
    elif value >0:
        sign = 1
    else:
        sign = -1 
    ## Check state to know if doing large or small movement, calculate steps accordingly
    if encoder.sw_state:
        steps = short_steps * sign
    else:
        steps = long_steps * sign

    microscope.push_axis(axis , steps)
    encoder.internal_counter = 0


if __name__ == "__main__":

    from .parametersIO import *
    from .microscope import *
    from .cameracontrol import *
    from RPi import GPIO

    GPIO.setmode(GPIO.BCM)
    microscope = Microscope(addr, ready_pin)
    microscope.set_led_state(1)
    microscope.set_ledpwr(200)

    #start picamPreview
    #camera = picamera.PiCamera()
    #previewPiCam(camera)

    encoder_F = Encoder(6, 12, "up",sw_pin=21)
    encoder_Y = Encoder(19, 16,"up",sw_pin=13)
    encoder_X = Encoder(26, 20,"up",sw_pin=5)
    
    try:
        while True:
            time.sleep(0.01)
            encoder_read(microscope, encoder_X,1,X_controller_short, X_controller_long)
            encoder_read(microscope, encoder_Y,2,Y_controller_short, Y_controller_long)
            encoder_read(microscope, encoder_F,3,F_controller_short, F_controller_long)

        
    except KeyboardInterrupt:
        pass

    microscope.set_led_state(0)
    GPIO.cleanup()
    

