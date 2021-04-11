#!/usr/bin/python3

import picarx_improved

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
    picarx_improved.forward(speed)
    print("direction: ",direction,"speed: ", speed)
    
if __name__ == "__main__":
    picarx_improved.dir_servo_angle_calibration(30)
    for i in range(1000):
        move_forward(0,100)
        