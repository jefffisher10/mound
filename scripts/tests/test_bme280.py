import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)
bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

temp_f = (bme.temperature * 9/5) + 32
print(f"Temperature: {temp_f:.1f}F")
print(f"Humidity:    {bme.humidity:.1f}%")
print(f"Pressure:    {bme.pressure:.1f} hPa")
