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

    def __init__(self, port=I2C_PORT, addr=ADDR):
        self.bus = SMBus(port) 
        self.addr = addr

    def get_rtd_temp(self):
        '''
        gets the temperature of a 2-pin RTD thermistor 
        base off of the pseudocode from p.50 and the configuration of the circuit on p.56 Table 27
        '''
        ### do a soft reset of config ###
        reset_cmd = 0x06
        self.bus.write_byte(self.addr, reset_cmd) 
        time.sleep(0.1)

        ### set registers ###
        reg_cmds = [
                # (reg, reg_val)
                (0x40, 0x36),
                (0x44, 0x0A),
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

        ### start read ### 
        read_cmd = 0x10
        while True: 
            time.sleep(1)
            data = self.bus.read_i2c_block_data(self.addr, read_cmd, 3)
            hexs = [hex(byte).strip('0x').zfill(2) for byte in data]
            # TODO: this is the most consistent pattern and seems to react to temperature 
            hexs_endian = [hexs[1], hexs[2], hexs[0]]
            hex_str = ''.join(hexs_endian)
            code = int(hex_str, 16)
            decode = (code / math.pow(2,24) )*self.R_REF/self.GAIN # see equation at p#58 of ADS docs
            print(decode) 

    def get_adc_temp(self):
        '''
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

        ### start command ###
        start_sync = 0x08
        self.bus.write_byte(self.addr, start_sync) 
        time.sleep(0.1)

        ### start read ### 
        while True:
            time.sleep(1)
            rdata = 0x10 # start a read
            data = self.bus.read_i2c_block_data(self.addr, rdata, 3) # 24-bit, so 3 bytes of conversion results
            hexs = [hex(byte).strip('0x').zfill(2) for byte in data]
            print(hexs) # TODO: this is garbage

            # convert the 14-bit, left-justified binary to a 2's compliment temperature
            temp_code = ''.join(hexs)[-4:]
            fourteen_bits = int(bin(int(temp_code, 16))[-14:], 2) # get rid of everything except the last 14 bits 

            if fourteen_bits >= 1<<13: # 2's compliment
                fourteen_bits -= 1<<14
            adc_temp = fourteen_bits*self.ADC_TEMP_STEP # apply step value 
            print(adc_temp)

if __name__ == '__main__':
    ads = ADS_I2C()
    ads.get_adc_temp()
    ads.get_rtd_temp()
