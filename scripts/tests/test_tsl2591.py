import board
import busio
import adafruit_tsl2591

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2591.TSL2591(i2c)

print(f"Light:    {sensor.lux:.2f} lux")
print(f"Visible:  {sensor.visible}")
print(f"Infrared: {sensor.infrared}")
