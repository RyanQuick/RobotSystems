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

from picarx_classes import Motors, Sensors, Interpreters, Controllers, CVSteering
import time
import cv2

def move_forward(m,speed,length,angle):
    m.set_dir_servo_angle(angle)
    m.forward(speed)
    time.sleep(length)
    m.stop()
    print('finished moving forward')
    
def pl_park(speed, length, direction=-1):
    m.set_dir_servo_angle(direction*40)
    m.backward(speed)
    time.sleep(length*.50)
    m.set_dir_servo_angle(-direction*40)
    m.backward(speed)
    time.sleep(length*.50)
    
    
def k_turn(speed, length, direction=-1):
    m.set_dir_servo_angle(direction*40)
    m.forward(speed)
    time.sleep(length*.50)
    m.set_dir_servo_angle(-direction*40)
    m.backward(speed)
    time.sleep(length*.50)
    m.set_dir_servo_angle(direction*40)
    m.forward(speed)
    time.sleep(length*.50)
    
def test():
    m.set_dir_servo_angle(-40)
    m.camera_servo_pin1.angle(-40)
    m.camera_servo_pin2.angle(-40)
    time.sleep(1)
    m.set_motor_speed(1, 1)
    m.set_motor_speed(2, 1)
    m.set_dir_servo_angle(40)
    m.camera_servo_pin1.angle(40)
    m.camera_servo_pin2.angle(40)
    time.sleep(1)

def gray_follow_line(speed):
    while True:        
        [position, adcs] = i.get_grayscale_value(s.get_adc_value())
        # logging.info("Relative Position: {0}, adc1: {1}, adc2: {2}, adc3: {3}".format(position,adcs[0],adcs[1],adcs[2]))
        c.line_following(m, position, speed)

def cv_follow_line(speed):
    while True:
        frame = cvs.start_cv()
        edges = cvs.look_for_color(frame)
        cropped_edges = cvs.crop_video(edges)
        line_segments = cvs.detect_line_segments(cropped_edges)
        path = cvs.average_slope_intercept(cvs, frame, line_segments)
        # cvs.make_points(CVSteering, frame, line)
        new_angle = cvs.steering_angle(path)
        adjusted_angle = cvs.steering_angle_adjustment(new_angle, turn_limit = 30)
        c.line_following(m,adjusted_angle/-30, speed)
        
# import atexit
# atexit.register(Motors.stop)

if __name__ == "__main__":
    m = Motors()
    s = Sensors()
    i = Interpreters()
    c = Controllers()
    cvs = CVSteering()
    choice = input('Choose an action to take: (park, forward, kturn, grayfollow, camerafollow)')
    if choice == 'forward':
        print('moving forward...')
        move_forward(m,50,2,0)
    elif choice == 'park':
        print('parking...')
        pl_park(m,75, 1.75,-1)
    elif choice == 'kturn':
        print('turning around...')
        k_turn(75,2.25,-1)
    elif choice == 'grayfollow':
        print('Following a line using the ADC grayscale sensor')
        gray_follow_line(0)
        
    elif choice == 'camerafollow':
        print('Following a line using the Camera and OpenCV')
        cv_follow_line(0)
    else:
        print('did nothing...')
        pass