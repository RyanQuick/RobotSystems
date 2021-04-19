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

from picarx_classes import Motors
import time

def move_forward(speed,length,angle):
    Motors.set_dir_servo_angle(motor_class,angle)
    Motors.forward(motor_class,speed)
    time.sleep(length)
    Motors.stop(m)
    print('finished moving forward')
    
def pl_park(speed, length, direction=-1):
    Motors.set_dir_servo_angle(motor_class,direction*40)
    Motors.backward(motor_class,speed)
    time.sleep(length*.50)
    Motors.set_dir_servo_angle(motor_class,-direction*40)
    Motors.backward(motor_class,speed)
    time.sleep(length*.50)
    
    
def k_turn(speed, length, direction=-1):
    Motors.set_dir_servo_angle(motor_class,direction*40)
    Motors.forward(motor_class,speed)
    time.sleep(length*.50)
    Motors.set_dir_servo_angle(motor_class,-direction*40)
    Motors.backward(motor_class,speed)
    time.sleep(length*.50)
    Motors.set_dir_servo_angle(motor_class,direction*40)
    Motors.forward(motor_class,speed)
    time.sleep(length*.50)   
        
    
def test():
    Motors.set_dir_servo_angle(motor_class,-40)
    Motors.camera_servo_pin1.angle(motor_class,-40)
    Motors.camera_servo_pin2.angle(motor_class,-40)
    time.sleep(1)
    Motors.set_motor_speed(motor_class,1, 1)
    Motors.set_motor_speed(motor_class,2, 1)
    Motors.set_dir_servo_angle(motor_class,40)
    Motors.camera_servo_pin1.angle(motor_class,40)
    Motors.camera_servo_pin2.angle(motor_class,40)
    time.sleep(1)



# import atexit
# atexit.register(Motors.stop)

if __name__ == "__main__":
    # while True:
    # test()
    motor_class = Motors()
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