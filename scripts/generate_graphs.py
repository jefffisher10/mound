import subprocess
import os
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
month = datetime.now().strftime('%Y-%m')

data_file = f'/home/ramblinray/mound/data/{month}.txt'
clean_file = '/tmp/mound_clean.txt'
gp_file = '/home/ramblinray/mound/scripts/generate_graphs.gp'

# Preprocess data file
with open(data_file, 'r') as infile, open(clean_file, 'w') as outfile:
    for line in infile:
        if line.startswith('#'):
            continue
        parts = line.strip().split(', ')
        if len(parts) < 2:
            continue
        timestamp = parts[0].replace(' ', 'T')
        rest = ', '.join(parts[1:])
        outfile.write(f'{timestamp}, {rest}\n')

# Build gnuplot script
gp_script = f"""
set terminal png size 1000,1200 background '#ffffff'
set output '/home/ramblinray/mound/graphs/today.png'

set datafile separator ','
set xdata time
set timefmt '%Y-%m-%dT%H:%M:%S'
set format x '%H:%M'
set xtics rotate by -45 font ',9'
set xrange ['{today}T00:00:00':'{today}T23:59:59']

set grid lc rgb '#e0e0e0' lw 1
set border lc rgb '#999999'
set tics textcolor rgb '#555555'
set style line 1 lc rgb '#2C3E50' lw 1.5
set style line 2 lc rgb '#c0392b' lw 1.5
set style line 3 lc rgb '#27ae60' lw 1.5
set style fill solid 0.15 noborder
set style rect fc rgb '#4a9eff' fs solid 0.08 noborder

set multiplot layout 6,1 \
    title 'MOUND — {today}' font ',13' \
    margins 0.12, 0.97, 0.05, 0.95 \
    spacing 0,0.02

# -- Air Temperature --------------------------------------
set ylabel 'Air Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [-20:110]
set ytics font ',9'
plot '{clean_file}' using 1:($8==1 ? $2 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:2 with lines ls 1 notitle

# -- Humidity ---------------------------------------------
set ylabel 'Humidity (%)' font ',9' textcolor rgb '#555555'
set yrange [0:100]
plot '{clean_file}' using 1:($8==1 ? $3 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:3 with lines ls 1 notitle

# -- Pressure ---------------------------------------------
set ylabel 'Pressure (hPa)' font ',9' textcolor rgb '#555555'
unset yrange
set yrange [980:1030]
plot '{clean_file}' using 1:($8==1 ? $4 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:4 with lines ls 1 notitle

# -- Light ------------------------------------------------
set ylabel 'Light (lux)' font ',9' textcolor rgb '#555555'
set yrange [0:50000]
plot '{clean_file}' using 1:($8==1 ? $5 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:($5 < 0 ? 0 : $5) with lines ls 1 notitle

# -- Soil Temperature -------------------------------------
set ylabel 'Soil Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [-20:110]
plot '{clean_file}' using 1:($8==1 ? $6 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:6 with lines ls 2 notitle

# -- Soil Moisture ----------------------------------------
set ylabel 'Soil Moisture' font ',9' textcolor rgb '#555555'
set yrange [10000:25000]
plot '{clean_file}' using 1:($8==1 ? $7 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '{clean_file}' using 1:7 with lines ls 3 notitle

unset multiplot
"""

with open(gp_file, 'w') as f:
    f.write(gp_script)

subprocess.run(['gnuplot', gp_file])
print("Graph generated!")
