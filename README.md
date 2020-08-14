# WXHAT IC drivers

## Requirements

### CiruitPython Compatibility
This library is being designed with CircuitPython compatibility in mind such that it could be ported over to a microcontroller in the future. However, CircuitPython has very little in terms of concurrent operation

This was abandoned for the sampling of all of the devices concurrently because CircuitPython does not support multithreaded operation. However, multithreaded operation is only used in wxhat.py, so all other code should be somewhat portable to CircuitPython.

The adafruit CircuitPython libraries need to be installed as well as the blinka library for digital IO.

### Enable I2C on the Pi4

```sh
sudo apt-get install -y i2c-tools
sudo raspi-config; # enable I2C in the interfacing options
```

### Install CircuitPython Libraries using venv
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
./neo_m8p/neo_m8p_hat.py
```

Test THP sensors
```sh
sudo ./thp_sensors.py
```

Test ADC
```sh
./ads_hat.py
```

Test Concurrent Sampling *(not CircuitPython compatible)*
```sh
sudo ./wxhat.py
```

Test IMU
```sh
./bno080_i2c.py
```

## Current issues

- [ ] Configurable logger that controls Neopixel 2 should be used instead of print
- [ ] Cleanup code make more generic
