#!/usr/bin/python3
'''
simple 2 pixel neopixel interface based off of preexisting neopixel library
'''
import time
import board
import digitalio
import neopixel

# TODO currently the pixel order is actually GRBW for some reason. It might be a bug in the connection or library

RED = (0,255,0,0)
GREEN = (255,0,0,0)
BLUE = (0,0,255,0)
WHITE = (0,0,0,255)

YELLOW = (255,255,0,0)
PURPLE = (0,255,255,0)
TURQUOISE = (255,0,255,0)

OFF = (0,0,0,0)

class Pixels:
    '''
    simple 2 pixel neopixel interface
    '''
    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.D18, 2, pixel_order=neopixel.RGBW )

    def set_pixel(self, pixel_num, rgbw_tuple): 
        if not isinstance(rgbw_tuple, tuple): 
            raise PixelError("RGBW must be type tuple")
        elif len(rgbw_tuple) != 4: 
            raise PixelError("RGBW value must have 4 entries")
        else: 
            self.pixels[pixel_num] = rgbw_tuple
        return 1

class PixelError(Exception):
    def __init__(self):
        pass

if __name__ == '__main__': 
    print("RGBW Neopixel Test")
    neo = Pixels()
    for i in range(10): 
        if i % 2 == 0:
            neo.set_pixel(0, RED) 
            neo.set_pixel(1, GREEN)
        else:
            neo.set_pixel(0, GREEN) 
            neo.set_pixel(1, RED) 
        time.sleep(1) 
    neo.set_pixel(0, OFF)
    neo.set_pixel(1, OFF) 
