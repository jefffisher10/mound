import subprocess
import os
from datetime import datetime, timedelta

today = datetime.now().strftime('%Y-%m-%d')
month = datetime.now().strftime('%Y-%m')

data_file = f'/home/ramblinray/mound/data/{month}.txt'
clean_file = '/tmp/mound_clean.txt'
gp_file = '/home/ramblinray/mound/scripts/generate_graphs.gp'
graph_out = '/home/ramblinray/mound/graphs/today.png'

# -- Preprocess data file ---------------------------------
def preprocess(source_file, dest_file, date_filter=None):
    with open(source_file, 'r') as infile, open(dest_file, 'w') as outfile:
        for line in infile:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split(', ')
            if len(parts) < 2:
                continue
            if date_filter and not parts[0].startswith(date_filter):
                continue
            timestamp = parts[0].replace(' ', 'T')
            rest = ', '.join(parts[1:])
            outfile.write(f'{timestamp}, {rest}\n')

# -- Get dynamic min/max for a column ---------------------
def get_range(filepath, col, exclude_val=None):
    values = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split(', ')
                if len(parts) > col:
                    try:
                        v = float(parts[col])
                        if exclude_val is None or v != exclude_val:
                            if v > -9000:  # filter out corrupt sensor readings
                                values.append(v)
                    except:
                        pass
    except:
        pass
    if not values:
        return None, None
    mn = min(values)
    mx = max(values)
    pad = (mx - mn) * 0.1 if mx != mn else 1.0
    return round(mn - pad, 1), round(mx + pad, 1)

# -- Build gnuplot script ---------------------------------
def make_gp(clean_file, output_file, title, xstart, xend, xfmt='%H:%M'):
    # Get dynamic ranges for each channel
    t_min,  t_max  = get_range(clean_file, 1)
    h_min,  h_max  = get_range(clean_file, 2)
    p_min,  p_max  = get_range(clean_file, 3)
    l_min,  l_max  = get_range(clean_file, 4, exclude_val=99999.0)
    st_min, st_max = get_range(clean_file, 5)
    sm_min, sm_max = get_range(clean_file, 6)

    # Fallbacks if no data
    t_min  = t_min  or 50;  t_max  = t_max  or 90
    h_min  = h_min  or 0;   h_max  = h_max  or 100
    p_min  = p_min  or 985; p_max  = p_max  or 1015
    l_min  = 0;             l_max  = l_max  or 10000
    st_min = st_min or 50;  st_max = st_max or 90
    sm_min = sm_min or 10000; sm_max = sm_max or 25000

    return f"""
set terminal png size 1000,1200 background '#ffffff'
set output '{output_file}'

set datafile separator ','
set xdata time
set timefmt '%Y-%m-%dT%H:%M:%S'
set format x '{xfmt}'
set xtics rotate by -45 font ',9'
set xrange ['{xstart}':'{xend}']

set grid lc rgb '#e0e0e0' lw 1
set border lc rgb '#999999'
set tics textcolor rgb '#555555'
set style line 1 lc rgb '#2C3E50' lw 1.5
set style line 2 lc rgb '#c0392b' lw 1.5
set style line 3 lc rgb '#27ae60' lw 1.5

set multiplot layout 6,1 \\
    title '{title}' font ',13' \\
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

# -- Generate today's graph -------------------------------
preprocess(data_file, clean_file, date_filter=today)
gp = make_gp(clean_file, graph_out,
             f'MOUND -- {today}',
             f'{today}T00:00:00',
             f'{today}T23:59:59')
with open(gp_file, 'w') as f:
    f.write(gp)
subprocess.run(['gnuplot', gp_file])
print("Today's graph generated!")

# -- Generate 7 day graph at midnight ---------------------
hour = datetime.now().hour
minute = datetime.now().minute
if hour == 0 and minute < 31:
    sevenday_clean = '/tmp/mound_7day.txt'
    sevenday_out = '/home/ramblinray/mound/graphs/7day.png'
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

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

    gp_7day = make_gp(sevenday_clean, sevenday_out,
                      'MOUND -- Last 7 Days',
                      f'{seven_days_ago}T00:00:00',
                      f'{today}T23:59:59',
                      xfmt='%m/%d')
    with open(gp_file, 'w') as f:
        f.write(gp_7day)
    subprocess.run(['gnuplot', gp_file])
    print("7 day graph generated!")

    subprocess.run([
        'scp', sevenday_out,
        'ramblinray@192.168.1.33:/var/www/html/mound/graphs/7day.png'
    ])
    print("7 day graph uploaded!")
