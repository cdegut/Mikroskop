from .super import Interface
from tkinter import Frame, Button, BOTH, Label, Scale, HORIZONTAL


def led_focus_zoom_buttons(self, position=400):
    Focus = Button(self, width=4, text="Focus", command=lambda: Focus_popup.open(self))     
    Ledbutton = Button(self, width=4, text="Light", command=lambda: Led_popup.open(self))
    ZoomButton = Button(self, width=4, text="Zoom", command=lambda: Zoom_popup.open(self))
    Focus.place(x=80, y=position)
    Ledbutton.place(x=10, y=position)
    ZoomButton.place(x=150, y=position)

class Led_popup(Interface, Frame): #widget to fill popup window, show an stop button and a modifiable label

    def __init__(self, Tk_root, last_window, microscope, parameters, camera):
        Interface.__init__(self, Tk_root, last_window, microscope, parameters=parameters, camera=camera)
        self.auto_exp_value = "auto"
        self.awb_value = "auto"
        self.init_window(last_window)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window):  
        self.last_window = last_window
        
        self.Tk_root.title("Led") 
        self.pack(fill=BOTH, expand=1)

        Power_label = Label(self, text = "LED power:")
        self.Led_scale = Scale(self, from_=0, to=255, length=200, width=60, orient=HORIZONTAL)
        Save =  Button(self, text="Save", command=self.save_led)

        Led1 = Button(self, text="LED 1", command= lambda: self.led_change(1))
        Led2 = Button(self, text="LED 2", command= lambda:  self.led_change(2))
        #Led12 = Button(self, text="Led 1+2", command= lambda: self.microscope.set_led_state(3))
        #Led12Low = Button(self, text="Led 1Low+2", command= lambda: self.microscope.set_led_state(4))
        LedOff = Button(self, text="Off", command= lambda: self.microscope.set_led_state(0))

        self.AutoExp = Button(self, text="AutoExp ON", command=self.auto_exp)
        Shutter_label = Label(self, text = "Shutter speed (μs);")
        self.Exp_scale = Scale(self, from_=100, to=15000, length=200, width=60, resolution=100, orient=HORIZONTAL)
        Gain_label = Label(self, text = "Analogue Gain:")
        self.Gain_scale = Scale(self, from_=1.0, to=10.5, length=200, width=60, resolution=0.5, orient=HORIZONTAL)
        self.AWB_button = Button(self, text="Normal mode", command=self.awb)

        #Led12.place(x=20,y=170)
        #Led12Low.place(x=110,y=170)
        Power_label.place(x=10, y= 55)  
        self.Led_scale.place(x=10,y=70)
        
        Led1.place(x=20,y=30)
        Led2.place(x=90,y=30)
        LedOff.place(x=160,y=30)
        self.AWB_button.place(x=20,y=170)
           
        self.AutoExp.place(x=20,y=210) 
        
        Shutter_label.place(x=10, y= 245)  
        self.Exp_scale.place(x=10,y=260)
        Gain_label.place(x=10, y= 355)  
        self.Gain_scale.place(x=10,y=370)



        self.Led_scale.set(self.microscope.positions[3])


        self.set_led()
        self.set_exp()
        self.set_analog_gain()
        Save.place(x=20, y=490)
        self.back_button(position=(90,490))

        if self.auto_exp_value == "off":
            self.AutoExp.config(text="AutoExp OFF")
        
        if self.awb_value == "off":
            self.AWB_button.config(text="AWB Fluo")


    def led_change(self, led):
        if led == 1:
            self.microscope.set_led_state(1)
            self.camera.awb_preset("white")
            self.AWB_button.config(text="Normal mode")

        if led == 2:
            self.microscope.set_led_state(2)
            self.camera.awb_preset("Green Fluo")
            self.AWB_button.config(text="Green Fluo Mode")

    def auto_exp(self):
        if self.auto_exp_value == "auto":
            self.camera.auto_exp_enable(False)
            self.auto_exp_value = "off"
            self.AutoExp.config(text="AutoExp OFF")
        
        elif self.auto_exp_value == "off":
            self.camera.auto_exp_enable(True)
            self.auto_exp_value = "auto"
            self.AutoExp.config(text="AutoExp ON")
    
    def awb(self):
        if self.awb_value == "auto":
            self.awb_value = "off"
            self.camera.awb_preset("Green Fluo")
            self.AWB_button.config(text="Green Fluo Mode")

        elif self.awb_value == "off":
            self.awb_value = "auto"
            self.camera.awb_preset( "auto")
            self.AWB_button.config(text="Normal mode")
   
    def save_led(self):
        self.parameters.update([("led",[self.microscope.positions[3], self.microscope.positions[4]])])

    def set_led(self): ## Read the scale and set the led at the proper power
        pwr = self.Led_scale.get()
        if pwr != self.microscope.positions[3]:
            self.microscope.positions[3] = pwr
            self.microscope.set_ledpwr(pwr)
        Interface._job1 = self.after(100, self.set_led)
    
    def set_exp(self): ## Read the scale and set the led at the proper power
        exp_scale = self.Exp_scale.get()
        real_exp = self.camera.curent_exposure()[0]
        if exp_scale != real_exp: 
            if self.auto_exp_value == "off":
                self.camera.set_exposure( exp_scale)
            elif self.auto_exp_value == "auto":
                self.Exp_scale.set(real_exp)
        
        Interface._job2 = self.after(100, self.set_exp)
    
    def set_analog_gain(self):
        gain_scale = self.Gain_scale.get()
        real_gain = self.camera.curent_exposure()[1]
        if gain_scale != real_gain: 
            if self.auto_exp_value == "off":
                self.camera.set_exposure( gain=gain_scale)
            elif self.auto_exp_value == "auto":
                self.Gain_scale.set(real_gain)
        
        Interface._job3 = self.after(100, self.set_analog_gain)
         

    def set_default(self): ## Read led power from Default parameter set
        led = self.parameters.get("Default")["led"]
        self.microscope.set_ledpwr(led[0])
        self.microscope.positions[3] = led[0]
        self.microscope.set_led_state(led[1])
        self.Led_scale.set(self.microscope.positions[3])
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._led_popup:
            Interface._led_popup.init_window(self)
        else:
            Interface._led_popup = Led_popup(self.Tk_root, last_window=self, microscope=self.microscope, parameters=self.parameters, camera=self.camera)


