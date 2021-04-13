#!/usr/bin/python3


from math import tan, pi

try :
    from ezblock import __reset_mcu__
    from ezblock import *
    from ezblock import delay
    
    __reset_mcu__()
    time.sleep(0.01)
except ImportError :
    print (" This computer does not appear to be a PiCar -\
           X system(/ opt / ezblock is not present ) \
           . Shadowing hardware calls with substitute functions ")
    from sim_ezblock import *

import picarx_improved
import time

def move_forward(direction,speed):
    picarx_improved.set_dir_servo_angle(direction)
    picarx_improved.forward(speed)
    time.sleep(0.5)
    picarx_improved.stop()
    
def test():
    picarx_improved.dir_servo_angle_calibration(-10) 
    picarx_improved.set_dir_servo_angle(-40)
    picarx_improved.camera_servo_pin1.angle(-40)
    picarx_improved.camera_servo_pin2.angle(-40)
    time.sleep(1)
    picarx_improved.set_motor_speed(1, 1)
    picarx_improved.set_motor_speed(2, 1)
    picarx_improved.set_dir_servo_angle(40)
    picarx_improved.camera_servo_pin1.angle(40)
    picarx_improved.camera_servo_pin2.angle(40)
    time.sleep(1)

    
if __name__ == "__main__":
    while True:
        #test()
        move_forward(-40,50)