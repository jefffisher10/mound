import subprocess
import os
import time
from datetime import datetime, timedelta
time.sleep(10)  # wait for log_sensors.py to finish

today = datetime.now().strftime('%Y-%m-%d')
month = datetime.now().strftime('%Y-%m')
hour = datetime.now().hour
minute = datetime.now().minute

data_file = f'/home/ramblinray/mound/data/{month}.txt'
clean_file = '/tmp/mound_clean.txt'
gp_file = '/home/ramblinray/mound/scripts/generate_graphs.gp'
graph_out = '/home/ramblinray/mound/graphs/today.png'
archive_dir = '/home/ramblinray/mound/graphs/archive'
error_path = '/home/ramblinray/mound/data/errors.txt'

# -- Preprocess data --------------------------------------
def preprocess(data_file, clean_file, date_filter=None):
    with open(data_file, 'r') as infile, open(clean_file, 'w') as outfile:
        for line in infile:
            if line.startswith('#'):
                continue
            parts = line.strip().split(', ')
            if len(parts) < 2:
                continue
            if date_filter and not parts[0].startswith(date_filter):
                continue
            timestamp = parts[0].replace(' ', 'T')
            rest = ', '.join(parts[1:])
            outfile.write(f'{timestamp}, {rest}\n')

# -- Build gnuplot script ---------------------------------
def make_gp_script(clean_file, output_file, title, xrange_start, xrange_end):
    return f"""
set terminal png size 1000,1200 background '#ffffff'
set output '{output_file}'

set datafile separator ','
set xdata time
set timefmt '%Y-%m-%dT%H:%M:%S'
set format x '%H:%M'
set xtics rotate by -45 font ',9'
set xrange ['{xrange_start}':'{xrange_end}']

set grid lc rgb '#e0e0e0' lw 1
set border lc rgb '#999999'
set tics textcolor rgb '#555555'
set style line 1 lc rgb '#2C3E50' lw 1.5
set style line 2 lc rgb '#c0392b' lw 1.5
set style line 3 lc rgb '#27ae60' lw 1.5

set multiplot layout 6,1 \
    title '{title}' font ',13' \
    margins 0.12, 0.97, 0.05, 0.95 \
    spacing 0,0.02

set ylabel 'Air Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [-20:120]
set ytics font ',9'
plot '{clean_file}' using 1:($8==1 ? $2 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:2 with lines ls 1 notitle

set ylabel 'Humidity (%)' font ',9' textcolor rgb '#555555'
set yrange [0:100]
plot '{clean_file}' using 1:($8==1 ? $3 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:3 with lines ls 1 notitle

set ylabel 'Pressure (hPa)' font ',9' textcolor rgb '#555555'
set yrange [980:1030]
plot '{clean_file}' using 1:($8==1 ? $4 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:4 with lines ls 1 notitle

set ylabel 'Light (lux)' font ',9' textcolor rgb '#555555'
set yrange [0:50000]
plot '{clean_file}' using 1:($8==1 ? $5 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:($5 < 0 ? 0 : $5) with lines ls 1 notitle

set ylabel 'Soil Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [-20:120]
plot '{clean_file}' using 1:($8==1 ? $6 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:6 with lines ls 2 notitle

set ylabel 'Soil Moisture' font ',9' textcolor rgb '#555555'
set yrange [10000:25000]
plot '{clean_file}' using 1:($8==1 ? $7 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:7 with lines ls 3 notitle

unset multiplot
"""

# -- Generate today's graph -------------------------------
subprocess.run(['python', '/home/ramblinray/mound/scripts/generate_graphs.py'])
print("Today's graph generated!")

# -- Archive today's graph at midnight --------------------
if hour == 23 and minute >= 30:
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    archive_path = f'{archive_dir}/{yesterday}.png'
    if os.path.exists(graph_out):
        subprocess.run(['cp', graph_out, archive_path])
        print(f"Archived yesterday's graph as {yesterday}.png")

    # SCP archive to botpi
    subprocess.run([
        'scp', archive_path,
        f'botpi@192.168.1.33:/var/www/html/mound/graphs/archive/{yesterday}.png'
    ])
    print(f"Archive uploaded to botpi!")

    # -- Generate 7 day graph -----------------------------
    sevenday_clean = '/tmp/mound_7day.txt'
    sevenday_out = '/home/ramblinray/mound/graphs/7day.png'
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # Collect last 7 days of data
    with open(sevenday_clean, 'w') as outfile:
        for i in range(7, -1, -1):
            d = (datetime.now() - timedelta(days=i))
            m = d.strftime('%Y-%m')
            day_str = d.strftime('%Y-%m-%d')
            day_file = f'/home/ramblinray/mound/data/{m}.txt'
            if os.path.exists(day_file):
                with open(day_file, 'r') as infile:
                    for line in infile:
                        if line.startswith('#'):
                            continue
                        parts = line.strip().split(', ')
                        if len(parts) < 2:
                            continue
                        if not parts[0].startswith(day_str):
                            continue
                        timestamp = parts[0].replace(' ', 'T')
                        rest = ', '.join(parts[1:])
                        outfile.write(f'{timestamp}, {rest}\n')

    gp_7day = make_gp_script(sevenday_clean, sevenday_out,
                              f'MOUND — Last 7 Days',
                              f'{seven_days_ago}T00:00:00',
                              f'{today}T23:59:59')

    # Fix x format for 7 day
    gp_7day = gp_7day.replace("set format x '%H:%M'",
                               "set format x '%m/%d'")

    with open(gp_file, 'w') as f:
        f.write(gp_7day)
    subprocess.run(['gnuplot', gp_file])
    print("7 day graph generated!")

    subprocess.run([
        'scp', sevenday_out,
        'botpi@192.168.1.33:/var/www/html/mound/graphs/7day.png'
    ])
    print("7 day graph uploaded to botpi!")

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
# -- Upload latest.json to botpi -------------------------
subprocess.run([
    'scp',
    '/home/ramblinray/mound/data/latest.json',
    'botpi@192.168.1.33:/var/www/html/mound/data/latest.json'
])
print("JSON uploaded to botpi!")
