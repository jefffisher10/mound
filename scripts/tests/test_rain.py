import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO

# ADS1115 analog reading
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
channel = AnalogIn(ads, 1)  # A1

# Digital pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

print(f"Analog value: {channel.value}  Voltage: {channel.voltage:.3f}V")
print(f"Digital (rain detected): {not GPIO.input(17)}")

GPIO.cleanup()
