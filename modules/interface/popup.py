from tests.test import LEDArray
from .super import Interface
from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkSlider, BOTH, HORIZONTAL, N
from modules.controllers import *


def led_focus_zoom_buttons(self, position=400):
    Focus = CTkButton(self, width=60, text="Focus", command=lambda: Focus_popup.open(self))     
    Ledbutton = CTkButton(self, width=60, text="Light", command=lambda: Led_popup.open(self))
    ZoomButton = CTkButton(self, width=60, text="Zoom", command=lambda: Zoom_popup.open(self))
    Focus.place(x=80, y=position)
    Ledbutton.place(x=10, y=position)
    ZoomButton.place(x=150, y=position)

class Led_popup(Interface, CTkFrame): #widget to fill popup window, show an stop button and a modifiable label

    def __init__(self, Tk_root, last_window, microscope: MicroscopeManager, parameters, camera):

        Interface.__init__(self, Tk_root, last_window, microscope, parameters=parameters, camera=camera)
        self.auto_exp_value = "auto"
        self.awb_value = "auto"
        self.darkField_status = "Off"
        self.darkfield_type = "Normal"
        self.init_window(last_window)
        
    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window):
        self.last_window = last_window
        
        self.Tk_root.title("Light and Exposure") 
        self.pack(fill=BOTH, expand=1)

        self.led1_label = CTkLabel(self, text = "LED power:")
        self.led1_scale = CTkSlider(self, from_=0, to=100, height=60, width=200, orientation=HORIZONTAL)
        self.led2_label = CTkLabel(self, text = "LED power:")
        self.led2_scale = CTkSlider(self, from_=0, to=100, height=60, width=200, orientation=HORIZONTAL)

        Save =  CTkButton(self, width=80, text="Save", command=self.save_capture_param)


        
        self.Shutter_label = CTkLabel(self, text = "Shutter speed μs")
        self.Exp_scale = CTkSlider(self, from_=100, to=83000, height=60, width=200, number_of_steps=(20000-100)/100, orientation=HORIZONTAL)
        self.Gain_label = CTkLabel(self, text = "")
        self.Gain_scale = CTkSlider(self, from_=1.0, to=10.5, height=60, width=200, number_of_steps=(10.5-1)/0.5, orientation=HORIZONTAL)
        self.EV_label = CTkLabel(self, text = "EV:")
        self.EV_scale = CTkSlider(self, from_=-2.0, to=2, height=60, width=200, number_of_steps=8, orientation=HORIZONTAL)
        
        self.DarkField_button = CTkButton(self, text=f"Darkfield: {self.darkField_status}", command=self.darkfield_switch, width=100, height = 40)
        self.DarkField_select_button = CTkButton(self, text=f"type {self.darkfield_type}", command=self.darkfield_select, width=100, height = 40)
        self.AWB_button = CTkButton(self, text=f"AWB: {self.awb_value}", command=self.awb, width=100, height = 40)
        #self.AWB_custom = CTkButton(self, text=f"Custom config", command=self.awb_config, width=100, height = 40)

        self.AutoExp = CTkButton(self, text="AutoExp ON", command=self.auto_exp, width=100, height = 40)


        self.led1_label.place(x=10, y= 10)  
        self.led1_scale.place(relx=0.5, y=35, anchor=N)
        self.led1_scale.set(self.microscope.led1pwr)
        self.led2_label.place(x=10, y= 95)  
        self.led2_scale.place(relx=0.5, y=120, anchor=N)
        self.led2_scale.set(self.microscope.led2pwr)

        self.DarkField_button.place(x=10,y=190)
        self.DarkField_select_button.place(x=120,y=190)
        self.AWB_button.place(x=10,y=240)   
        #self.AWB_custom.place(x=120,y=240)     
        self.AutoExp.place(relx=0.5,y=290, anchor=N ) 

        self.exposure_panel()

        self.set_exp_and_gain()
        self.set_led()
        
        #Save.place(x=110, y=490)
        self.back_button(position=(10,520))

        if self.auto_exp_value == "off":
            self.AutoExp.configure(text="AutoExp OFF")
        
        if self.awb_value == "Green Fluo":
            self.AWB_button.configure(text="AWB Fluo")


    def exposure_panel(self):
            y_pos =340
            
            if self.auto_exp_value == "off":
                self.EV_scale.place_forget()
                self.EV_label.place_forget()

                self.Shutter_label.place(x=10, y= y_pos)
                self.Exp_scale.place(relx=0.5,y=y_pos+25, anchor=N)
                self.Exp_scale.set(self.camera.metadata['ExposureTime'])

                self.Gain_label.place(x=10, y= y_pos + 90)  
                self.Gain_scale.place(relx=0.5,y=y_pos + 90 + 25, anchor=N)
                self.Gain_scale.set(self.camera.metadata['AnalogueGain'])

            else:
                self.Exp_scale.place_forget()
                self.Gain_scale.place_forget()
            
                self.Shutter_label.place(x=10, y= y_pos)
                self.Gain_label.place(x=10, y= y_pos + 20)

                self.EV_label.place(x=10, y= y_pos + 45)  
                self.EV_scale.place(relx=0.5,y=y_pos + 45 +25 , anchor=N)
                self.EV_scale.set(self.camera.EV_value)


    def darkfield_switch(self):

        if self.darkField_status == "Off":
            self.darkField_status = "On"

            self.DarkField_button.configure(text = f"Darkfield: {self.darkField_status}")
            
            match self.darkfield_type:
    
                case "Normal":
                    self.microscope.request_led_array(LEDArray(255,255,80))
                    return    

                case "Blue":
                    self.microscope.request_led_array(LEDArray(0,0,255))
                    return    
                
                case "Blue-Red":
                    bluered = LEDArray(255,0,0)
                    bluered.half(0,0,128, 8)
                    self.microscope.request_led_array(bluered)
                    return        
        
                case "Half":
                    half = LEDArray(255,255,80)
                    half.half(0,0,0, 8)
                    self.microscope.request_led_array(half)
                    return          

                case "Quarter":
                    quart = LEDArray(0,0,0)
                    quart.quarter(255,255,80, 0)
                    self.microscope.request_led_array(quart)
                    return      

      
        else:

            self.microscope.request_led_array(LEDArray(0,0,0))
            self.darkField_status = "Off"
            self.DarkField_button.configure(text = f"Darkfield: {self.darkField_status}")
    
    def darkfield_select(self):
        match self.darkfield_type:
            case "Normal":
                self.darkfield_type = "Blue"

            case "Blue":
                self.darkfield_type = "Blue-Red"
            
            case "Blue-Red":
                self.darkfield_type = "Half"
    
            case "Half":
                self.darkfield_type = "Quarter"
            
            case _:
                self.darkfield_type = "Normal"
        
        self.DarkField_select_button.configure(text = f"type: {self.darkfield_type}")

    def auto_exp(self):
        if self.auto_exp_value == "auto":
            self.camera.auto_exp_enable(False)
            self.auto_exp_value = "off"
            self.exposure_panel()
       
        elif self.auto_exp_value == "off":
            self.camera.auto_exp_enable(True)
            self.auto_exp_value = "auto"
            self.exposure_panel()
    
    def awb(self):
        if self.awb_value == "White LED":
            self.awb_value = "auto"
            self.camera.awb_preset("auto")
            self.AWB_button.configure(text=f"AWB: {self.awb_value}")

        elif self.awb_value == "auto":
            self.awb_value = "Green Fluo"
            self.camera.awb_preset("Green Fluo")
            self.AWB_button.configure(text=f"AWB: {self.awb_value}")

        elif self.awb_value == "Green Fluo":
            self.awb_value = "Green Fluo 2"
            self.camera.awb_preset("Green Fluo 2")
            self.AWB_button.configure(text=f"AWB: {self.awb_value}")

        elif self.awb_value == "Green Fluo 2":
            self.awb_value = "Green Fluo 3"
            self.camera.awb_preset("Green Fluo 3")
            self.AWB_button.configure(text=f"AWB: {self.awb_value}")

        elif self.awb_value == "Green Fluo 3":
            self.awb_value = "Green Fluo 4"
            self.camera.awb_preset("Green Fluo 4")
            self.AWB_button.configure(text=f"AWB: {self.awb_value}")

        elif self.awb_value == "Green Fluo 4":
            self.awb_value = "White LED"
            self.camera.awb_preset("White LED")
            self.AWB_button.configure(text=f"AWB: {self.awb_value}")
   
    def save_capture_param(self):
        self.camera.capture_param["led1pwr"] = self.led1_scale.get()
        self.camera.capture_param["led2pwr"] = self.led2_scale.get()
        self.camera.capture_param["auto_exp"] = self.auto_exp_value
        self.camera.capture_param["exp"] = self.camera.metadata['ExposureTime']
        self.camera.capture_param["gain"] = self.camera.metadata['AnalogueGain']
        self.camera.capture_param["awb"] = self.awb_value
        self.camera.capture_param["EV"] = self.EV_scale.get()

    def set_led(self): ## Read the scale and set the led at the proper power
        pwr_1 = int(self.led1_scale.get())
        pwr_2 = int(self.led2_scale.get())
        self.led1_label.configure(text=f"LED 1 power: {pwr_1}")
        self.led2_label.configure(text=f"LED 2 power: {pwr_2}")

        if pwr_1 != self.microscope.led1pwr or pwr_2 != self.microscope.led2pwr:
            self.microscope.led1pwr = pwr_1
            self.microscope.led2pwr = pwr_2
            self.microscope.request_ledspwr(pwr_1, pwr_2)
        Interface._job1 = self.after(100, self.set_led)
    
    def set_exp_and_gain(self): ## Read the scale and set the led at the proper power
        
        exp_scale = int(self.Exp_scale.get())
        self.Shutter_label.configure(text=f"Shutter speed {exp_scale}μs")

        current_exp = self.camera.metadata['ExposureTime']
        if exp_scale != current_exp: 
            if self.auto_exp_value == "off":
                self.camera.set_exposure( exp_scale)
            elif self.auto_exp_value == "auto":
                if current_exp > 20000:
                    current_exp = 20000
                self.Exp_scale.set(current_exp)
        
        gain_scale = int(self.Gain_scale.get())
        self.Gain_label.configure(text=f"Analogue Gain: {gain_scale}")

        current_gain = self.camera.metadata['AnalogueGain']
        if gain_scale != current_gain: 
            if self.auto_exp_value == "off":
                self.camera.set_exposure(gain=gain_scale)
            elif self.auto_exp_value == "auto":
                self.Gain_scale.set(current_gain)
        
        if self.auto_exp_value == "auto":
            EV = self.EV_scale.get()
            self.EV_label.configure(text=f"EV: {EV}")
            self.camera.set_EV(EV)

        Interface._job2 = self.after(200, self.set_exp_and_gain)
         
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._led_popup:
            Interface._led_popup.init_window(self)
        else:
            Interface._led_popup = Led_popup(self.Tk_root, last_window=self, microscope=self.microscope, parameters=self.parameters, camera=self.camera)


