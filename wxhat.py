#! /usr/bin/python3
import time
import csv
import RPi.GPIO as GPIO
import board
import digitalio
from ads_hat import ADS_I2C
from multiprocessing import Process, Value, Manager
from thp_sensors import THPSensors
from neopixel_hat import Pixels, PixelError, RED, GREEN, BLUE, WHITE, YELLOW
from neo_m8p.neo_m8p_hat import NEO_M8P_HAT, NEO_M8P_MSG
from neo_m8p.nav_consts import * 
from bno080_i2c import BNO080_I2C

GPIO.setmode(GPIO.BCM)

STATUS_STARTUP = RED
STATUS_WORKING = GREEN
STATUS_WARNING = YELLOW

ads = ADS_I2C()
ads_code = Value('i', 0)

thp = THPSensors()

gps_recent_msgs = Manager().dict()

imu_recent_reports = Manager().dict()

def write_sample(channel):
    new_row = [ # TODO: this is irresponsible but clever, dictionaries are not usually ordered, but the return values for these functions statically order them
            ads_code.value,
            *thp.get_pressure().values(), 
            *thp.get_temperature().values(),
            *thp.get_humidity().values(),
            gps_recent_msgs.get('nav_pvt', None),
            BNO080_I2C.parse_rep(imu_recent_reports.get(BNO080_I2C.SENSOR_REPORTID_ROT, [None])[-1]), # the last in the list is the most recent
            BNO080_I2C.parse_rep(imu_recent_reports.get(BNO080_I2C.SENSOR_REPORTID_ACC, [None])[-1])
            # imu_recent_reports.get(BNO080_I2C.GET_TIME_REFERENCE, [None])[-1] # available if useful
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

def imu_start():
    # reset to start with a clean buffer
    rst = digitalio.DigitalInOut(board.D22)
    rst.direction = digitalio.Direction.OUTPUT
    rst.value = False
    time.sleep(1)
    rst.value = True
    time.sleep(1)

    imu = BNO080_I2C(0x4a, 3)
    imu.get_shtp_errors()
    imu_inf = imu.get_prod_inf()
    imu.start_rot(1) 
    imu.start_acc(1)
    running_report_types = [imu.SENSOR_REPORTID_ACC, imu.SENSOR_REPORTID_ROT]
    imu_proc = Process(target=imu.get_report_cont, args=(running_report_types, 0.5, imu_recent_reports))
    imu_proc.start()

def run_hat():
    neo = Pixels()
    neo.set_pixel(0, STATUS_STARTUP)

    with open('wxhat_results.csv', 'w') as csv_file: 
        csv_writer = csv.writer(csv_file)
        header = ['ADS Code', 'BMP388 Pressure', 'BME280 Pressure', 'BMP388 Temperature', 'BME280 Temperature', 'SHT31D Temperature', 'BME280 Humidity', 'SHT31D Humidity', 'GPS NAVPVT MSG', 'IMU ROT REPORT', 'IMU ACC REPORT']
        csv_writer.writerow(header)

    # start ADS as thread
    p = Process(target=ads.get_rtd_temp_cont, args=(ads_code,))
    p.start()

    
    # start GPS as a thread
    gps_startup()

    # start IMU as thread
    imu_start()

    # start THPSensors 

    GPIO.setup(26, GPIO.IN)

    GPIO.add_event_detect(26, GPIO.RISING, callback=write_sample, bouncetime=200)

    # while(True):
    #   time.sleep(0.1)
    _ = input('Press Enter to stop')

if __name__ == '__main__':
    run_hat()
