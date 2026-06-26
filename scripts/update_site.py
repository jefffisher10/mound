import subprocess
import os
import time
from datetime import datetime, timedelta

time.sleep(10)  # wait for log_sensors.py to finish

today = datetime.now().strftime('%Y-%m-%d')
month = datetime.now().strftime('%Y-%m')
hour = datetime.now().hour
minute = datetime.now().minute

error_path  = '/home/ramblinray/mound/data/errors.txt'
graph_out   = '/home/ramblinray/mound/graphs/today.png'
archive_dir = '/home/ramblinray/mound/graphs/archive'

# -- Debug log --------------------------------------------
with open(error_path, 'a') as f:
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, DEBUG: hour={hour} minute={minute}\n")

# -- Archive BEFORE regenerating graph --------------------
if hour == 23 and minute >= 30:
    archive_path = f'{archive_dir}/{today}.png'
    with open(error_path, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, DEBUG: archive block firing\n")
    if os.path.exists(graph_out):
        subprocess.run(['cp', graph_out, archive_path])
        with open(error_path, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, DEBUG: archive copied ok\n")
    else:
        with open(error_path, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, DEBUG: today.png NOT FOUND\n")
    scp = subprocess.run([
        'scp', archive_path,
        f'botpi@192.168.1.33:/var/www/html/mound/graphs/archive/{today}.png'
    ])
    with open(error_path, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, DEBUG: archive SCP returned {scp.returncode}\n")

# -- Generate today's graph -------------------------------
subprocess.run(['python', '/home/ramblinray/mound/scripts/generate_graphs.py'])

# -- Upload today's graph to botpi ------------------------
scp_result = subprocess.run([
    'scp', graph_out,
    'botpi@192.168.1.33:/var/www/html/mound/graphs/today.png'
])
if scp_result.returncode == 0:
    print("Today's graph uploaded to botpi!")
else:
    with open(error_path, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR: SCP failed\n")
    print("SCP failed!")

# -- Generate and upload HTML page ------------------------
subprocess.run(['python', '/home/ramblinray/mound/scripts/generate_page.py'])

page_scp = subprocess.run([
    'scp',
    '/home/ramblinray/mound/page/index.html',
    'botpi@192.168.1.33:/var/www/html/mound/index.html'
])
if page_scp.returncode == 0:
    print("Page uploaded to botpi!")
else:
    print("Page SCP failed!")

# -- Upload latest.json to botpi --------------------------
subprocess.run([
    'scp',
    '/home/ramblinray/mound/data/latest.json',
    'botpi@192.168.1.33:/var/www/html/mound/data/latest.json'
])
print("JSON uploaded to botpi!")