class Focus_popup(Interface, CTkFrame):

    def __init__(self, Tk_root, last_window, microscope: MicroscopeManager,  position_grid, parameters):
        Interface.__init__(self, Tk_root, last_window=self, microscope=microscope, position_grid=position_grid, parameters=parameters)    
        self.init_window(last_window)

    ###########
    ### Generate the window content, called every time window is (re)opened 
    def init_window(self, last_window):
        self.last_window = last_window
        
        self.Tk_root.title("Focus") 
        self.pack(fill=BOTH, expand=1)
        self.show_record_label()

        Fp1000 = CTkButton(self, width=80, text="Fcs +1000", command=lambda: self.microscope.request_push_axis("F",1000))
        Fm1000 = CTkButton(self, width=80,text="Fcs -1000", command=lambda: self.microscope.request_push_axis("F",-1000))

        Fp100 = CTkButton(self, width=80, text="Fcs +200", command=lambda: self.microscope.request_push_axis("F",200))
        Fm100 = CTkButton(self, width=80,text="Fcs -200", command=lambda: self.microscope.request_push_axis("F",-200))

        Fp25 = CTkButton(self, width=80,text="Fcs +25 ", command=lambda: self.microscope.request_push_axis("F",25))
        Fm25 = CTkButton(self, width=80,text="Fcs -25 ", command=lambda: self.microscope.request_push_axis("F",-25))

        Fp5 = CTkButton(self, width=80,text="Fcs +5  ", command=lambda: self.microscope.request_push_axis("F",5))
        Fm5 = CTkButton(self, width=80,text="Fcs -5  ", command=lambda: self.microscope.request_push_axis("F",-5))

        save = CTkButton(self, width=80, fg_color='green',text="Save", command=self.save_focus)
        Reset = CTkButton(self, width=80,fg_color='red', text="Reset", command=lambda: self.microscope.request_XYF_travel(-1,-1,self.parameters.get()["start"][2]))
        
        ObjOn = CTkButton(self, width=80, text="ObjOn", command=lambda:  self.microscope.request_XYF_travel(-1,-1,self.parameters.get()["start"][2] - 100 ))
        ObjOff = CTkButton(self, width=80, text="ObjOff", command=lambda: self.microscope.request_XYF_travel(-1,-1,0))

        Fp1000.place(x=10, y=155)
        Fm1000.place(x=100, y=155)       
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
        self.parameters.update_start(None , None, self.microscope.XYFposition[2], None)
        self.position_grid.generate_grid()
   
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._focus_popup:
            Interface._focus_popup.init_window(self)
        else:
            Interface._focus_popup = Focus_popup(self.Tk_root, last_window=self, microscope=self.microscope, position_grid=self.position_grid, parameters=self.parameters)

