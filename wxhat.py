#! /usr/bin/python3
import time
import RPi.GPIO as GPIO
from ads_hat import ADS_I2C
from multiprocessing import Process, Value
from thp_sensors import THPSensors
from neopixel_hat import Pixels, PixelError, RED, GREEN, BLUE, WHITE, YELLOW
from neo_m8p.neo_m8p_hat import NEO_M8P_HAT, NEO_M8P_MSG
from neo_m8p.nav_consts import * 

GPIO.setmode(GPIO.BCM)

STATUS_STARTUP = RED
STATUS_WORKING = GREEN
STATUS_WARNING = YELLOW

ads = ADS_I2C()
ads_code = Value('i', 0)

def write_sample(channel):
    print(ads_code.value)
    print("got here")

def run_hat():
    neo = Pixels()
    neo.set_pixel(0, STATUS_STARTUP)

    # start ADS as thread
    p = Process(target=ads.get_rtd_temp_cont, args=(ads_code,))
    p.start()

    # start GPS as thread
    gps_port = NEO_M8P_HAT('/dev/serial0', 9600) 
    timepulse_msg = NEO_M8P_MSG(*CFG_TP5)
    

    # all multibyte values are little endian unless otherwise stated
    timepulse_msg.set_payload([
        0x00, # timepulse selection
        0x00, # message version                                                                                                                                      
        0x00, # reserved                                                                                                                                             
        0x00, # reserved                                                                                                                                             
        0x00, 0x00, # Antenna delay                                                                                                                                  
        0x00, 0x00, # RF delay                                                                                                                                       
        0x01, 0x00, 0x00, 0x00, # frequency in Hz                                                                                                                    
        0x01, 0x00, 0x00, 0x00, # frequency in Hz when GPS time is locked in
        0xff, 0xff, 0xff, 0x7f, # 50% pulse width          
        0xff, 0xff, 0xff, 0x7f, # 50% pulse width when locked to GPS time
        0x00, 0x00, 0x00, 0x00, # user configurable delay
        0b01101001, 0x00, 0x00, 0x00  # flags                                                                                                                    
    ])                                                                                                                                                                                                                                                                                                                        
    gps_port.send(timepulse_msg)                                                                                                                                                                                                                                                                                              

    time.sleep(1)
    
    # start IMU as thread

    # start THPSensors 

    GPIO.setup(26, GPIO.IN)

    GPIO.add_event_detect(26, GPIO.RISING, callback=write_sample, bouncetime=200)

    # while(True):
    #   time.sleep(0.1)
    _ = input('Press Enter to stop')

if __name__ == '__main__':
    run_hat()
