#!/usr/bin/python3
from smbus2 import SMBus, i2c_msg
import time
import board
import digitalio

class BNO080_I2C:
    
    # I2C packet read delay in microseconds
    I2CDELAY            = 400
    # Packets can be up to 32k.
    MAX_PACKET_SIZE     = 32762 
    # This is in words, we only care about the first 9 (Qs, range, etc)
    MAX_METADATA_SIZE   = 9
    # SHTP cmd channel: byte-0=command, byte-1=parameter, byte-n=parameter
    CHANNEL_COMMAND     = 0
    # SHTP exec channel: write 1=reset, 2=on, 3=sleep; read 1=reset complete
    CHANNEL_EXECUTABLE  = 1
    # Sensor Hub control channel for sensor config commands and responses
    CHANNEL_CONTROL     = 2
    # Input Sensor reports only sends data from sensor to host
    CHANNEL_REPORTS     = 3
    # Wake Input Sensor reports sends data from wake sensors to host
    CHANNEL_WAKE_REPORTS = 4
    # Gyro rotation vector in extra channel to allow prioritization
    CHANNEL_GYRO        = 5
    # Control channel commands (BNO8X datasheet figure 1-30)
    COMMAND_RESPONSE    = 0xF1
    COMMAND_REQUEST     = 0xF2
    FRS_READ_RESPONSE   = 0xF3  # Flash Record System read response
    FRS_READ_REQUEST    = 0xF4  # Flash Record System read request
    FRS_WRITE_RESPONSE  = 0xF5  # Flash Record System write response
    FRS__WRITE_DATA     = 0xF6  # Flash Record System write data
    FRS__WRITE_REQUEST  = 0xF7  # Flash Record System write request
    PRODUCT_ID_RESPONSE = 0xF8
    PRODUCT_ID_REQUEST  = 0xF9
    GET_TIME_REFERENCE  = 0xFB 
    GET_FEATURE_RESPONSE= 0xFC
    SET_FEATURE_COMMAND = 0xFD
    GET_FEATURE_REQUEST = 0xFE
    #All the different sensors and features we can get reports from
    #These are used when enabling a given sensor
    SENSOR_REPORTID_ACC = 0x01 # Accelerometer
    SENSOR_REPORTID_GYR = 0x02 # Gyroscope
    SENSOR_REPORTID_MAG = 0x03 # Magnetometer
    SENSOR_REPORTID_LIN = 0x04 # Linear Acceleration
    SENSOR_REPORTID_ROT = 0x05 # Rotation Vector
    SENSOR_REPORTID_GRA = 0x06 # Gravity
    SENSOR_REPORTID_GAM = 0x08 # Game Rotation Vector
    SENSOR_REPORTID_GEO = 0x09 # Geomagnetic Rotation
    SENSOR_REPORTID_TAP = 0x10 # Tap Detector
    SENSOR_REPORTID_STP = 0x11 # Step Counter
    SENSOR_REPORTID_STA = 0x13 # Stability Classifier
    SENSOR_REPORTID_PER = 0x1E # Personal Activity Classifier

    def __init__(self, addr, port): 
        self.addr = addr
        self.bus = SMBus(port)
        self.sequence = [0]*5

    @classmethod
    def _i2c_delay(cls):
        time.sleep(cls.I2CDELAY/1000000)

    def start_rot(self):
        pass

    def start_calib(self):
        pass

    def get_shtp_errors(self):
        self.send_shtp(self.CHANNEL_COMMAND, [0x01])
        res_head, res_data = self.receive_shtp_until(self.CHANNEL_COMMAND, 0x01)
        return res_data[1:]

    def get_prod_inf(self):
        self.send_shtp(self.CHANNEL_CONTROL, [self.PRODUCT_ID_REQUEST])
        res_head, res_data = self.receive_shtp_until(self.CHANNEL_CONTROL, self.PRODUCT_ID_RESPONSE)
        return res_data

    def send_shtp(self, channel, data):
        self.sequence[channel] += 1
        packetlen = len(data)+4
        packet = [
                packetlen & 0xFF,
                (packetlen >> 8) & 0xFF, 
                channel,
                self.sequence[channel],
                *data
        ]

        # TODO: add to debug log
        # print("Sending: ")
        # print(print_hex(packet))

        write = i2c_msg.write(self.addr, packet)
        write.flags = 0x0000
        self.bus.i2c_rdwr(write)

    def receive_shtp_until(self, chan_type, res_type):
        res_head, res_data = self.receive_shtp()
        count = 0 
        while (res_head[2] != chan_type or res_data[0] != res_type) and count < 3: 
            self._i2c_delay()
            res_head, res_data = self.receive_shtp()
            count += 1
        return [res_head, res_data]



    def receive_shtp(self):
        read_head = i2c_msg.read(self.addr, 4) 
        self.bus.i2c_rdwr(read_head)
        header = list(read_head)

        packetlen = (header[1] << 8) | header[0] # stitch the two length bytes together
        packetlen &= ~(1 << 15)                  # clear MSB
        datalen = packetlen - 4                  # subtract header
        subtransfer = header[1] & 0x80 != 0x00   # see if the data is not all ready at once

        read = i2c_msg.read(self.addr, packetlen)
        time.sleep(1000/1000000) # sleep 1000 us between reads
        self.bus.i2c_rdwr(read)
        msg = list(read)
        
        if len(msg) != packetlen or len(msg) == 0:
            # print ("Packet Error")
            return [None, None]

        self.sequence[msg[2]] = msg[3] # sync the sequence with the IMU

        # print("Received: ")
        # print(print_hex(msg))

        return [msg[0:4], msg[4:]]

def print_hex(hexs):
    return [hex(h) for h in hexs]

if __name__ == '__main__':
    # reset to start with a clean buffer
    rst = digitalio.DigitalInOut(board.D22)
    rst.direction = digitalio.Direction.OUTPUT
    rst.value = False
    time.sleep(1)
    rst.value = True
    time.sleep(1)

    imu = BNO080_I2C(0x4a, 3)
    errs = imu.get_shtp_errors()
    if len(errs) > 0: 
        print(f"WARNING: IMU has {len(errs)} errors: {print_hex(errs)}.")
    prod_inf = imu.get_prod_inf()
    print(f"Product info: {print_hex(prod_inf)}")
