#!/usr/bin/python3


from math import tan, pi

try :
    from ezblock import __reset_mcu__
    from ezblock import *
    from ezblock import delay
    
    __reset_mcu__()
    time.sleep(0.01)
except ImportError:
    print ("Simulator")
    from sim_ezblock import *

import picarx_improved
import time

def move_forward(speed,length,angle):
    picarx_improved.set_dir_servo_angle(angle)
    picarx_improved.forward(speed,angle)
    time.sleep(length)
    picarx_improved.stop()
    print('finished moving forward')
    
def pl_park(speed,length, direction=-1):
    # picarx_improved.set_dir_servo_angle(0)
    # time.sleep(.1)
    picarx_improved.set_dir_servo_angle(direction*40)
    picarx_improved.backward(speed,direction*40)
    time.sleep(length*.50)
    picarx_improved.set_dir_servo_angle(-direction*40)
    picarx_improved.backward(speed,-direction*40)
    time.sleep(length*.50)
    
    
def k_turn(speed,length, direction=-1):
    # picarx_improved.set_dir_servo_angle(0)
    # time.sleep(.1)
    picarx_improved.set_dir_servo_angle(direction*40)
    picarx_improved.forward(speed,-direction*40)
    time.sleep(length*.50)
    picarx_improved.set_dir_servo_angle(-direction*40)
    picarx_improved.backward(speed,direction*40)
    time.sleep(length*.50)
    picarx_improved.set_dir_servo_angle(direction*40)
    picarx_improved.forward(speed,-direction*40)
    time.sleep(length*.50)   
        
    
def test():
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
    choice = input('Choose an action to take: (park, forward, kturn)')
    if choice == 'forward':
        print('moving forward...')
        move_forward(50,2,0)
    elif choice == 'park':
        print('parking...')
        pl_park(75, 1.75,-1)
    elif choice == 'kturn':
        print('turning around...')
        k_turn(75,2.25,-1)
    else:
        print('did nothing...')
        pass