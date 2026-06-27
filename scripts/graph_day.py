import subprocess
import os
import sys
from datetime import datetime

# -- Accept a date argument or use yesterday ---------------
if len(sys.argv) > 1:
    target_date = sys.argv[1]
else:
    # Default to yesterday
    from datetime import timedelta
    target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

month = target_date[:7]
data_file = f'/home/ramblinray/mound/data/{month}.txt'
clean_file = '/tmp/mound_manual.txt'
gp_file = '/tmp/mound_manual.gp'
output_file = f'/home/ramblinray/mound/graphs/archive/{target_date}.png'

print(f"Generating graph for {target_date}...")

# -- Check data file exists --------------------------------
if not os.path.exists(data_file):
    print(f"ERROR: No data file found for {month}")
    sys.exit(1)

# -- Preprocess -------------------------------------------
count = 0
with open(data_file, 'r') as infile, open(clean_file, 'w') as outfile:
    for line in infile:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.strip().split(', ')
        if len(parts) < 2:
            continue
        if not parts[0].startswith(target_date):
            continue
        timestamp = parts[0].replace(' ', 'T')
        rest = ', '.join(parts[1:])
        outfile.write(f'{timestamp}, {rest}\n')
        count += 1

print(f"Found {count} readings for {target_date}")

if count == 0:
    print("ERROR: No data found for that date!")
    sys.exit(1)

# -- Get dynamic ranges -----------------------------------
def get_range(col, exclude_val=None):
    values = []
    with open(clean_file) as f:
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
set output '{output_file}'

set datafile separator ','
set xdata time
set timefmt '%Y-%m-%dT%H:%M:%S'
set format x '%H:%M'
set xtics rotate by -45 font ',9'
set xrange ['{target_date}T00:00:00':'{target_date}T23:59:59']

set grid lc rgb '#e0e0e0' lw 1
set border lc rgb '#999999'
set tics textcolor rgb '#555555'
set style line 1 lc rgb '#2C3E50' lw 1.5
set style line 2 lc rgb '#c0392b' lw 1.5
set style line 3 lc rgb '#27ae60' lw 1.5

set multiplot layout 6,1 \\
    title 'MOUND -- {target_date}' font ',13' \\
    margins 0.12, 0.97, 0.05, 0.95 \\
    spacing 0,0.02

set ylabel 'Air Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [{t_min}:{t_max}]
set ytics font ',9'
plot '{clean_file}' using 1:($8==1 ? $2 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{clean_file}' using 1:2 with lines ls 1 notitle

set ylabel 'Humidity (%)' font ',9' textcolor rgb '#555555'
set yrange [{h_min}:{h_max}]
plot '{clean_file}' using 1:($8==1 ? $3 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{clean_file}' using 1:3 with lines ls 1 notitle

set ylabel 'Pressure (hPa)' font ',9' textcolor rgb '#555555'
set yrange [{p_min}:{p_max}]
plot '{clean_file}' using 1:($8==1 ? $4 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{clean_file}' using 1:4 with lines ls 1 notitle

set ylabel 'Light (lux)' font ',9' textcolor rgb '#555555'
set yrange [{l_min}:{l_max}]
plot '{clean_file}' using 1:($8==1 ? $5 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{clean_file}' using 1:($5 >= 99999 ? 1/0 : ($5 < 0 ? 0 : $5)) with lines ls 1 notitle

set ylabel 'Soil Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [{st_min}:{st_max}]
plot '{clean_file}' using 1:($8==1 ? $6 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{clean_file}' using 1:6 with lines ls 2 notitle

set ylabel 'Soil Moisture' font ',9' textcolor rgb '#555555'
set yrange [{sm_min}:{sm_max}]
plot '{clean_file}' using 1:($8==1 ? $7 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \\
     '{clean_file}' using 1:7 with lines ls 3 notitle

unset multiplot
"""

with open(gp_file, 'w') as f:
    f.write(gp)

subprocess.run(['gnuplot', gp_file])
print(f"Graph saved to {output_file}")

# -- SCP to ramblinray -----------------------------------------
scp = subprocess.run([
    'scp', output_file,
    f'ramblinray@192.168.1.33:/var/www/html/mound/graphs/archive/{target_date}.png'
])
if scp.returncode == 0:
    print(f"Uploaded to yesteryearforever!")
else:
    print(f"SCP failed!")