class Zoom_popup(Interface, CTkFrame): #widget to fill popup window, show an stop button and a modifiable label

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
            y_p = 60
            Zoom_1 = CTkButton(self, text=zoom_buttons[0][0], width=80, height=40, command=lambda: self.camera.change_zoom(zoom_buttons[0][1]))
            Zoom_1.place(relx=0.5, y=30, anchor=N)
            Zoom_2 = CTkButton(self, text=zoom_buttons[1][0], width=80, height=40, command=lambda: self.camera.change_zoom(zoom_buttons[1][1]))
            Zoom_2.place(relx=0.5, y=30+y_p, anchor=N)
            Zoom_3 = CTkButton(self, text=zoom_buttons[2][0], width=80, height=40, command=lambda: self.camera.change_zoom(zoom_buttons[2][1]))
            Zoom_3.place(relx=0.5, y=30+y_p*2, anchor=N)
            Zoom_4 = CTkButton(self, text=zoom_buttons[3][0], width=80, height=40, command=lambda: self.camera.change_zoom(zoom_buttons[3][1]))
            Zoom_4.place(relx=0.5, y=30+y_p*3, anchor=N)
            Zoom_5 = CTkButton(self, text=zoom_buttons[4][0], width=80, height=40, command=lambda: self.camera.change_zoom(zoom_buttons[4][1]))
            Zoom_5.place(relx=0.5, y=30+y_p*4, anchor=N)

        else:
            warning = CTkLabel(self, text="Can't change zoom \n whilerecording video")
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