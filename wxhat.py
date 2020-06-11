#!/usr/bin/python3
'''
A Python script to combine the functionality of all of the sensors in the Raspberry Pi 4 WxHAT
'''
import board
import busio
import math
import time

import adafruit_bme280
import adafruit_bmp3xx
import adafruit_sht31d

import neopixel_hat

BME280_ADDR = 0x77
BMP388_ADDR = 0x76
SHT31D_ADDR = 0x44

class NoOp:
    ''' Dummy class to compensate for sensors that are not connecting '''
    def __init__(self): pass
    def __getattr__(self, _): return None


class WxHat:
    ''' Top-Level class to combine all of the sensors from the Hat '''
    def __init__(self):
        bus = busio.I2C(board.SCL, board.SDA)
        self.sea_level_pressure = None
        # init bme280
        try:
            self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(bus, address=BME280_ADDR)
        except:
            self.bme280 = NoOp()
            print("WARNING: could not connect bme280")

        # init bmp388
        try: 
            self.bmp388 = adafruit_bmp3xx.BMP3XX_I2C(bus, address=BMP388_ADDR)
            self.bmp388.pressure_oversampling = 8
            self.bmp388.temperature_oversampling = 2
        except:
            self.bmp388 = NoOp()
            print("WARNING: could not connect bmp388")

        # init sht31d
        try:
            self.sht31d = adafruit_sht31d.SHT31D(bus, address=SHT31D_ADDR)
        except:
            self.sht31d = NoOp()
            print("WARNING: could not connect sht31d")

    def set_sea_level(self, sea_level):
        self.sea_level_pressure = sea_level
        self.bme280.sea_level_pressure = sea_level
        self.bmp388.sea_level_pressure = sea_level

    def get_altitude(self): 
        if self.sea_level_pressure is None: 
            print("WARNING: cannot obtain sea level from pressure without sea_level_pressure being set.")

        else: 
            return { "bmp388": self.bmp388.altitude, "bme280": self.bme280.altitude }

    def get_pressure(self):
        return { "bmp388": self.bmp388.pressure, "bme280": self.bme280.pressure,  } 

    def get_temperature(self):
        return { "bmp388": self.bmp388.temperature, "bme280": self.bme280.temperature, "sht31d": self.sht31d.temperature } 

    def get_humidity(self):
        return {"bme280": self.bme280.humidity, "sht31d": self.sht31d.relative_humidity } 


if __name__ == '__main__':
    status_leds = neopixel_hat.Pixels()
    status_leds.set_pixel(0, neopixel_hat.YELLOW)
    pihat = WxHat()
    pihat.set_sea_level(1013.25)
    while True: 
        status_leds.set_pixel(0, neopixel_hat.OFF)
        print(f"Temps: {pihat.get_temperature()}")
        print(f"Hums: {pihat.get_humidity()}")
        print(f"Press: {pihat.get_pressure()}")
        print(f"Alts: {pihat.get_altitude()}")
        time.sleep(0.5)
        status_leds.set_pixel(0, neopixel_hat.GREEN) # green every time new data
        time.sleep(0.5)
