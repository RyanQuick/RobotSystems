#!/usr/bin/python3

import time
import concurrent.futures
from threading import Lock
from picarx_classes import Motors, Sensors, Interpreters, Controllers

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


class DataBus:
    def __init__(self):
        self.message = 0
        
    def read(self):
        return self.message
    
    def write(self, msg):
        self.message = msg
    
    def test(self):
        print(self.read())
        self.write('Testing read/write')
        print(self.read())


def sensor_producer(s, in_bus, delay):
    lock = Lock()
    while True:
        with lock:
            adcs = s.get_adc_value()
        in_bus.write(adcs)
        time.sleep(delay)
        
    
    
def interpreter_cp(i, in_bus, out_bus, delay):
    while True:
        # logging.info("in_bus: {0}".format(in_bus.read()))
        if in_bus.read() != None:
            position = i.get_grayscale_value(in_bus.read())
            out_bus.write(position)
            # logging.info("out bus: {0}".format(out_bus.read()))
            time.sleep(delay)
        else:
            time.sleep(delay)
    
def controller_consumer(c, out_bus, delay, speed):
    while True:
        if out_bus.read() != None:
            c.line_following(out_bus.read(), speed)
            time.sleep(delay)
        else:
            time.sleep(delay)
            
def simultaneity(m,s,i,c, speed):

    sensor_delay = 0.2
    interpreter_delay = 0.2
    controller_delay = 0.2
    in_bus = DataBus()
    out_bus = DataBus()
    
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        bus_sensor = executor.submit(sensor_producer, s, in_bus, sensor_delay)
        bus_interpreter = executor.submit(interpreter_cp, i, in_bus, out_bus, interpreter_delay)
        bus_controller = executor.submit(controller_consumer, c, out_bus, controller_delay, speed)
    
    logging.info("made it here")
    logging.info(bus_controller)
    # eSensor.result()
    bus_sensor.result()
    bus_interpreter.result()
    bus_controller.result()



        
if __name__ == "__main__":
    b = DataBus()
    b.test()
