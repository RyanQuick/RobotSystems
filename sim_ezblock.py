#!/usr/bin/python3

class Servo():
    def __init__(self, pwm):
        pass

    def angle(self, angle):
        pass
    


class PWM():


    def __init__(self, channel, debug="critical"):
        pass

    def i2c_write(self, reg, value):
        pass

    def freq(self, *freq):
        return 0


    def prescaler(self, *prescaler):
        return 0


    def period(self, *arr):
        return 0

    def pulse_width(self, *pulse_width):
        return 0


    def pulse_width_percent(self, *pulse_width_percent):
        return 0

class Pin():
    

    def __init__(self, *value):
        pass
        
    def check_board_type(self):
        pass

    def init(self, mode, pull=None):
        pass

    def dict(self, *_dict):
        return 0

    def __call__(self, value):
        return 0

    def value(self, *value):
        return 0


    def on(self):
        return 0

    def off(self):
        return 0

    def high(self):
        return 0

    def low(self):
        return 0

    def mode(self, *value):
        return 0
        

    def pull(self, *value):
        return 0

    def irq(self, handler=None, trigger=None, bouncetime=200):
       pass

    def name(self):
        return 0
    def names(self):
        return 0
    
    class cpu(object):
        pass

class ADC():

    def __init__(self, chn):
        pass
        
    def read(self):                     
        return 0

    def read_voltage(self):                           
        return 0
