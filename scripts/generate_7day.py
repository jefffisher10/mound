import subprocess
import os
from datetime import datetime, timedelta

today = datetime.now().strftime('%Y-%m-%d')
month = datetime.now().strftime('%Y-%m')
seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

sevenday_clean = '/tmp/mound_7day.txt'
sevenday_out   = '/home/ramblinray/mound/graphs/7day.png'
gp_file        = '/home/ramblinray/mound/scripts/generate_graphs.gp'
error_path     = '/home/ramblinray/mound/data/errors.txt'

# -- Collect last 7 days of data --------------------------
print("Collecting 7 days of data...")
with open(sevenday_clean, 'w') as outfile:
    for i in range(7, -1, -1):
        d = (datetime.now() - timedelta(days=i))
        m = d.strftime('%Y-%m')
        day_str = d.strftime('%Y-%m-%d')
        day_file = f'/home/ramblinray/mound/data/{m}.txt'
        if os.path.exists(day_file):
            with open(day_file, 'r') as infile:
                for line in infile:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split(', ')
                    if len(parts) < 2:
                        continue
                    if not parts[0].startswith(day_str):
                        continue
                    timestamp = parts[0].replace(' ', 'T')
                    rest = ', '.join(parts[1:])
                    outfile.write(f'{timestamp}, {rest}\n')

# -- Count lines ------------------------------------------
with open(sevenday_clean) as f:
    count = sum(1 for _ in f)
print(f"Found {count} readings across 7 days")

# -- Get dynamic ranges -----------------------------------
def get_range(col, exclude_val=None):
    values = []
    with open(sevenday_clean) as f:
        for line in f:
            parts = line.strip().split(', ')
            if len(parts) > col:
                try:
                    v = float(parts[col])
                    if (exclude_val is None or v != exclude_val) and v > -100:
                        values.append(v)
                except:
                    pass
    if not values:
        return None, None
    mn = min(values)
    mx = max(values)
    pad = (mx - mn) * 0.1 if mx != mn else 1.0
    return round(mn - pad, 1), round(mx + pad, 1)

t_min,  t_max  = get_range(1)
h_min,  h_max  = get_range(2)
p_min,  p_max  = get_range(3)
l_min,  l_max  = get_range(4, exclude_val=99999.0)
st_min, st_max = get_range(5)
sm_min, sm_max = get_range(6)

t_min  = t_min  or 50;  t_max  = t_max  or 90
h_min  = h_min  or 0;   h_max  = h_max  or 100
p_min  = p_min  or 985; p_max  = p_max  or 1015
l_min  = 0;             l_max  = l_max  or 10000
st_min = st_min or 50;  st_max = st_max or 90
sm_min = sm_min or 10000; sm_max = sm_max or 25000

# -- Write gnuplot script ---------------------------------
gp = f"""
set terminal png size 1000,1200 background '#ffffff'
set output '{sevenday_out}'

set datafile separator ','
set xdata time
set timefmt '%Y-%m-%dT%H:%M:%S'
set format x '%m/%d'
set xtics rotate by -45 font ',9'
set xrange ['{seven_days_ago}T00:00:00':'{today}T23:59:59']

set grid lc rgb '#e0e0e0' lw 1
set border lc rgb '#999999'
set tics textcolor rgb '#555555'
set style line 1 lc rgb '#2C3E50' lw 1.5
set style line 2 lc rgb '#c0392b' lw 1.5
set style line 3 lc rgb '#27ae60' lw 1.5

set multiplot layout 6,1 \\
    title 'MOUND -- Last 7 Days' font ',13' \\
    margins 0.12, 0.97, 0.05, 0.95 \\
    spacing 0,0.02

set ylabel 'Air Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [{t_min}:{t_max}]
set ytics font ',9'
plot '{sevenday_clean}' using 1:($8==1 ? $2 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{sevenday_clean}' using 1:2 with lines ls 1 notitle

set ylabel 'Humidity (%)' font ',9' textcolor rgb '#555555'
set yrange [{h_min}:{h_max}]
plot '{sevenday_clean}' using 1:($8==1 ? $3 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{sevenday_clean}' using 1:3 with lines ls 1 notitle

set ylabel 'Pressure (hPa)' font ',9' textcolor rgb '#555555'
set yrange [{p_min}:{p_max}]
plot '{sevenday_clean}' using 1:($8==1 ? $4 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{sevenday_clean}' using 1:4 with lines ls 1 notitle

set ylabel 'Light (lux)' font ',9' textcolor rgb '#555555'
set yrange [{l_min}:{l_max}]
plot '{sevenday_clean}' using 1:($8==1 ? $5 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{sevenday_clean}' using 1:($5 >= 99999 ? 1/0 : ($5 < 0 ? 0 : $5)) with lines ls 1 notitle

set ylabel 'Soil Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [{st_min}:{st_max}]
plot '{sevenday_clean}' using 1:($8==1 ? $6 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{sevenday_clean}' using 1:6 with lines ls 2 notitle

set ylabel 'Soil Moisture' font ',9' textcolor rgb '#555555'
set yrange [{sm_min}:{sm_max}]
plot '{sevenday_clean}' using 1:($8==1 ? $7 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{sevenday_clean}' using 1:7 with lines ls 3 notitle

unset multiplot
"""

with open(gp_file, 'w') as f:
    f.write(gp)

subprocess.run(['gnuplot', gp_file])
print("7 day graph generated!")

# -- SCP to botpi -----------------------------------------
scp = subprocess.run([
    'scp', sevenday_out,
    'botpi@192.168.1.33:/var/www/html/mound/graphs/7day.png'
])
if scp.returncode == 0:
    print("7 day graph uploaded to botpi!")
else:
    with open(error_path, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR: 7day SCP failed\n")
    print("SCP failed!")
