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

error_path = '/home/ramblinray/mound/data/errors.txt'
noon_jpg   = f'/home/ramblinray/mound/images/noon/{today}.jpg'

os.makedirs('/home/ramblinray/mound/images/noon', exist_ok=True)

BOTPI        = 'ramblinray@192.168.1.33'
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

# -- SCP to ramblinray -----------------------------------------
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

# -- Noon keeper only -------------------------------------
if hour == 12 and minute >= 30:
    if not os.path.exists(noon_jpg):
        if capture(noon_jpg, 1296, 972):
            stamp(noon_jpg, 'noon')
            ship(noon_jpg, f'{BOTPI_IMAGES}/noon/{today}.jpg')
            ship(noon_jpg, f'{BOTPI_IMAGES}/latest.jpg')
            print("Noon keeper captured and uploaded!")
        else:
            with open(error_path, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR camera: failed to capture noon\n")

print("Camera script complete.")
