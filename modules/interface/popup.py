from .super import Interface
import tkinter as tk
from ..parametersIO import update_parameters_led, load_parameters, update_parameters_start
from ..cameracontrol import change_zoom

class Led_popup(Interface, tk.Frame): #widget to fill popup window, show an stop button and a modifiable label

    def __init__(self, Tk_root, last_window, microscope):
        tk.Frame.__init__(self, Tk_root)
        Interface.__init__(self, Tk_root,last_window=self, microscope=microscope)

        self.init_window(last_window)

    ##Initialise the inside of the window
    def init_window(self, last_window):    

        self.last_window = last_window
        self.Tk_root.title("Led") 
        self.pack(fill=tk.BOTH, expand=1)

        OK =  tk.Button(self, text="OK", fg='Red' , command=self.close)
        self.Led = tk.Scale(self, from_=0, to=255, length=200, width=60, orient=tk.HORIZONTAL)
        Default = tk.Button(self, text="Default LED 1&2 pwr = 200", command=self.set_default)
        Save =  tk.Button(self, text="Save", command=lambda: update_parameters_led(self.microscope.positions[3], self.microscope.positions[4]))

        Led1 = tk.Button(self, text="Led 1", command= lambda: self.microscope.set_led_state(1))
        Led2 = tk.Button(self, text="Led 2", command= lambda: self.microscope.set_led_state(2))
        Led12 = tk.Button(self, text="Led 1+2", command= lambda: self.microscope.set_led_state(3))
        LedOff = tk.Button(self, text="Led Off", command= lambda: self.microscope.set_led_state(0))

        self.Led.place(x=10,y=100)

        OK.place(x=20,y=420)
        Save.place(x=20, y=380)
        
        Default.place(x=10,y=40)

        Led1.place(x=20,y=250)
        Led2.place(x=90,y=250)
        Led12.place(x=20,y=300)   
        LedOff.place(x=110,y=300) 

        self.Led.set(self.microscope.positions[3])

        self.set_led()

    def set_led(self): ## Read the scale and set the led at the proper power
        pwr = self.Led.get()
        if pwr != self.microscope.positions[3]:
            self.microscope.positions[3] = pwr
            self.microscope.set_ledpwr(pwr)
        Interface._job1 = self.after(100, self.set_led)

    def set_default(self):
        self.microscope.set_ledpwr(200)
        self.microscope.positions[3] = 200
        self.microscope.set_led_state(3)
        self.Led.set(self.microscope.positions[3])
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._led_popup:
            Interface._led_popup.init_window(self)
        else:
            Interface._led_popup = Led_popup(self.Tk_root, last_window=self, microscope=self.microscope)


class Focus_popup(Interface, tk.Frame):

    def __init__(self, Tk_root, last_window=None, microscope=None, grid=None, camera=None):
        tk.Frame.__init__(self, Tk_root)
        Interface.__init__(self, Tk_root,last_window=self, microscope=microscope)    
        self.init_window(last_window)

   #Creation of init_window

    def init_window(self, last_window):
        self.last_window = last_window
        
        self.Tk_root.title("Focus") 
        self.pack(fill=tk.BOTH, expand=1)

        OK =  tk.Button(self, text="OK", command=self.close)


        Fp100 = tk.Button(self, text="Fcs +200", command=lambda: self.microscope.move_1axis(3,200))
        Fm100 = tk.Button(self, text="Fcs -200", command=lambda: self.microscope.move_1axis(3,-200))

        Fp25 = tk.Button(self, text="Fcs +25", command=lambda: self.microscope.move_1axis(3,25))
        Fm25 = tk.Button(self, text="Fcs -25", command=lambda: self.microscope.move_1axis(3,-25))

        Fp5 = tk.Button(self, text="Fcs +5", command=lambda: self.microscope.move_1axis(3,5))
        Fm5 = tk.Button(self, text="Fcs -5", command=lambda: self.microscope.move_1axis(3,-5))

        save = tk.Button(self, text="Save", command=self.save_focus)
        Reset = tk.Button(self, text="Reset", command=lambda: self.microscope.checked_send_motor_cmd(3, load_parameters()["start"][2]))

        Fp100.place(x=10, y=200)
        Fm100.place(x=100, y=200)
        Fp25.place(x=10, y=245)
        Fm25.place(x=100, y=245)
        Fp5.place(x=10, y=290)
        Fm5.place(x=100, y=290)

        OK.place(x=10,y=380)
        save.place(x=80,y=330)
        Reset.place(x=10, y=330)
    
    def save_focus(self):
        update_parameters_start(None , None, self.microscope.positions[2])
        self.grid.generate_grid()
    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._focus_popup:
            Interface._focus_popup.init_window(self)
        else:
            Interface._focus_popup = Focus_popup(self.Tk_root, last_window=self, microscope=self.microscope)

class Zoom_popup(Interface, tk.Frame): #widget to fill popup window, show an stop button and a modifiable label

    def __init__(self, Tk_root, last_window=None, microscope=None, camera=None):
        tk.Frame.__init__(self, Tk_root)
        Interface.__init__(self, Tk_root, microscope=microscope, camera=camera)

        self.init_window(last_window)

    ##Initialise the inside of the window
    def init_window(self, last_window):
        self.last_window = last_window 
        self.Tk_root.title("Zoom") 
        self.pack(fill=tk.BOTH, expand=1)

        zoom_buttons = [("1x", 1),("1.5x", 0.75),("2x", 0.5),("4x", 0.25),("8x", 0.125)]
        y_p = 50
        for button in zoom_buttons:
            b = tk.Button(self, text=button[0], command=lambda value = button[1]: change_zoom(self.camera, value))
            b.place(x=10, y=y_p)
            y_p = y_p+50

        Snap = tk.Button(self, text="Snap!", command=self.snap_timestamp)

        Snap.place(x=10, y=350)

        self.back_to_main_button()

    
    def open(self):
        self.clear_jobs()
        self.clear_frame()
        if Interface._zoom_popup:
            Interface._zoom_popup.init_window(self)
        else:
            Interface._zoom_popup = Zoom_popup(self.Tk_root, last_window=self, microscope=self.microscope, camera=self.camera)