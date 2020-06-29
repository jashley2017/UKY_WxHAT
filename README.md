# WXHAT IC drivers

## Requirements

This library is being designed with CircuitPython compatibility in mind such that it could be ported over to a microcontroller in the future. 

The adafruit CircuitPython libraries need to be install as well as the blinka library for digital IO.

### Enable I2C and install python bus

```sh
sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tools
sudo raspi-config; # enable I2C in the interfacing options
```

### Install CircuitPython Libraries

```sh
  sudo pip3 install RPI.GPIO
  sudo pip3 install adafruit-blinka
  sudo pip3 install adafruit-circuitpython-bme280
  sudo pip3 install adafruit-circuitpython-bmp3xx
  sudo pip3 install adafruit-circuitpython-neopixel
  sudo pip3 install adafruit-circuitpython-sht31d
```

## Usage

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

Test Concurrent Sampling 
```sh
sudo ./wxhat.py
```

Test IMU
```sh
./bno080_i2c.py
```

## Current issues

- [ ] IMU library needs infinite loop functions for updating sensor values
- [ ] Configurable logger that controls Neopixel 2 should be used instead of print
- [ ] Cleanup code make more generic
