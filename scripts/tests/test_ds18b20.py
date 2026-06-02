# Read DS18B20 soil temperature probe

sensor_path = "/sys/bus/w1/devices/28-000000cc0ce2/temperature"

with open(sensor_path, "r") as f:
    raw = int(f.read().strip())

temp_c = raw / 1000
temp_f = (temp_c * 9/5) + 32

print(f"Soil Temp: {temp_f:.1f}F ({temp_c:.1f}C)")
