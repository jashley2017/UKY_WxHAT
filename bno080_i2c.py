#!/usr/bin/python3
from smbus2 import SMBus, i2c_msg
import time
import sys
import board
import digitalio

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
def delete_last_lines(n=1):
    for _ in range(n):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)

class BNO080_I2C:
    
    # I2C packet read delay in microseconds
    I2CDELAY            = 400
    # Packets can be up to 32k.
    MAX_PACKET_SIZE     = 32762 
    # This is in words, we only care about the first 9 (Qs, range, etc)
    MAX_METADATA_SIZE   = 9
    # SHTP cmd channel: byte-0=command, byte-1=parameter, byte-n=parameter
    CHANNEL_COMMAND     = 0
    # SHTP exec channel: write 1=reset, 2=on, 3=sleep, read 1=reset complete
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
    GET_TIMESTAMP_REBASE = 0xFA
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

    REPORT_SIZES = {
        SENSOR_REPORTID_ACC : 10, 
        SENSOR_REPORTID_GYR : 10, 
        SENSOR_REPORTID_MAG : 10, 
        SENSOR_REPORTID_LIN : 10, 
        SENSOR_REPORTID_ROT : 14, 
        SENSOR_REPORTID_GRA : 10, 
        SENSOR_REPORTID_GAM : 12, 
        SENSOR_REPORTID_GEO : 14, 
        SENSOR_REPORTID_TAP : 5, 
        SENSOR_REPORTID_STP : 12, 
        SENSOR_REPORTID_STA : 6, 
        SENSOR_REPORTID_PER : 4, 
        GET_TIME_REFERENCE : 5,
        GET_TIMESTAMP_REBASE: 5

    }

    def __init__(self, addr, port): 
        self.addr = addr
        self.bus = SMBus(port)
        self.sequence = [0]*5
        self.get_ad()

    @classmethod
    def _i2c_delay(cls):
        time.sleep(cls.I2CDELAY/1000000)

    def start_calib(self):
        me_calib = [
                self.COMMAND_REQUEST, 
                self.sequence[self.CHANNEL_CONTROL], 
                0x07,
                0x01,
                0x01,
                0x01,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00
        ]
        self.send_shtp(self.CHANNEL_CONTROL, me_calib)

        res_head, res_data = self.receive_shtp_until(self.CHANNEL_CONTROL, [self.COMMAND_RESPONSE])
        count = 0
        while res_data[2] != 0x07 and count < 3:
            res_head, res_data = self.receive_shtp_until(self.CHANNEL_COMMAND, [self.COMMAND_RESPONSE])
            count += 1
        if res_data[2] == 0x07 and res_data[5] != 0:
            print(f"ERROR: ME calibration set command failed: {res_data}")
        
        self.start_game_rot(10)
        self.start_mag(50)

        report_dict = self.get_report([self.SENSOR_REPORTID_MAG])
        mag_rep = report_dict.get(self.SENSOR_REPORTID_MAG, [[0x00, 0x00, 0x00]])[-1] # most recent mag report

        while mag_rep[2] & 0x03 != 0x03:
            print(mag_rep[2] & 0x03)
            time.sleep(1/50)
            delete_last_lines(1)
            report_dict = self.get_report([self.SENSOR_REPORTID_MAG])
            mag_rep = report_dict.get(self.SENSOR_REPORTID_MAG, [[0x00, 0x00, 0x00]])[-1] # most recent mag report

        print("Calibration Success!")
        return True

    def set_feature(self, sensor, features, sensitivity, rate, batch, sensor_spec):
        feat_cmd = [
            self.SET_FEATURE_COMMAND,
            sensor,
            features,
            sensitivity & 0xff,    # sensitvity LSB
            sensitivity >> 8,      # sensitivty MSB 
            rate & 0xff,           # rate LSB
            (rate & 0xff00) >> 8,    # rate
            (rate & 0xff0000) >> 16, # rate 
            (rate) >> 24,            # rate MSB  
            (batch & 0xff),           # batch rate LSB
            (batch & 0xff00) >> 8,    # batch rate
            (batch & 0xff0000) >> 16, # batch rate 
            (batch >> 24),            # batch rate MSB  
            (sensor_spec & 0xff),
            (sensor_spec & 0xff00) >> 8,
            (sensor_spec & 0xff0000) >> 16,
            (sensor_spec >> 24)
        ]
        self.send_shtp(self.CHANNEL_CONTROL, feat_cmd)
        time.sleep(0.1) # letting sensor catch up
        self.send_shtp(self.CHANNEL_CONTROL, [self.GET_FEATURE_REQUEST, sensor])
        self._i2c_delay()
        res_head, res_data = self.receive_shtp_until(self.CHANNEL_CONTROL, [self.GET_FEATURE_RESPONSE])

        # TODO: Log this on debug and check the values
        # print(f"Sensor: {res_data[1]}");
        # print(f"Feature Flags: {res_data[2]}"); 
        # print(f"Sensitivity byte: {res_data[4]}, {res_data[3]}"); 
        # print(f"Report Interval word:  {res_data[8]} {res_data[7]} {res_data[6]} {res_data[5]}"); 
        # print(f"Sensor Specific Config word: {res_data[13]}, {res_data[14]}, {res_data[15]}, {res_data[16]}");

        return True

    def start_acc(self, rate):
        return self.set_feature(self.SENSOR_REPORTID_ACC, 0, 0, rate, 0, 0)

    def start_rot(self, rate):
        return self.set_feature(self.SENSOR_REPORTID_ROT, 0, 0, rate, 0, 0)

    def start_game_rot(self, rate):
        return self.set_feature(self.SENSOR_REPORTID_GAM, 0, 0, rate, 0, 0)

    def start_mag(self, rate):
        return self.set_feature(self.SENSOR_REPORTID_MAG, 0, 0, rate, 0, 0)

    def get_report(self, report_types): 
        report_types.append(self.GET_TIME_REFERENCE)
        res_head, res_data = self.receive_shtp_until(self.CHANNEL_REPORTS, report_types, 20)
        report_ind = 0 
        reports = {}
        while report_ind < len(res_data):
            inc = self.REPORT_SIZES.get(res_data[report_ind], None)
            if inc is None: 
                print(f"WARNING: unrecognized input report: {res_data[0]}")
                return None
            else: 
                if not reports.get(res_data[report_ind], False):
                    reports[res_data[report_ind]] = [res_data[report_ind:report_ind+inc]]
                else:
                    reports[res_data[report_ind]].append(res_data[report_ind:report_ind+inc])
                report_ind += inc
        return reports 

    def get_shtp_errors(self):
        self.send_shtp(self.CHANNEL_COMMAND, [0x01])
        res_head, res_data = self.receive_shtp_until(self.CHANNEL_COMMAND, [0x01], 5)

    def get_prod_inf(self):
        self.send_shtp(self.CHANNEL_CONTROL, [self.PRODUCT_ID_REQUEST])
        _res_head1, res_data1 = self.receive_shtp_until(self.CHANNEL_CONTROL, [self.PRODUCT_ID_RESPONSE])
        _res_head2, res_data2 = self.receive_shtp_until(self.CHANNEL_CONTROL, [self.PRODUCT_ID_RESPONSE])
        return [res_data1, res_data2]

    def send_shtp(self, channel, data):
        '''
        sends a single SHTP message to the IMU
        '''
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

    def receive_shtp_until(self, chan_type, res_types, max_count=3):
        '''
        asks IMU for I2C SHTP messages until the one with the correct channel and report type(s) shows up
        '''
        count = 0
        res_head, res_data = self.receive_shtp()
        while (res_head[2] != chan_type or res_data[0] not in res_types) and count < max_count: 
            self._i2c_delay()
            res_head, res_data = self.receive_shtp()
            count += 1
        return [res_head, res_data] if res_head[2] == chan_type and res_data[0] in res_types else [None, None]

    def receive_shtp(self):
        '''
        reads a single SHTP message from the IMU
        '''
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
            return [[0]*4, [0]*4]

        if msg[2] == 0 and msg[0+4] == 0x01:
            self.print_shtp_errs(msg[4:])

        self.sequence[msg[2]] = msg[3] # sync the sequence with the IMU

        # print("Received: ")
        # print(print_hex(msg))

        return [msg[0:4], msg[4:]]
    
    @staticmethod
    def print_shtp_errs(err_data):
        if len(err_data) == 1:
            return None

        err_dict = [
            "No Error",
            "Hub application attempted to exceed maximum read cargo length",
            "Hub application attempted to exceed maximum read cargo length",
            "Host wrote a header with length greater than maximum write cargo length",
            "Host wrote a header with length <= header length (invalid or no payload)",
            "Host tried to fragment cargo (transfer length < full cargo length)",
            "Host wrote continuation of fragmented cargo (continuation bit set)",
            "Unrecognized command on control channel (2)",
            "Unrecognized parameter to get-advertisement command",
            "Host wrote to unrecognized channel",
            "Advertisement request received while Advertisement Response was pending",
            "Host write before the hub finished sending advertisement response",
            "Error list too long to send, truncated"
        ]
                
        print("ERROR: the following errors were reported from the IMU:")
        for err in err_data[1:]:
            print(f"\t{err_dict[err]}")
    
    def get_ad(self):
        res_head, res_data = self.receive_shtp()
        if res_head[2] == self.CHANNEL_COMMAND and res_data[0] == 0x00:
            # TODO: log not print, and get something out of this ad
            print("Got advertisement")
        else:
            print("Did not get advertisement, moving on")

    @classmethod
    def print_rep(cls, rep):
        rep_methods = {
                cls.SENSOR_REPORTID_ACC: cls._print_acc, 
                cls.SENSOR_REPORTID_GYR: cls._print_gyr,
                cls.SENSOR_REPORTID_MAG: cls._print_mag,
                cls.SENSOR_REPORTID_LIN: cls._print_lin,
                cls.SENSOR_REPORTID_ROT: cls._print_rot,
                cls.SENSOR_REPORTID_GRA: cls._print_gra,
                cls.SENSOR_REPORTID_GAM: cls._print_gam,
                cls.SENSOR_REPORTID_GEO: cls._print_geo,
                cls.SENSOR_REPORTID_TAP: cls._print_tap,
                cls.SENSOR_REPORTID_STP: cls._print_stp,
                cls.SENSOR_REPORTID_STA: cls._print_sta,
                cls.SENSOR_REPORTID_PER: cls._print_per
        }
        rep_methods[rep[0]](rep)

    @classmethod
    def _print_acc(cls, rep): 
        print(f" Acceleration: stat: {hex(rep[2])} delay: {hex(rep[3])} x: {cls.print_hex(rep[5:3:-1])} y: {cls.print_hex(rep[7:5:-1])} z: {cls.print_hex(rep[9:7:-1])}")
    @classmethod
    def _print_gyr(cls, rep):
        pass
    @classmethod
    def _print_mag(cls,rep):
        pass
    @classmethod
    def _print_lin(cls,rep):
        pass
    @classmethod
    def _print_rot(cls,rep):
        print(f" Rotation: stat: {hex(rep[2])} delay: {hex(rep[3])} i: {cls.print_hex(rep[5:3:-1])} j: {cls.print_hex(rep[7:5:-1])} k: {cls.print_hex(rep[9:7:-1])} r: {cls.print_hex(rep[11:9:-1])} accuracy: {cls.print_hex(rep[13:11:-1])} ")
    @classmethod
    def _print_gra(cls,rep):
        pass
    @classmethod
    def _print_gam(cls,rep):
        pass
    @classmethod
    def _print_geo(cls,rep):
        pass
    @classmethod
    def _print_tap(cls,rep):
        pass
    @classmethod
    def _print_stp(cls,rep):
        pass
    @classmethod
    def _print_sta(cls,rep):
        pass
    @classmethod
    def _print_per(cls,rep):
        pass
    @classmethod
    def print_hex(cls,hexs):
        return '0x' + ''.join([hex(h).strip('0x').zfill(2) for h in hexs])



if __name__ == '__main__':
    # reset to start with a clean buffer
    rst = digitalio.DigitalInOut(board.D22)
    rst.direction = digitalio.Direction.OUTPUT
    rst.value = False
    time.sleep(1)
    rst.value = True
    time.sleep(1)
    
    imu = BNO080_I2C(0x4a, 3)
    imu.get_shtp_errors()
    prod_inf = imu.get_prod_inf()
    print(f"Product info: {imu.print_hex(prod_inf[0])}\n{imu.print_hex(prod_inf[1])}")

    # imu.start_calib()

    imu.start_rot(20)
    imu.start_acc(20)

    time.sleep(1)
    while True:
        reps = imu.get_report([imu.SENSOR_REPORTID_ACC, imu.SENSOR_REPORTID_ROT])
        acc_rep = reps.get(imu.SENSOR_REPORTID_ACC, [False])[-1]
        rot_rep = reps.get(imu.SENSOR_REPORTID_ROT, [False])[-1]
        count = 0 
        if acc_rep and rot_rep:
            imu.print_rep(acc_rep)
            imu.print_rep(rot_rep)
            count = 2 
        time.sleep(0.5)
        delete_last_lines(count)
