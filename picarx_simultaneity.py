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
        return self.messages
    
    def write(self, msg):
        self.message = msg


def sensor_producer(in_bus, delay):
    lock = Lock()
    s = Sensors()
    while True:
        with lock:
            adcs = s.get_adc_value()
        in_bus.write(adcs)
        time.sleep(delay)
        
    
    
def interpreter_cp(in_bus, out_bus, delay):
    i = Interpreters()
    while True:
        logging.info("in_bus: {0}".format(in_bus.read))
        if in_bus.read != None:
            [position, adcs] = i.get_grayscale_value(in_bus.read)
            out_bus.write(position)
            logging.info("position values: {0}".format(position))
            time.sleep(delay)
        else:
            time.sleep(delay)
    
def controller_consumer(out_bus, delay, speed):
    c = Controllers()
    m = Motors()
    while True:
        if out_bus.read != None:
            c.line_following(m, position, speed)
            time.sleep(delay)
        else:
            time.sleep(delay)
            
def simultaneity(speed):
    logging.info("Starting bus grayscale line chasing")

    sensor_delay = 0.2
    interpreter_delay = 0.2
    controller_delay = 0.2
    in_bus = DataBus()
    out_bus = DataBus()
    
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        bus_sensor = executor.submit(sensor_producer, in_bus, sensor_delay)
        bus_interpreter = executor.submit(interpreter_cp, in_bus, out_bus, interpreter_delay)
        bus_controller = executor.submit(controller_consumer, in_bus, controller_delay, speed)
            
            
        
if __name__ == "__main__":
    simultaneity(0)
