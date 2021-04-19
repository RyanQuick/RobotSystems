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

from picarx_classes import Motors, Sensors, Interpreters, Controllers
import time
import cv2

def move_forward(speed,length,angle):
    Motors.set_dir_servo_angle(Motors(), angle)
    Motors.forward(Motors(), speed)
    time.sleep(length)
    Motors.stop(m)
    print('finished moving forward')
    
def pl_park(speed, length, direction=-1):
    Motors.set_dir_servo_angle(Motors(), direction*40)
    Motors.backward(Motors(), speed)
    time.sleep(length*.50)
    Motors.set_dir_servo_angle(Motors(), -direction*40)
    Motors.backward(Motors(), speed)
    time.sleep(length*.50)
    
    
def k_turn(speed, length, direction=-1):
    Motors.set_dir_servo_angle(Motors(), direction*40)
    Motors.forward(Motors(), speed)
    time.sleep(length*.50)
    Motors.set_dir_servo_angle(Motors(), -direction*40)
    Motors.backward(Motors(), speed)
    time.sleep(length*.50)
    Motors.set_dir_servo_angle(Motors(), direction*40)
    Motors.forward(Motors(), speed)
    time.sleep(length*.50)   
    Motors()
    
def test():
    Motors.set_dir_servo_angle(Motors(), -40)
    Motors.camera_servo_pin1.angle(Motors(), -40)
    Motors.camera_servo_pin2.angle(Motors(), -40)
    time.sleep(1)
    Motors.set_motor_speed(Motors(), 1, 1)
    Motors.set_motor_speed(Motors(), 2, 1)
    Motors.set_dir_servo_angle(Motors(), 40)
    Motors.camera_servo_pin1.angle(Motors(), 40)
    Motors.camera_servo_pin2.angle(Motors(), 40)
    time.sleep(1)

def gray_follow_line(speed,length):
    for i in range(length):        
        [position, adcs] = Interpreters().getGrayscaleValue(Sensors().get_adc_value())
        # logging.info("Relative Position: {0}, adc1: {1}, adc2: {2}, adc3: {3}".format(position,adcs[0],adcs[1],adcs[2]))
        Controllers().line_following(position, speed)

def cv_follow_line():
    


# import atexit
# atexit.register(Motors.stop)

if __name__ == "__main__":
    # m = Motors()
    # s = Sensors()
    # i = Interpreters()
    # c = Controllers()
    choice = input('Choose an action to take: (park, forward, kturn, grayfollow)')
    if choice == 'forward':
        print('moving forward...')
        move_forward(50,2,0)
    elif choice == 'park':
        print('parking...')
        pl_park(75, 1.75,-1)
    elif choice == 'kturn':
        print('turning around...')
        k_turn(75,2.25,-1)
    elif choice == 'grayfollow':
        print('Following a line using the ADC grayscale sensor')
        length = int(input('How many Times?') or '1000')
        gray_follow_line(0, length)
    else:
        print('did nothing...')
        pass