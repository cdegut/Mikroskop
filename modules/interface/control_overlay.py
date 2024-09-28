from customtkinter import CTkFrame, CTkButton, CTkLabel, N, CTkSlider, IntVar, CENTER, CTkImage, BOTH
from ..microscope import Microscope

class Overlay(CTkFrame): #main GUI window
    def __init__(self, Tk_control, microscope):
        CTkFrame.__init__(self, Tk_control)
        self.microscope = microscope
        self.pack(fill=BOTH, expand=1)

        Up = CTkButton(self,text="Up", width=60, height=60, anchor=CENTER, command=lambda: self.microscope.push_axis(1 , 100))
        Down = CTkButton(self, text="Down",width=60, height=60, anchor=CENTER,command=lambda: self.microscope.push_axis(1 , -100))
        Left = CTkButton(self, text="Left",width=60, height=60, anchor=CENTER,command=lambda: self.microscope.push_axis(2 , 100))
        Right = CTkButton(self, text="Right",width=60, height=60, anchor=CENTER,command=lambda: self.microscope.push_axis(2 , -100))
        Stop = CTkButton(self, text="Stop", width=60, fg_color='#FFADAD', height=60, anchor=CENTER,command=lambda: self.microscope.push_axis(2 , -100))
        Fplus = CTkButton(self, text="F+",width=60, fg_color='#DEDAF4', text_color='black', height=60, anchor=CENTER,command=lambda: self.microscope.push_axis(3 , -100))
        Fminus = CTkButton(self, text="F-", width=60, fg_color='#DEDAF4', text_color='black', height=60, anchor=CENTER,command=lambda: self.microscope.push_axis(3 , -100))


        Up.place(relx=0.5, rely=0.15, anchor=CENTER)
        Down.place(relx=0.5, rely=0.85, anchor=CENTER)
        Left.place(relx=0.15, rely=0.5, anchor=CENTER)
        Right.place(relx=0.85, rely=0.5, anchor=CENTER)
        Stop.place(relx=0.5, rely=0.5, anchor=CENTER)
        Fplus.place(relx=0.85, rely=0.15, anchor=CENTER)
        Fminus.place(relx=0.85, rely=0.85, anchor=CENTER)

#main loop
if __name__ == "__main__": 

    import customtkinter
    from modules.microscope import Microscope
    from modules.microscope_param import *
    from modules.parametersIO import ParametersSets
    parameters = ParametersSets()
    microscope = Microscope(addr, ready_pin, parameters)

    #touch control
    Tk_control = customtkinter.CTk()

    Tk_control.geometry("200x200+0+35")
    Tk_control.wm_attributes("-topmost", True)
    #Tk_control.wm_attributes("-disabled", True)
    Tk_control.wait_visibility(Tk_control)
    Tk_control.wm_attributes("-alpha", 0)
    ### Don't display border if on the RPi display



    overlay = Overlay(Tk_control, microscope)
    overlay.mainloop()





