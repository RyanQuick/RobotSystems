import time
import concurrent.futures
from threading import Lock
from picarx_classes import Motors, Sensors, Interpreters, Controllers
from rossros import Bus, ConsumerProducer, Producer, Consumer, Timer, Printer, runConcurrently

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

from logdecorator import log_on_start , log_on_end , log_on_error 


def multimodal_grayscale():
    sensor_delay = 0.2
    interpreter_delay = 0.2
    controller_delay = 0.2
    
    s = Sensors()
    i = Interpreters()
    c = Controllers()
    m = Motors()
    
    sensor_producer = Producer(s.get_adc_value(),delay = sensor_delay, name = "sensor_producer")
    interpreter_cp = ConsumerProducer(i.get_grayscale_value(),delay = interpreter_delay, name = "interpreter_cp")
    controller_consumer = Consumer(c.line_following(m, out_bus.read(), speed),delay = interpreter_delay, name = "interpreter_cp")
    runConcurrently([sensor_producer,interpreter_cp,controller_consumer])
    
    