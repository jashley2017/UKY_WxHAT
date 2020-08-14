#!/usr/bin/python3 
'''
Python I2C driver for ADS122C04

docs: http://www.ti.com/lit/ds/symlink/ads122c04.pdf
'''

import math
import time
import board
import digitalio
import struct 
from multiprocessing import Lock, Value
from smbus2 import SMBus, i2c_msg

class ADS_I2C():
    '''
    WARNING: does not yet work
    Python I2C driver class for ADS122C04
    '''

    # class constants 
    ADDR = 0x40
    I2C_PORT = 3
    R_REF = 1650
    ADC_TEMP_STEP = 0.0312
    GAIN = 8
    SAMPLE_RATES = {
        20: 0b000,
        45: 0b001,
        90: 0b010,
        175: 0b001,
        330: 0b100,
        600: 0b101,
        1000: 0b110
    }

    def __init__(self, port=I2C_PORT, addr=ADDR, sample_rate=20):
        self.bus = SMBus(port) 
        self.addr = addr
        self.sample_rate = sample_rate

    def setup_rtd(self):
        '''
        sets up the 2-pin RTD thermistor configuration
        based off of the pseudocode from p.50 and the configuration of the circuit on p.56 Table 27
        '''
        ### do a soft reset of config ###
        reset_cmd = 0x06
        self.bus.write_byte(self.addr, reset_cmd) 
        time.sleep(0.1)

        ### set registers ###
        reg_cmds = [
                # (reg, reg_val)
                (0x40, 0x36),
                (0x44, 0x0A | (self.SAMPLE_RATES[self.sample_rate] << 5)),
                (0x48, 0x56),
                (0x4c, 0x80)
                ]
        for reg, reg_data in reg_cmds:
            self.bus.write_byte_data(self.addr, reg, reg_data)
            time.sleep(0.1)

        ### read back the regs for sanity ###
        reg_read_cmds = [
                # reg
                0x20,
                0x24,
                0x28,
                0x2c
                ]
        config_regs = []
        for read_cmd in reg_read_cmds: 
            read = self.bus.read_byte_data(self.addr, read_cmd, 1) 
            config_regs.append(hex(read))
        print(f"Config Registers: {config_regs}")

        ### start command ###
        start_sync = 0x08
        self.bus.write_byte(self.addr, start_sync) 
        time.sleep(0.1)


    def get_rtd_temp(self):
        self.setup_rtd()
        ### start read ### 
        while True: 
            time.sleep(1/(2*self.sample_rate)) # nyquist, sample at 2x the other frequency and never miss a data point
            hexs = self.rdata()
            if hexs: 
                hex_str = ''.join(hexs)
                code = int(hex_str, 16)
                return code

    def get_rtd_temp_cont(self, code=None):
        '''
        gets rtd temperature continuously 
        '''
        
        self.setup_rtd()
        ### start read ### 
        while True: 
            time.sleep(1/(2*self.sample_rate)) # nyquist, sample at 2x the other frequency and never miss a data point
            hexs = self.rdata()
            if hexs: 
                hex_str = ''.join(hexs)
                if code is not None:
                    code.value = int(hex_str, 16)
                else:
                    print(int(hex_str, 16))

    def get_adc_temp(self):
        '''
        WARNING: GARBAGE DATA, DOES NOT CURRENTLY WORK
        gets the ADC internal temp
        currently garbage data, configuration based on p.30 and table 30 
        '''
        ### do a soft reset of config ###
        reset_cmd = 0x06
        self.bus.write_byte(self.addr, reset_cmd) 
        time.sleep(0.1)

        reg_cmds = [
                (0x40, 0x00),
                (0x44, 0x09),
                (0x48, 0x55),
                (0x4c, 0x70)
                ]

        for reg, reg_data in reg_cmds:
            self.bus.write_byte_data(self.addr, reg, reg_data)
            time.sleep(0.1)

        ### start command ###
        start_sync = 0x08
        self.bus.write_byte(self.addr, start_sync) 
        time.sleep(0.1)

        ### start read ### 
        while True:
            # TODO: garbage output from the ADC
            time.sleep(0.02)
            hexs = self.rdata()
            if hexs:
                temp_bytes = int(''.join(hexs[0:2]), 16)
                # convert the 14-bit, left-justified binary to a 2's compliment temperature
                fourteen_bits = temp_bytes & 0x3fff  # get rid of everything except the last 14 bits 

                if fourteen_bits >= 1<<13: # 2's compliment
                    fourteen_bits -= 1<<14
                adc_temp = fourteen_bits*self.ADC_TEMP_STEP # apply step value 
                print(adc_temp)

    def rdata(self):
        read_cmd = 0x10
        drdy_cmd = 0x28
        drdy = (self.bus.read_byte_data(self.addr, drdy_cmd, 1) & 0x80)
        hexs = []
        if (drdy):
            data = self.bus.read_i2c_block_data(self.addr, read_cmd, 3)
            hexs = [hex(byte).strip('0x').zfill(2) for byte in data]
            return hexs

if __name__ == '__main__':
    ads = ADS_I2C()
    # ads.get_adc_temp()
    ads.get_rtd_temp_cont()
