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
    
    
    stopsign = Bus(False)
    
    grayscale_producer = Producer(grayin_bus.set_message(s.get_adc_value(),"grayscale_in"), grayin_bus, delay = sensor_delay, termination_busses = stopsign, name = "grayscale_producer")
    logging.info("Bus Value: {0}".format(i.get_grayscale_value(grayin_bus.get_message("grayscale_in"))))
    grayscale_cp = ConsumerProducer(grayout_bus.set_message(i.get_grayscale_value(grayin_bus.get_message("grayscale_in")),"grayscale_out"), grayin_bus, grayout_bus, delay = interpreter_delay, termination_busses = stopsign, name = "grayscale_cp")
    logging.info("Bus Value: {0}".format(grayout_bus.get_message("grayscale_out")))
    grayscale_consumer = Consumer(c.line_following(m, grayout_bus.get_message("grayscale_out")[0], speed), grayout_bus, delay = interpreter_delay, termination_busses = stopsign, name = "grayscale_consumer")
    
    #ultras_producer = Producer(s.get_distance(), delay = sensor_delay, name = "ultras_producer")
    #ultras_consumer = Consumer(c.wall_checking(m, ultrasout_bus.get_message()),delay = interpreter_delay, name = "ultras_cp")
    logging.info("made it here")
    runConcurrently([grayscale_producer, grayscale_cp, grayscale_consumer])#, ultras_producer, ultras_consumer])
    
    