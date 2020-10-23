# WXHAT IC drivers

## Requirements

### CiruitPython Compatibility
This library is being designed with CircuitPython compatibility in mind such that it could be ported over to a microcontroller in the future. However, CircuitPython has very little in terms of concurrent operation

This was abandoned for the sampling of all of the devices concurrently because CircuitPython does not support multithreaded operation. However, multithreaded operation is only used in wxhat.py, so all other code should be somewhat portable to CircuitPython.

The adafruit CircuitPython libraries need to be installed as well as the blinka library for digital IO.

### Initial Setup

#### Enable I2C interfacing
```sh
sudo apt-get install -y i2c-tools
sudo raspi-config; # enable I2C in the interfacing options
sudo raspi-config; # disable Serial console (Interfacing options -> Serial -> No on console options, yes on serial option)
```

#### Boot configuration
The boot/config.txt file needs to be altered in order to accomadate the clock stretching for the IMU. In order to do this, copy the config.txt file in this repository to your /boot directory like so:

```sh 
sudo cp ./config.txt /boot
```

#### Install CircuitPython Libraries using venv
```sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Usage
Before any run, you will need to source the python virtual environment you created.
```sh
source venv/bin/activate
```

Test GPS
```sh
python3 ./neo_m8p/neo_m8p_hat.py
```

Test THP sensors
```sh
sudo venv/bin/python3 ./thp_sensors.py
```

Test ADC
```sh
python3 ./ads_hat.py
```

Test Concurrent Sampling *(not CircuitPython compatible)*
```sh
sudo venv/bin/python3 ./wxhat.py
```

Test IMU
```sh
python3 ./bno080_i2c.py
```

## Current issues

- [X] Configurable logger that controls Neopixel 2 should be used instead of print
- [ ] Cleanup code make more generic
