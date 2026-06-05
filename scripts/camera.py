import subprocess
import os
from datetime import datetime
from PIL import Image, ImageDraw

# -- Paths ------------------------------------------------
today = datetime.now().strftime('%Y-%m-%d')
month = datetime.now().strftime('%Y-%m')
hour = datetime.now().hour
minute = datetime.now().minute
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

data_file = f'/home/ramblinray/mound/data/{month}.txt'
error_path = '/home/ramblinray/mound/data/errors.txt'

# Only noon is archived for timelapse
noon_jpg = f'/home/ramblinray/mound/images/noon/{today}.jpg'
temp_jpg = '/home/ramblinray/mound/images/temp.jpg'

os.makedirs('/home/ramblinray/mound/images/noon', exist_ok=True)

BOTPI = 'botpi@192.168.1.33'
BOTPI_IMAGES = '/var/www/html/mound/images'

# -- Stamp timestamp onto image ---------------------------
def stamp(path, label=None):
    try:
        img = Image.open(path)
        draw = ImageDraw.Draw(img)
        text = f'MOUND  {timestamp}'
        if label:
            text = f'MOUND  {timestamp}  [{label}]'
        draw.text((11, 11), text, fill='black')
        draw.text((10, 10), text, fill='white')
        img.save(path)
    except Exception as e:
        with open(error_path, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR stamp: {e}\n")

# -- Get last two lux readings ----------------------------
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

# -- Capture image ----------------------------------------
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

# -- SCP to botpi -----------------------------------------
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

# -- Capture and ship latest.jpg only (no archive) --------
def capture_latest(label):
    if capture(temp_jpg, 1296, 972):
        stamp(temp_jpg, label)
        ship(temp_jpg, f'{BOTPI_IMAGES}/latest.jpg')
        print(f"{label} shot uploaded as latest.jpg!")
    else:
        with open(error_path, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR camera: failed to capture {label}\n")

# -- Lux readings for dawn/dusk detection -----------------
lux_readings = get_last_lux_readings()
prev_lux = lux_readings[-2] if len(lux_readings) >= 2 else None
curr_lux = lux_readings[-1] if len(lux_readings) >= 1 else None

DAWN_THRESHOLD = 100
DUSK_THRESHOLD = 100

# Dawn -- lux just crossed above threshold
if prev_lux is not None and curr_lux is not None:
    if prev_lux < DAWN_THRESHOLD and curr_lux >= DAWN_THRESHOLD:
        capture_latest('dawn')

    # Dusk -- lux just crossed below threshold
    if prev_lux >= DAWN_THRESHOLD and curr_lux < DUSK_THRESHOLD:
        capture_latest('dusk')

# Mid-morning -- 09:00
if hour == 9 and minute < 31:
    capture_latest('mid-morning')

# Noon -- 12:30, also archive for timelapse
if hour == 12 and minute >= 30:
    if capture(noon_jpg, 1296, 972):
        stamp(noon_jpg, 'noon')
        ship(noon_jpg, f'{BOTPI_IMAGES}/noon/{today}.jpg')
        ship(noon_jpg, f'{BOTPI_IMAGES}/latest.jpg')
        print("Noon keeper archived and uploaded!")

# Mid-afternoon -- 15:00
if hour == 15 and minute < 31:
    capture_latest('mid-afternoon')

print("Camera script complete.")
