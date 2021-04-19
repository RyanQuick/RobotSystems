#!/usr/bin/python3

import time
from math import tan, pi

try :
    from ezblock import __reset_mcu__
    from ezblock import *
    
    __reset_mcu__()
    time.sleep(0.01)
except ImportError :
    print ("Simulator")
    from sim_ezblock import *


import logging
logging_format = "%(asctime) s : %(message) s " 
logging.basicConfig(level = logging.INFO) #format = logging_format, level = logging.INFO, )#datefmt ="% H :% M :% S ")

# logging.getLogger().setLevel(logging.DEBUG) 
# comment out this line to remove debugging comments
# logging.debug (message) Use this line to print debugging info

from logdecorator import log_on_start , log_on_end , log_on_error 
# Add these lines to the start of functions
# @log_on_start ( logging . DEBUG , " Message when function starts ") 
# @log_on_error ( logging . DEBUG , " Message when function encounters an error before completing ") 
# @log_on_end ( logging . DEBUG , " Message when function ends successfully ")


class Motors:
    
    
    def __init__(self):
        self.PERIOD = 4095
        self.PRESCALER = 10
        self.TIMEOUT = 0.02
        
        self.dir_servo_pin = Servo(PWM('P2'))
        self.camera_servo_pin1 = Servo(PWM('P0'))
        self.camera_servo_pin2 = Servo(PWM('P1'))
        self.left_rear_pwm_pin = PWM("P13")
        self.right_rear_pwm_pin = PWM("P12")
        self.left_rear_dir_pin = Pin("D4")
        self.right_rear_dir_pin = Pin("D5")
        

        
        self.Servo_dir_flag = 1
        self.dir_cal_value = -18
        self.cam_cal_value_1 = 5
        self.cam_cal_value_2 = 10
        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = [1, -1]
        self.cali_speed_value = [0, 0]
        
        self.steering_dir_val = 0

        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)
        
        import atexit
        atexit.register(self.stop)

    def set_motor_speed(self, motor, speed):
        # global cali_speed_value,cali_dir_value
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        #if speed != 0:
            #speed = int(speed /2 ) + 50
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
            
            
    def motor_speed_calibration(self, value):
        # global cali_speed_value,cali_dir_value
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0
    
    def motor_direction_calibration(self, motor, value):
        # 0: positive direction
        # 1:negative direction
        # global cali_dir_value
        motor -= 1
        if value == 1:
            self.cali_dir_value[motor] = -1*self.cali_dir_value[motor]
    
    
    def dir_servo_angle_calibration(self, value):
        # global dir_cal_value
        self.dir_cal_value = value
        self.set_dir_servo_angle(self.dir_cal_value)
        # dir_servo_pin.angle(dir_cal_value)
    
    def set_dir_servo_angle(self, value):
        #global dir_cal_value
        self.steering_dir_val = value
        self.dir_servo_pin.angle(value+self.dir_cal_value)
    
    def camera_servo1_angle_calibration(self, value):
        # global cam_cal_value_1
        self.cam_cal_value_1 = value
        self.set_camera_servo1_angle(self.cam_cal_value_1)
        # camera_servo_pin1.angle(cam_cal_value)
    
    def camera_servo2_angle_calibration(self, value):
        # global cam_cal_value_2
        self.cam_cal_value_2 = value
        self.set_camera_servo2_angle(self.cam_cal_value_2)
        # camera_servo_pin2.angle(cam_cal_value)
    
    def set_camera_servo1_angle(self, value):
        #global cam_cal_value_1
        self.camera_servo_pin1.angle(-1 *(value+self.cam_cal_value_1))
    
    def set_camera_servo2_angle(self, value):
        # global cam_cal_value_2
        self.camera_servo_pin2.angle(-1 * (value+self.cam_cal_value_2))
    

    
    def set_power(self, speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed) 
    
    def backward(self, speed):
        if self.steering_dir_val != 0:
            # print('turning angle:',theta)
            turn_radius = 9.5/tan((self.steering_dir_val* pi/ 180))
            # print('turn_radius: ',turn_radius)
            angle_vel = speed/turn_radius
            # print('angle_vel:',angle_vel)
            motor_speed = [angle_vel*(turn_radius-5.85), angle_vel*(turn_radius+5.85)]
            motor_speed = [motor_speed[0]/max(motor_speed)*speed, motor_speed[1]/max(motor_speed)*speed]
    
        else:
            motor_speed = [speed,speed]
        
        
        self.set_motor_speed(1, motor_speed[0])
        self.set_motor_speed(2, motor_speed[1])
        # print("left speed", motor_speed[0],"right speed", motor_speed[1],)
    
    def forward(self, speed):
        if self.steering_dir_val != 0:
            
            turn_radius = 9.5/tan(self.steering_dir_val* pi/ 180)
            angle_vel = speed/turn_radius
            motor_speed = [angle_vel*(turn_radius+5.85), angle_vel*(turn_radius-5.85)]
            motor_speed = [motor_speed[0]/max(motor_speed)*speed, motor_speed[1]/max(motor_speed)*speed]
        else:
            motor_speed = [speed,speed]
        
        
        self.set_motor_speed(1, -1*motor_speed[0])
        self.set_motor_speed(2, -1*motor_speed[1])
        # print("left speed", (-1*motor_speed[0]),"right speed", (-1*motor_speed[1]),)
    
    def stop(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)
    
    
    

         
    def test(self):
        self.camera_servo1_angle_calibration(5)
        self.camera_servo2_angle_calibration(10)
        self.dir_servo_angle_calibration(-10) 
        self.set_dir_servo_angle(-40)
        time.sleep(1)
        self.set_dir_servo_angle(0)
        time.sleep(1)
        self.set_motor_speed(1, 1)
        self.set_motor_speed(2, 1)
        self.camera_servo_pin1.angle(0)
        self.camera_servo_pin2.angle(0)
        time.sleep(1)
        self.camera_servo_pin1.angle(-40)
        self.camera_servo_pin2.angle(-40)
    
    def manual_motor_shutdown(self):
        self.stop()
        
    # import atexit
    # atexit.register(self.stop)



