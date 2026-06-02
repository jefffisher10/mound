import board
import busio
import adafruit_tsl2591
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_ina219 import INA219
import RPi.GPIO as GPIO
from datetime import datetime
import os
import time

# -- File paths ------------------------------------------
month_file = datetime.now().strftime("%Y-%m") + ".txt"
log_path   = os.path.expanduser("~/mound/data/") + month_file
error_path = os.path.expanduser("~/mound/data/errors.txt")
timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

header = "# timestamp, temp_f, humidity_pct, pressure_hpa, lux, soil_temp_f, soil_moisture_raw, rain, voltage, current_ma\n"

# -- Setup I2C --------------------------------------------
i2c = busio.I2C(board.SCL, board.SDA)

# -- Read BME280 ------------------------------------------
try:
    bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    temp_f   = round((bme.temperature * 9/5) + 32, 1)
    humidity = round(bme.humidity, 1)
    pressure = round(bme.pressure, 1)
except Exception as e:
    temp_f = humidity = pressure = None
    with open(error_path, "a") as f:
        f.write(f"{timestamp}, ERROR BME280: {e}\n")

# -- Read TSL2591 -----------------------------------------
try:
    tsl = adafruit_tsl2591.TSL2591(i2c)
    tsl.gain = adafruit_tsl2591.GAIN_LOW
    tsl.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS
    try:
	lux = round(tsl.lux, 1)
    except adafruit_tsl2591.exceptions.OverflowError:
	lux = 99999

except Exception as e:
    lux = None
    with open(error_path, "a") as f:
        f.write(f"{timestamp}, ERROR TSL2591: {e}\n")

# -- Read ADS1115 -----------------------------------------
try:
    ads = ADS.ADS1115(i2c)
    soil_moisture = AnalogIn(ads, 0).value
except Exception as e:
    soil_moisture = None
    with open(error_path, "a") as f:
        f.write(f"{timestamp}, ERROR ADS1115: {e}\n")

# -- Read DS18B20 -----------------------------------------
try:
    path = "/sys/bus/w1/devices/28-000000cc0ce2/temperature"
    with open(path, "r") as f:
        raw = int(f.read().strip())
    soil_temp = round((raw / 1000 * 9/5) + 32, 1)
except Exception as e:
    soil_temp = None
    with open(error_path, "a") as f:
        f.write(f"{timestamp}, ERROR DS18B20: {e}\n")

# -- Read rain digital ------------------------------------
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN)
    rain = 0 if GPIO.input(17) else 1
except Exception as e:
    rain = None
    with open(error_path, "a") as f:
        f.write(f"{timestamp}, ERROR RAIN: {e}\n")
finally:
    GPIO.cleanup()

# -- Read INA219 ------------------------------------------
try:
    ina = INA219(i2c)
    voltage    = round(ina.bus_voltage, 3)
    current_ma = round(ina.current, 1)
except Exception as e:
    voltage = current_ma = None
    with open(error_path, "a") as f:
        f.write(f"{timestamp}, ERROR INA219: {e}\n")

# -- Write log --------------------------------------------
if not os.path.exists(log_path):
    with open(log_path, "w") as f:
        f.write(header)

line = f"{timestamp}, {temp_f}, {humidity}, {pressure}, {lux}, {soil_temp}, {soil_moisture}, {rain}, {voltage}, {current_ma}\n"

with open(log_path, "a") as f:
    f.write(line)