class Focus_popup(Interface, Frame):

    def __init__(self, Tk_root, last_window, microscope,  grid, parameters):
        Interface.__init__(self, Tk_root, last_window=self, microscope=microscope, grid=grid, parameters=parameters)    
        self.init_window(last_window)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window):
        self.last_window = last_window
        
        self.Tk_root.title("Focus") 
        self.pack(fill=BOTH, expand=1)
        self.show_record_label()

        Fp100 = Button(self, text="Fcs +200", command=lambda: self.microscope.move_1axis(3,200))
        Fm100 = Button(self, text="Fcs -200", command=lambda: self.microscope.move_1axis(3,-200))

        Fp25 = Button(self, text="Fcs +25 ", command=lambda: self.microscope.move_1axis(3,25))
        Fm25 = Button(self, text="Fcs -25 ", command=lambda: self.microscope.move_1axis(3,-25))

        Fp5 = Button(self, text="Fcs +5  ", command=lambda: self.microscope.move_1axis(3,5))
        Fm5 = Button(self, text="Fcs -5  ", command=lambda: self.microscope.move_1axis(3,-5))

        save = Button(self, fg='green',text="Save", command=self.save_focus)
        Reset = Button(self, fg='red', text="Reset", command=lambda: self.microscope.move_focus(self.parameters.get()["start"][2]))
        
        ObjOn = Button(self, text="ObjOn", command=lambda:  self.microscope.move_focus(self.parameters.get()["start"][2] - 600 ))
        ObjOff = Button(self, text="ObjOff", command=lambda: self.microscope.move_focus(0))
        
        Fp100.place(x=10, y=200)
        Fm100.place(x=100, y=200)
        Fp25.place(x=10, y=245)
        Fm25.place(x=100, y=245)
        Fp5.place(x=10, y=290)
        Fm5.place(x=100, y=290)

        ObjOff.place(x=10, y=100)
        ObjOn.place(x=100, y=100)


        save.place(x=80,y=350)
        Reset.place(x=10, y=350)
        self.back_button()

    def save_focus(self):
        self.parameters.update_start(None , None, self.microscope.positions[2], None)
        self.grid.generate_grid()
   
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._focus_popup:
            Interface._focus_popup.init_window(self)
        else:
            Interface._focus_popup = Focus_popup(self.Tk_root, last_window=self, microscope=self.microscope, grid=self.grid, parameters=self.parameters)

class Zoom_popup(Interface, Frame): #widget to fill popup window, show an stop button and a modifiable label

    def __init__(self, Tk_root, last_window, microscope, parameters, camera):
        Interface.__init__(self, Tk_root, last_window, microscope, parameters=parameters, camera=camera)
        self.init_window(last_window)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window):
        self.last_window = last_window 
        self.Tk_root.title("Zoom") 
        self.pack(fill=BOTH, expand=1)
        self.show_record_label()

        if not Interface._video_timer: ## Deactivate zoom button if filming
            zoom_buttons = [(" 1x", 1),("1.5x", 0.75),(" 2x", 0.5),(" 4x", 0.25),(" 8x", 0.125)]
            y_p = 30
            for button in zoom_buttons:
                b = Button(self, text=button[0], width=10, heigh=2, command=lambda value = button[1]: self.camera.change_zoom(value))
                b.place(x=60, y=y_p)
                y_p = y_p+60
        else:
            warning = Label(self, text="Can't change zoom \n whilerecording video")
            warning.place(x=10, y=30)

        self.back_button()
        self.snap_button()

    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._zoom_popup:
            Interface._zoom_popup.init_window(self)
        else:
            Interface._zoom_popup = Zoom_popup(self.Tk_root, last_window=self, microscope=self.microscope, parameters=self.parameters, camera=self.camera)