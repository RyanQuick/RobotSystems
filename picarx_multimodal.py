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


def multimodal(speed):
    sensor_delay = 0.2
    interpreter_delay = 0.2
    controller_delay = 0.2
    
    s = Sensors()
    i = Interpreters()
    c = Controllers()
    m = Motors()
    
    grayin_bus = Bus()
    grayout_bus = Bus()
    
    ultrasin_bus = Bus()
    ultrasout_bus = Bus()
    
    grayscale_producer = Producer(s.get_adc_value(),delay = sensor_delay, name = "grayscale_producer")
    grayscale_cp = ConsumerProducer(i.get_grayscale_value(),delay = interpreter_delay, name = "grayscale_cp")
    grayscale_consumer = Consumer(c.line_following(m, grayout_bus.read(), speed),delay = interpreter_delay, name = "grayscale_cp")
    
    ultras_producer = Producer(s.get_distance(), delay = sensor_delay, name = "ultras_producer")
    ultras_consumer = Consumer(c.wall_checking(m, ultrasout_bus.read()),delay = interpreter_delay, name = "ultras_cp")
    print('made it here')
    runConcurrently([grayscale_producer, grayscale_cp, grayscale_consumer, ultras_producer, ultras_consumer])
    
    