import subprocess
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# -- Paths ------------------------------------------------
today = datetime.now().strftime('%Y-%m-%d')
month = datetime.now().strftime('%Y-%m')
hour = datetime.now().hour
minute = datetime.now().minute
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

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

# -- Stamp timestamp onto image ---------------------------
def stamp(path, label=None):
    try:
        img = Image.open(path)
        draw = ImageDraw.Draw(img)
        text = f'MOUND  {timestamp}'
        if label:
            text = f'MOUND  {timestamp}  [{label}]'
        # Shadow for readability
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

# -- Always capture current conditions --------------------
if capture(current_jpg, 640, 480):
    stamp(current_jpg)
    ship(current_jpg, f'{BOTPI_IMAGES}/current.jpg')
    print("Current shot uploaded!")
else:
    with open(error_path, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR camera: failed to capture current.jpg\n")

# -- Check for keeper shots -------------------------------
lux_readings = get_last_lux_readings()
prev_lux = lux_readings[-2] if len(lux_readings) >= 2 else None
curr_lux = lux_readings[-1] if len(lux_readings) >= 1 else None

DAWN_THRESHOLD = 100
DUSK_THRESHOLD = 100

if prev_lux is not None and curr_lux is not None:
    if prev_lux < DAWN_THRESHOLD and curr_lux >= DAWN_THRESHOLD:
        if not os.path.exists(dawn_jpg):
            if capture(dawn_jpg, 1296, 972):
                stamp(dawn_jpg, 'dawn')
                ship(dawn_jpg, f'{BOTPI_IMAGES}/dawn/{today}.jpg')
                print("Dawn keeper captured!")

    if prev_lux >= DAWN_THRESHOLD and curr_lux < DUSK_THRESHOLD:
        if not os.path.exists(dusk_jpg):
            if capture(dusk_jpg, 1296, 972):
                stamp(dusk_jpg, 'dusk')
                ship(dusk_jpg, f'{BOTPI_IMAGES}/dusk/{today}.jpg')
                print("Dusk keeper captured!")

if hour == 12 and minute >= 30:
    if not os.path.exists(afternoon_jpg):
        if capture(afternoon_jpg, 1296, 972):
            stamp(afternoon_jpg, 'afternoon')
            ship(afternoon_jpg, f'{BOTPI_IMAGES}/afternoon/{today}.jpg')
            print("Afternoon keeper captured!")

if hour == 0 and minute < 31:
    if not os.path.exists(midnight_jpg):
        if capture(midnight_jpg, 1296, 972):
            stamp(midnight_jpg, 'midnight')
            ship(midnight_jpg, f'{BOTPI_IMAGES}/midnight/{today}.jpg')
            print("Midnight keeper captured!")
