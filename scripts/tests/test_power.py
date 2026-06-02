import board
import busio
from adafruit_ina219 import INA219

# Setup I2C and INA219
i2c = busio.I2C(board.SCL, board.SDA)
ina = INA219(i2c)

print(f"Bus Voltage:   {ina.bus_voltage:.3f} V")
print(f"Current:       {ina.current:.2f} mA")
print(f"Power:         {ina.power:.2f} mW")
