
from RPi import GPIO

class Encoder:

    def __init__(self, clk_pin, dt_pin, pull="up", sw_pin=None, encoder_callback=None, switch_callback=None):

        ##Initiate internal states states
        self.last_state = (0,0)
        self.direction = 0
        self.sw_state = False
        self.sw_counter = 0
        self.internal_counter = 0
        
        ##callback function       
        self.encoder_callback = encoder_callback
        self.switch_callback = switch_callback

        ## Pins
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.sw_pin = sw_pin
        if pull == "up":
            self.pull = True
        else:
            self.pull = False
        
        ##set pin states
        if self.pull:
            GPIO.setup(self.clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            if sw_pin:
                GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        else:
            GPIO.setup(self.clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self.dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            if sw_pin:
                GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(self.clk_pin, edge=GPIO.BOTH, callback=self.__read_state)  
        GPIO.add_event_detect(self.dt_pin, edge=GPIO.BOTH, callback=self.__read_state)
        if sw_pin:
            GPIO.add_event_detect(self.sw_pin, GPIO.RISING, callback=self.__switch_click, bouncetime=500)  

    ### End of init 

    def __switch_click(self, channel):
        self.sw_state = not self.sw_state
        self.sw_counter +=1
        if self.switch_callback:
            self.switch_callback()
    
    def __read_state(self, channel):
        
        #Generate curate state
        dt_state =  GPIO.input(self.dt_pin)
        clk_state =  GPIO.input(self.clk_pin)

        if self.pull:
            state = (not clk_state, not dt_state)
        else:
            state = (clk_state, dt_state)

    #### 00 mark the end of a turn
        if state == (0,0):
            ## check that the click is in the same direction as previous detected
            if self.last_state == (1,0) and self.direction == 1:
                self.internal_counter += 1
                if self.encoder_callback:
                    self.encoder_callback()
                self.direction = 0 ## set direction to 0 after the callback
                
            if self.last_state == (0,1)and self.direction == -1:
                self.internal_counter -= 1
                if self.encoder_callback:
                    self.encoder_callback()
                self.direction = 0 ## set direction to 0 after the callback
        
    ## Detect direction before the end of click to cross validate the click
        elif state == (0,1):
            if self.last_state == (0,0):
                self.direction = 1
            if self.last_state == (1,1):
                self.direction = -1 
        
        elif state == (1,0):
            if self.last_state == (1,1):
                self.direction = 1
            if self.last_state == (0,0):
                self.direction = -1
        
        elif state == (1,1):
            if self.last_state == (0,1):
                self.direction = 1
            if self.last_state == (1,0):
                self.direction = -1  
                
        self.last_state = state