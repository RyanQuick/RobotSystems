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


def multimodal(m,s,i,c, speed):
    sensor_delay = 0.2
    interpreter_delay = 0.2
    controller_delay = 0.2
    
        
    grayin_bus = Bus()
    grayout_bus = Bus()
    
    ultras_bus = Bus()
    
    stopsign = Bus(False)
    
    speed = Bus(initial_message = speed)
    

    
    grayscale_producer = Producer(s.get_adc_value, grayin_bus, delay = sensor_delay, termination_busses = stopsign, name = "grayscale_producer") # Nigel says this works
    
    # logging.info("Bus Value: {0}".format(i.get_grayscale_value(grayin_bus.get_message("adc_busvar"))))
    grayscale_cp = ConsumerProducer(i.get_grayscale_value, grayin_bus, grayout_bus, delay = interpreter_delay, termination_busses = stopsign, name = "grayscale_cp")
    # logging.info("Bus Value: {0}".format(grayout_bus.get_message("relative_pos")))
    grayscale_consumer = Consumer(c.line_following, (grayout_bus, speed_bus), delay = interpreter_delay, termination_busses = stopsign, name = "grayscale_consumer")
    
    ultras_producer = Producer(s.get_distance, ultras_bus, delay = sensor_delay, termination_busses = stopsign, name = "ultras_producer")
    ultras_consumer = Consumer(c.wall_checking, ultras_bus, termination_busses = stopsign, delay = interpreter_delay, name = "ultras_cp")
    logging.info("made it here")
    runConcurrently([grayscale_producer, grayscale_cp, grayscale_consumer, ultras_producer, ultras_consumer])
    
    