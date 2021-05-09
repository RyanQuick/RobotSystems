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
from picarx_simultaneity import simultaneity
from picarx_multimodal import multimodal
import time
import cv2

def move_forward(m,speed,length,angle):
    m.set_dir_servo_angle(angle)
    m.forward(speed)
    time.sleep(length)
    m.stop()
    
def pl_park(m, speed, length, direction=-1):
    m.set_dir_servo_angle(direction*40)
    m.backward(speed)
    time.sleep(length*.50)
    m.set_dir_servo_angle(-direction*40)
    m.backward(speed)
    time.sleep(length*.50)
    
    
def k_turn(m, speed, length, direction=-1):
    m.set_dir_servo_angle(direction*40)
    m.forward(speed)
    time.sleep(length*.50)
    m.set_dir_servo_angle(-direction*40)
    m.backward(speed)
    time.sleep(length*.50)
    m.set_dir_servo_angle(direction*40)
    m.forward(speed)
    time.sleep(length*.50)
    
# def test(m):
#     m.set_dir_servo_angle(-40)
#     m.camera_servo_pin1.angle(-40)
#     m.camera_servo_pin2.angle(-40)
#     time.sleep(1)
#     m.set_motor_speed(1, 1)
#     m.set_motor_speed(2, 1)
#     m.set_dir_servo_angle(40)
#     m.camera_servo_pin1.angle(40)
#     m.camera_servo_pin2.angle(40)
#     time.sleep(1)

def gray_follow_line(m,s,i,c, speed):    
    while True:        
        position = i.get_grayscale_value(s.get_adc_value())
        # logging.info("Relative Position: {0}".format(position))
        c.line_following(position, speed)
        
def wall_stop(s,c):
    while True: 
        distance = s.get_distance()
        logging.info("Checking for walls: {0}".format(distance))
        c.wall_checking(distance)

def cv_follow_line(cvs, c, speed):
    while True:
        frame = cvs.start_cv()
        edges = cvs.look_for_color(frame)
        cropped_edges = cvs.crop_video(edges)
        line_segments = cvs.detect_line_segments(cropped_edges)
        path = cvs.average_slope_intercept(cvs, frame, line_segments)
        # cvs.make_points(CVSteering, frame, line)
        new_angle = cvs.steering_angle(path)
        adjusted_angle = cvs.steering_angle_adjustment(new_angle, turn_limit = 30)
        c.line_following(adjusted_angle/-30, speed)

    

if __name__ == "__main__":
    m = Motors()
    s = Sensors()
    i = Interpreters()
    c = Controllers(m)
    cvs = CVSteering()
    choice = input('Choose an action to take: (park, forward, kturn, \
                   grayfollow, camerafollow, grayfollow2, grayfollow3, wallstop)')
    if choice == 'forward':
        print('moving forward...')
        move_forward(m,50,2,0)
    elif choice == 'park':
        print('parking...')
        pl_park(m,75, 1.75,-1)
    elif choice == 'kturn':
        print('turning around...')
        k_turn(m,75,2.25,-1)
    elif choice == 'grayfollow':
        print('Following a line using the ADC grayscale sensor')
        gray_follow_line(m,s,i,c,0)
    elif choice == 'camerafollow':
        print('Following a line using the Camera and OpenCV')
        cv_follow_line(cvs, c, 0)
    elif choice == 'grayfollow2':
        print('Following a line using bus & grayscale sensor')
        simultaneity(m,s,i,c,0)
    elif choice == 'grayfollow3':
        print('Following a line using RossROS & grayscale sensor')
        multimodal(m,s,i,c,0)
    elif choice == 'wallstop':
        print('Following a line using RossROS & grayscale sensor')
        wall_stop(s,c)
    else:
        print('did nothing...')
        pass