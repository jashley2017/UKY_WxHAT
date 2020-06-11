'''
NEO_M8P RTK GPS UART+I2C python driver

currently starts the timepulse at 1Hz 50% duty cycle
'''
#!/usr/bin/python3
import serial
import time
import board
import digitalio


# reset = digitalio.DigitalInOut(board.D20)
# reset.direction = digitalio.Direction.OUTPUT
timepulse = digitalio.DigitalInOut(board.D26)
timepulse.direction = digitalio.Direction.INPUT

# reset.value = True
# time.sleep(1)
# reset.value = False


delay = 0.5
gps_port = serial.Serial(
        port='/dev/serial0',
        baudrate=9600, 
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        timeout=1 
    )

# all multibyte values are little endian unless otherwise stated
pps_conf_msg = [
    0xB5, # header 1
    0x62, # header 2
    0x06, # class
    0x31, # id 
    32&0xff, # length lsb
    (32>>8)&0xff, # length msb
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
]

ck_a = 0
ck_b = 0
for byte in pps_conf_msg[2:]:
    ck_a+=byte
    ck_b+=ck_a

ck_a &= 0xff
ck_b &= 0xff

pps_conf_msg.append(ck_a)
pps_conf_msg.append(ck_b)

msg = bytearray(pps_conf_msg)

print(f"Sending {msg.hex()}")

gps_port.write(msg)
time.sleep(1)

ack = gps_port.read(8)

print(f"Response {ack.hex()}")

count = 0 
while count < 10:
    print(timepulse.value)
    time.sleep(0.5)

