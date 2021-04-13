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

# import sys
# sys.path.append(r'/opt/ezblock')
# from ezblock import __reset_mcu__
# import time
# __reset_mcu__()
# time.sleep(0.01)

# from picarmini import dir_servo_angle_calibration
# from picarmini import forward
# from ezblock import delay
# from picarmini import backward
# from picarmini import set_dir_servo_angle
# from picarmini import stop


# dir_servo_angle_calibration(0)

def move_forward(direction,speed):
    picarx_improved.set_dir_servo_angle(direction)
    # picarx_improved.forward(speed)
    print('direction: ', direction, 'speed: ', speed)
    
def test():
    picarx_improved.dir_servo_angle_calibration(-10) 
    picarx_improved.set_dir_servo_angle(-40)
    picarx_improved.time.sleep(1)
    picarx_improved.set_dir_servo_angle(0)
    time.sleep(1)
    picarx_improved.set_motor_speed(1, 1)
    picarx_improved.set_motor_speed(2, 1)
    #camera_servo_pin1.angle(0)
    #camera_servo_pin2.angle(0)
    
if __name__ == "__main__":
    picarx_improved.dir_servo_angle_calibration(0)
    while True:
        #move_forward(i,100)
        test()