from .encoder_class import Encoder


    
def encoder_read(microscope, encoder, axis, short_steps, long_steps):
    value = encoder.internal_counter
    if value == 0:
        return
    
    ## Check state to know if doing large or small movement, calculate steps accordingly
    if encoder.sw_state:
        steps = short_steps * value
    else:
        steps = long_steps * value

    if microscope.is_ready():
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
            encoder_read(microscope, encoder_X,1,X_controler_short, X_controler_long)
            encoder_read(microscope, encoder_Y,2,Y_controler_short, Y_controler_long)
            encoder_read(microscope, encoder_F,3,F_controler_short, F_controler_long)
        
    except KeyboardInterrupt:
        pass

    microscope.set_led_state(0)
    GPIO.cleanup()
    

