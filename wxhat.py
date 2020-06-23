#! /usr/bin/python3
import time
import csv
import RPi.GPIO as GPIO
from ads_hat import ADS_I2C
from multiprocessing import Process, Value, Manager
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

thp = THPSensors()

gps_recent_msgs = Manager().dict()

def write_sample(channel):
    new_row = [ # TODO: this is irresponsible but clever, dictionaries are not usually ordered, but the return values for these functions statically order them
            ads_code.value,
            *thp.get_pressure().values(), 
            *thp.get_temperature().values(),
            *thp.get_humidity().values(),
            gps_recent_msgs.get('nav_pvt', None)
    ]

    print (new_row)
    with open('wxhat_results.csv', 'a') as csv_file: 
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(new_row)

def gps_startup():
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

    nav_msg_msg = NEO_M8P_MSG(*CFG_MSG) 
    nav_msg_msg.length = 3 # there are multiple lengths

    nav_msg_msg.set_payload([
        *(NAV_PVT[:2]),
        0x01 # rate in Hz
    ])

    gps_port.send(nav_msg_msg)

    time.sleep(1)
    
    gps_proc = Process(target=gps_port.receive_ubx_cont, args=(gps_recent_msgs,))
    gps_proc.start()   


def run_hat():
    neo = Pixels()
    neo.set_pixel(0, STATUS_STARTUP)

    with open('wxhat_results.csv', 'w') as csv_file: 
        csv_writer = csv.writer(csv_file)
        header = ['ADS Code', 'BMP388 Pressure', 'BME280 Pressure', 'BMP388 Temperature', 'BME280 Temperature', 'SHT31D Temperature', 'BME280 Humidity', 'SHT31D Humidity', 'GPS NAVPVT MSG']
        csv_writer.writerow(header)

    # start ADS as thread
    p = Process(target=ads.get_rtd_temp_cont, args=(ads_code,))
    p.start()

    
    # start GPS as a thread
    gps_startup()

    # start IMU as thread

    # start THPSensors 

    GPIO.setup(26, GPIO.IN)

    GPIO.add_event_detect(26, GPIO.RISING, callback=write_sample, bouncetime=200)

    # while(True):
    #   time.sleep(0.1)
    _ = input('Press Enter to stop')

if __name__ == '__main__':
    run_hat()
