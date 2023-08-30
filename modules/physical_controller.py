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
    
    if steps > 256:
        steps = 256
    if steps < -256:
        steps = -256

    microscope.push_axis(axis , steps)
    encoder.internal_counter = 0

def controller_startup():
    from .microscope_param import F_controller_pinA, F_controller_pinB, F_controller_Switch, Y_controller_pinA , Y_controller_pinB, Y_controller_Switch, X_controller_pinA, X_controller_pinB, X_controller_Switch
        #Generate the objects for the physical interface
    try:
        encoder_F = Encoder(F_controller_pinA, F_controller_pinB, "up", F_controller_Switch)
        encoder_Y = Encoder(Y_controller_pinA , Y_controller_pinB ,"up",Y_controller_Switch)
        encoder_X = Encoder(X_controller_pinA, X_controller_pinB,"up",X_controller_Switch)
    except: ##sometimes crash, try to redo it after gpio cleanup
        from RPi import GPIO
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        print("Trying the controller set up again")
        encoder_F = Encoder(F_controller_pinA, F_controller_pinB, "up", F_controller_Switch)
        encoder_Y = Encoder(Y_controller_pinA , Y_controller_pinB ,"up",Y_controller_Switch)
        encoder_X = Encoder(X_controller_pinA, X_controller_pinB,"up",X_controller_Switch)
    
    return encoder_X, encoder_Y, encoder_F


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

    encoder_X, encoder_Y, encoder_F = controller_startup()
    
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
    

