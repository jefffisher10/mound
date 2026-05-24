import board
import busio
import adafruit_tsl2591
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_bme280 import basic as adafruit_bme280
import RPi.GPIO as GPIO
from datetime import datetime
import os
import time

# -- File paths ------------------------------------------
month_file = datetime.now().strftime("%Y-%m") + ".txt"
log_path   = os.path.expanduser("~/mound/data/") + month_file
error_path = os.path.expanduser("~/mound/data/errors.txt")
timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -- Header for new monthly files -------------------------
header = "# timestamp, temp_f, humidity_pct, pressure_hpa, lux, soil_temp_f, soil_moisture_raw, rain\n"

# -- Setup ------------------------------------------------
i2c   = busio.I2C(board.SCL, board.SDA)
bme   = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
tsl   = adafruit_tsl2591.TSL2591(i2c)
ads   = ADS.ADS1115(i2c)
soil  = AnalogIn(ads, 0)
rain_analog = AnalogIn(ads, 1)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

# -- DS18B20 ----------------------------------------------
def read_soil_temp():
    sensor_path = "/sys/bus/w1/devices/28-000000cc0ce2/temperature"
    with open(sensor_path, "r") as f:
        raw = int(f.read().strip())
    temp_c = raw / 1000
    return round((temp_c * 9/5) + 32, 1)

# -- Read all sensors -------------------------------------
success = False
for attempt in range(3):
    try:
        temp_f   = round((bme.temperature * 9/5) + 32, 1)
        humidity = round(bme.humidity, 1)
        pressure = round(bme.pressure, 1)
        lux      = round(tsl.lux, 1)
        soil_temp = read_soil_temp()
        moisture  = soil.value
        rain      = 0 if GPIO.input(17) else 1

        line = f"{timestamp}, {temp_f}, {humidity}, {pressure}, {lux}, {soil_temp}, {moisture}, {rain}\n"

        # Write header if new file
        if not os.path.exists(log_path):
            with open(log_path, "w") as f:
                f.write(header)

        with open(log_path, "a") as f:
            f.write(line)

        success = True
        break

    except RuntimeError:
        time.sleep(5)

if not success:
    with open(error_path, "a") as f:
        f.write(f"{timestamp}, ERROR: sensor failed after 3 attempts\n")

GPIO.cleanup()