class Sensors:
    def __init__(self):
        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

    # def Get_distance(self):
    #     timeout=0.01
    #     trig = Pin('D8')
    #     echo = Pin('D9')
    
    #     trig.low()
    #     time.sleep(0.01)
    #     trig.high()
    #     time.sleep(0.000015)
    #     trig.low()
    #     pulse_end = 0
    #     pulse_start = 0
    #     timeout_start = time.time()
    #     while echo.value()==0:
    #         pulse_start = time.time()
    #         if pulse_start - timeout_start > timeout:
    #             return -1
    #     while echo.value()==1:
    #         pulse_end = time.time()
    #         if pulse_end - timeout_start > timeout:
    #             return -2
    #     during = pulse_end - pulse_start
    #     cm = round(during * 340 / 2 * 100, 2)
    #     #print(cm)
    #     return cm
    
    def get_adc_value(self):
        adc_value_list = []
        adc_value_list.append(self.S0.read())
        adc_value_list.append(self.S1.read())
        adc_value_list.append(self.S2.read())
        return adc_value_list
    
    
class Interpreters:
    def __init__(self):
        self.sensitivity = 200
        self.polarity = 1 # Means black line
        
    def getGrayscaleValue(self, adcs):
        if abs(adcs[0] - adcs[2]) > self.sensitivity:
            if adcs[0] < adcs[2]:
                if adcs[0] + abs((adcs[2]-adcs[0])/4) > adcs[1]:
                    rob_pos = .5 * self.polarity   
                else:
                    rob_pos = 1* self.polarity
            else:
                if adcs[2]+abs((adcs[2]-adcs[0])/4) < adcs[1]:
                    rob_pos = -1 * self.polarity   
                else:
                    rob_pos = -.5* self.polarity
        else:
            rob_pos = 0
                
                
        return rob_pos, adcs
          

class Controllers:
    def __init__(self):
        self.line_steering = -30
        
    def line_following(self, rob_pos, speed):
        logging.info("steering angle: {0}, speed: {1}".format(rob_pos*self.line_steering,speed))
        Motors().set_dir_servo_angle(rob_pos*self.line_steering)
        Motors().forward(speed)
        
        
        
if __name__ == "__main__":
    # m = Motors()
    s = Sensors()
    i = Interpreters()
    c = Controllers()
    while True:
        
        [position, adcs] = i.getGrayscaleValue(s.get_adc_value())
        # logging.info("Relative Position: {0}, adc1: {1}, adc2: {2}, adc3: {3}".format(position,adcs[0],adcs[1],adcs[2]))
        c.line_following(position, 0)
        # time.sleep(.1)
    # try:
    #     # self.dir_servo_angle_calibration(-10) 
    #     while 1:-
    #         m.test()
    # finally: 
    #     m.stop()
    
    
    
    
    
# import logging
# logging.basicConfig(level=logging.INFO)

# def hypotenuse(a, b):
#     """Compute the hypotenuse"""
#     return (a**2 + b**2)**0.5
# opp = 3
# adj = 4
# logging.info("Hypotenuse of {a}, {b} is {c}".format(a=opp, b=adj, c=hypotenuse(opp,adj)))


