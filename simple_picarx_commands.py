#!/usr/bin/python3


from math import tan, pi

try :
    from ezblock import __reset_mcu__
    from ezblock import *
    from ezblock import delay
    
    __reset_mcu__()
    time.sleep(0.01)
except ImportError:
    print (" This computer does not appear to be a PiCar -\
           X system(/ opt / ezblock is not present ) \
           . Shadowing hardware calls with substitute functions ")
    from sim_ezblock import *

import picarx_improved
import time

def move_forward(speed,length,angle):
    picarx_improved.set_dir_servo_angle(angle)
    picarx_improved.forward(speed)
    time.sleep(length)
    picarx_improved.stop()
    
def pl_park(speed,length, direction=-1):
    picarx_improved.set_dir_servo_angle(0)
    time.sleep(.1)
    picarx_improved.set_dir_servo_angle(direction*50)
    picarx_improved.backward(speed)
    time.sleep(length/2)
    picarx_improved.set_dir_servo_angle(-direction*50)
    time.sleep(length/2)
        
        
    
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



# import atexit
# atexit.register(picarx_improved.stop)

if __name__ == "__main__":
    # while True:
    # test()
    # move_forward(50,1,-40)
    pl_park(100, 1.5,-1)