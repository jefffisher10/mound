import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Setup I2C and ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Read channel A0 (soil moisture sensor)
channel = AnalogIn(ads, 0)

print(f"Raw value: {channel.value}  Voltage: {channel.voltage:.3f}V")
