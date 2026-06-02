import subprocess
import os
from datetime import datetime

# ── Paths ────────────────────────────────────────────────
today = datetime.now().strftime('%Y-%m-%d')
month = datetime.now().strftime('%Y-%m')
hour = datetime.now().hour
minute = datetime.now().minute

data_file = f'/home/ramblinray/mound/data/{month}.txt'
error_path = '/home/ramblinray/mound/data/errors.txt'

current_jpg   = '/home/ramblinray/mound/images/current.jpg'
dawn_jpg      = f'/home/ramblinray/mound/images/dawn/{today}.jpg'
afternoon_jpg = f'/home/ramblinray/mound/images/afternoon/{today}.jpg'
dusk_jpg      = f'/home/ramblinray/mound/images/dusk/{today}.jpg'
midnight_jpg  = f'/home/ramblinray/mound/images/midnight/{today}.jpg'

os.makedirs('/home/ramblinray/mound/images/dawn', exist_ok=True)
os.makedirs('/home/ramblinray/mound/images/afternoon', exist_ok=True)
os.makedirs('/home/ramblinray/mound/images/dusk', exist_ok=True)
os.makedirs('/home/ramblinray/mound/images/midnight', exist_ok=True)

BOTPI = 'botpi@192.168.1.33'
BOTPI_IMAGES = '/var/www/html/mound/images'

# ── Get last two lux readings ────────────────────────────
def get_last_lux_readings():
    readings = []
    try:
        with open(data_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split(', ')
                if len(parts) >= 5:
                    try:
                        lux = float(parts[4])
                        readings.append(lux)
                    except:
                        readings.append(None)
    except:
        pass
    return readings[-2:] if len(readings) >= 2 else readings

# ── Capture image ────────────────────────────────────────
def capture(path, width, height):
    result = subprocess.run([
        'rpicam-still',
        '--vflip', '--hflip',
        '--width', str(width),
        '--height', str(height),
        '--nopreview',
        '-o', path
    ], capture_output=True)
    return result.returncode == 0

# ── SCP to botpi ─────────────────────────────────────────
def ship(local_path, remote_path):
    result = subprocess.run([
        'scp', local_path,
        f'{BOTPI}:{remote_path}'
    ], capture_output=True)
    if result.returncode != 0:
        with open(error_path, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR camera SCP: {local_path}\n")
        return False
    return True

# ── Always capture current conditions ───────────────────
if capture(current_jpg, 640, 480):
    ship(current_jpg, f'{BOTPI_IMAGES}/current.jpg')
    print("Current shot uploaded!")
else:
    with open(error_path, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR camera: failed to capture current.jpg\n")

# ── Check for keeper shots ───────────────────────────────
lux_readings = get_last_lux_readings()
prev_lux = lux_readings[-2] if len(lux_readings) >= 2 else None
curr_lux = lux_readings[-1] if len(lux_readings) >= 1 else None

DAWN_THRESHOLD = 100
DUSK_THRESHOLD = 100

# Dawn — lux just crossed above threshold
if prev_lux is not None and curr_lux is not None:
    if prev_lux < DAWN_THRESHOLD and curr_lux >= DAWN_THRESHOLD:
        if not os.path.exists(dawn_jpg):
            if capture(dawn_jpg, 1296, 972):
                ship(dawn_jpg, f'{BOTPI_IMAGES}/dawn/{today}.jpg')
                print(f"Dawn keeper captured!")

    # Dusk — lux just crossed below threshold
    if prev_lux >= DAWN_THRESHOLD and curr_lux < DUSK_THRESHOLD:
        if not os.path.exists(dusk_jpg):
            if capture(dusk_jpg, 1296, 972):
                ship(dusk_jpg, f'{BOTPI_IMAGES}/dusk/{today}.jpg')
                print(f"Dusk keeper captured!")

# Afternoon — between 12:30 and 13:00
if hour == 12 and minute >= 30:
    if not os.path.exists(afternoon_jpg):
        if capture(afternoon_jpg, 1296, 972):
            ship(afternoon_jpg, f'{BOTPI_IMAGES}/afternoon/{today}.jpg')
            print(f"Afternoon keeper captured!")

# Midnight — between 00:00 and 00:30
if hour == 0 and minute < 31:
    if not os.path.exists(midnight_jpg):
        if capture(midnight_jpg, 1296, 972):
            ship(midnight_jpg, f'{BOTPI_IMAGES}/midnight/{today}.jpg')
            print(f"Midnight keeper captured!")
