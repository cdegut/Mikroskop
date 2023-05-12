from .encoder_class import Encoder
from time import sleep
from threading import Thread

    
def encoder_read(microscope, encoder, axis, base_step, step_multiplier):
    value = encoder.internal_counter
    if value == 0:
        return
    
    ## Allow for large movement when switch is in True position ##
    if encoder.sw_state: 
        sleep(0.05)
        new_value = encoder.internal_counter ## Check if the knob is turning
        
        while new_value != value: ## Try to continue pooling value if turning
            value = new_value
            sleep(0.25)
            new_value = encoder.internal_counter

    if value > 1 or value < -1:
        value * 5 ## increase large pooled value
    
    ## Check state to know if doing large or small movement, calculate steps accordingly
    if encoder.sw_state:
        steps = value * base_step * step_multiplier 
    else:
        steps = value *base_step

    ## Finally move   
    if microscope.is_ready():
        microscope.move_1axis(axis , steps)
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
            encoder_read(microscope, encoder_X,1,X_controler_steps, sw_step_multiplier)
            encoder_read(microscope,encoder_Y,2,Y_controler_steps, sw_step_multiplier)
            encoder_read(microscope,encoder_F,3,F_controler_steps, sw_step_multiplier)
        
    except KeyboardInterrupt:
        pass

    microscope.set_led_state(0)
    GPIO.cleanup()
    

