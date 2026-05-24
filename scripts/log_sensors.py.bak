import adafruit_dht
import board
from datetime import datetime
import os
import time

# Setup sensor
dht = adafruit_dht.DHT11(board.D4)

# Build file paths
month_file = datetime.now().strftime("%Y-%m") + ".txt"
log_path = os.path.expanduser("~/mound/data/") + month_file
error_path = os.path.expanduser("~/mound/data/errors.txt")

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Try up to 3 times
success = False
for attempt in range(3):
    try:
        temp_c = dht.temperature
        temp_f = (temp_c * 9/5) + 32
        humidity = dht.humidity

        line = f"{timestamp}, {temp_f:.1f}F, {humidity}%\n"

        with open(log_path, "a") as f:
            f.write(line)

        success = True
        break

    except RuntimeError:
        time.sleep(5)

# If all attempts failed, log the error
if not success:
    with open(error_path, "a") as f:
        f.write(f"{timestamp}, ERROR: sensor failed after 3 attempts\n")

dht.exit()
