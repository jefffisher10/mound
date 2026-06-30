#!/usr/bin/env python3
"""
power_watch.py — High-frequency power diagnostic logger for MOUND.

Polls the INA219 (load-side voltage/current), the Pi's own throttling
and core voltage state, and CPU temp every ~10 seconds. Designed to run
continuously in the background and catch the moment of an overnight
power failure that the normal 30-minute sensor log misses.

Run as a background service (not cron) so it keeps polling continuously
rather than re-spawning every 30 min. See setup notes at the bottom.
"""

import time
import subprocess
from datetime import datetime

LOG_PATH = '/home/ramblinray/mound/data/power_watch.txt'
POLL_SECONDS = 10

try:
    import board
    import busio
    from adafruit_ina219 import INA219
    i2c = busio.I2C(board.SCL, board.SDA)
    ina = INA219(i2c)
    INA_OK = True
except Exception as e:
    INA_OK = False
    INA_INIT_ERROR = str(e)


def get_throttled():
    try:
        out = subprocess.run(['vcgencmd', 'get_throttled'],
                              capture_output=True, text=True, timeout=3)
        return out.stdout.strip().split('=')[-1]
    except Exception as e:
        return f'ERR:{e}'


def get_core_volts():
    try:
        out = subprocess.run(['vcgencmd', 'measure_volts', 'core'],
                              capture_output=True, text=True, timeout=3)
        # format: volt=1.2000V
        return out.stdout.strip().split('=')[-1].replace('V', '')
    except Exception as e:
        return f'ERR:{e}'


def get_cpu_temp():
    try:
        out = subprocess.run(['vcgencmd', 'measure_temp'],
                              capture_output=True, text=True, timeout=3)
        # format: temp=45.6'C
        return out.stdout.strip().split('=')[-1].replace("'C", '')
    except Exception as e:
        return f'ERR:{e}'


def get_ina219():
    if not INA_OK:
        return f'ERR_INIT:{INA_INIT_ERROR}', f'ERR_INIT'
    try:
        v = round(ina.bus_voltage, 4)
        c = round(ina.current, 2)
        return v, c
    except Exception as e:
        return f'ERR:{e}', f'ERR:{e}'


def main():
    # Write header if file doesn't exist yet
    try:
        with open(LOG_PATH, 'x') as f:
            f.write('# timestamp, voltage_v, current_ma, throttled, core_volts, cpu_temp_c\n')
    except FileExistsError:
        pass

    while True:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        v, c = get_ina219()
        throttled = get_throttled()
        core_v = get_core_volts()
        temp = get_cpu_temp()

        line = f'{ts}, {v}, {c}, {throttled}, {core_v}, {temp}\n'

        with open(LOG_PATH, 'a') as f:
            f.write(line)
            f.flush()

        time.sleep(POLL_SECONDS)


if __name__ == '__main__':
    main()
