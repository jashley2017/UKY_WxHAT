#!/usr/bin/python3
'''
NEO_M8P RTK GPS UART+I2C python driver

currently starts the timepulse at 1Hz 50% duty cycle
'''
import serial
import time
import board
import digitalio
import busio

# get GPS constants 
if __name__ == '__main__':
    from nav_consts import *
else:
    from .nav_consts import *

# TODO: replace print with proper logging

class NEO_M8P_HAT: 
    def __init__(self, port, baud=9600, i2c_port=0x42):
        self.uart = serial.Serial(
            port=port,
            baudrate=baud, 
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            timeout=1 
        )

        self.bus = busio.I2C(board.SCL, board.SDA)
        self.i2c_port = i2c_port

    def send(self, gps_msg):
        raw_msg = gps_msg.message()
        print(f"Sending 0x{raw_msg.hex()}")

        self.uart.write(raw_msg)

        # get acknowledgement
        res = self.receive_ubx()
        count = 5
        while res['class'] != 0x05 and count > 0: 
            count -= 1
            res = self.receive_ubx()

        # check message
        success = self.check_res( # these are to get all of the values in a standard format
                res,
                gps_msg.msg_cls,
                gps_msg.msg_id
        )


        # print(f"Response: {res}")
        return success

    def check_res(self, res, msg_cls, msg_id):
        if res['class'] != ACK_ACK[0]:
            print(f"Unknown message class {res['class']}")
            return False
        if res['id'] != ACK_ACK[1]:
            if res['id'] == ACK_NAK[1]:
                print(f"Message was not acknowledged")
                return False
            else: 
                print(f"Unknown message id {res['id']}")
                return False 
        if res['payload'][0] != msg_cls: 
            print(f"Wrong message class acknowledged: {res['payload'][0]}")
            return False
        if res['payload'][1] != msg_id:
            print(f"Wrong message id acknowledged: {res['payload'][1]}")
            return False
        return True


    def receive_ubx(self): 
        head = self.uart.read(1)
        while head.hex() != 'b5': 
            head = self.uart.read(1)

        header = [head, *self.uart.read(5)]

        msg_length = header[5] << 8 | header[4]
        payload = self.uart.read(msg_length)
        # TODO: check checksum here

        rec_msg = NEO_M8P_MSG(header[2], header[3], msg_length)
        rec_msg.set_payload(payload)

        return rec_msg
            # { 'class': header[2], 'id': header[3], 'payload': payload }

    def receive_ubx_cont(self, recent_msgs):
        while True:
            ubx_packet = self.receive_ubx()
            if ubx_packet['class'] == NAV_PVT[0] and ubx_packet['id'] == NAV_PVT[1]: # TODO: add more relevant messages
                recent_msgs['nav_pvt'] = ubx_packet['payload'].hex()

    def read_i2c_message(self):
        '''
        write: 

        i2c_addr << 1 | 0x00
        register (0xff) 
        i2c_addr << 1 | 0x01

        read:

        n data bytes 
        '''
        pass


class NEO_M8P_MSG:
    def __init__(self, msg_cls, msg_id, length):
        self.msg_cls = msg_cls
        self.msg_id = msg_id
        self.length = length
        self.payload = None

    def set_payload(self, payload): 
        self.payload = payload

    def message(self):
        if self.payload is None: 
            print("WARNING: must set payload before sending message")
            return None
        msg = [
            0xB5,
            0x62,
            self.msg_cls, 
            self.msg_id,
            self.length&0xff,
            (self.length>>8)&0xff,
            *self.payload
        ]
        ck_a = 0
        ck_b = 0
        for byte in msg[2:]:
            ck_a+=byte
            ck_b+=ck_a

        ck_a &= 0xff
        ck_b &= 0xff

        msg.append(ck_a)
        msg.append(ck_b)

        return bytearray(msg)
    
    def __getitem__(self, key):
        return { 'class':self.msg_cls, 'id':self.msg_id, 'payload':self.payload }[key]

if __name__ == '__main__':
    timepulse = digitalio.DigitalInOut(board.D26)
    timepulse.direction = digitalio.Direction.INPUT
    h_int = digitalio.DigitalInOut(board.D13)
    h_int.direction = digitalio.Direction.OUTPUT


    delay = 0.5
    # TODO: more than 1 serial message at a time fails
    # * might be worthwhile to disable the NMEA messages over UART to clear up the stream
    # * wait significantly longer between config messages 
    # * toggle an interrupt signal when sending message
    gps_port = NEO_M8P_HAT('/dev/serial0', 9600)

    # these do the same thing, see nav_consts.py
    # timepulse_msg = NEO_M8P_MSG(0x06, 0x31, 32)

    i2c_setup_msg = NEO_M8P_MSG(*CFG_PRT)

    i2c_setup_msg.set_payload([
        0x00, # port ID I2C = 0
        0x00, # reserved
        0x00, 0x00, # txReady pin conf (disabled) 
        0x42<<1, 0x00, 0x00, 0x00, # mode slave address
        0x00, 0x00, 0x00, 0x00, # reserved
        0x01, 0x00, # in protocol mask (inUbx)
        0x01, 0x00, # out protocol mask (outUbx)
        0x00, 0x00, # timeout not set
        0x00, 0x00 # reserved
    ])

    gps_port.send(i2c_setup_msg)

    time.sleep(1)

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

    log_msg_msg = NEO_M8P_MSG(*CFG_MSG)
    log_msg_msg.length = 3

    log_msg_msg.set_payload([
        *(INF_WARNING[:2]),
        0x01
    ])

    gps_port.send(log_msg_msg)

    time.sleep(1)

    count = 0 

    while count < 10:
        print(timepulse.value)
        time.sleep(0.5)
        count+=1

    while True:
        res = gps_port.receive_ubx()
        print(f"Class: {hex(res['class'])}, ID: {hex(res['id'])}, Payload: {res['payload'].hex()}")
