
set terminal png size 1000,1200 background '#ffffff'
set output '/home/ramblinray/mound/graphs/today.png'

set datafile separator ','
set xdata time
set timefmt '%Y-%m-%dT%H:%M:%S'
set format x '%H:%M'
set xtics rotate by -45 font ',9'
set xrange ['2026-06-27T00:00:00':'2026-06-27T23:59:59']

set grid lc rgb '#e0e0e0' lw 1
set border lc rgb '#999999'
set tics textcolor rgb '#555555'
set style line 1 lc rgb '#2C3E50' lw 1.5
set style line 2 lc rgb '#c0392b' lw 1.5
set style line 3 lc rgb '#27ae60' lw 1.5

set multiplot layout 6,1 \
    title 'MOUND -- 2026-06-27' font ',13' \
    margins 0.12, 0.97, 0.05, 0.95 \
    spacing 0,0.02

set ylabel 'Air Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [68.4:69.2]
set ytics font ',9'
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $2 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:2 with lines ls 1 notitle

set ylabel 'Humidity (%)' font ',9' textcolor rgb '#555555'
set yrange [99.0:101.0]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $3 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:3 with lines ls 1 notitle

set ylabel 'Pressure (hPa)' font ',9' textcolor rgb '#555555'
set yrange [989.2:991.3]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $4 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:4 with lines ls 1 notitle

set ylabel 'Light (lux)' font ',9' textcolor rgb '#555555'
set yrange [0:5.1]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $5 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:($5 >= 99999 ? 1/0 : ($5 < 0 ? 0 : $5)) with lines ls 1 notitle

set ylabel 'Soil Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [71.2:72.1]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $6 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:6 with lines ls 2 notitle

set ylabel 'Soil Moisture' font ',9' textcolor rgb '#555555'
set yrange [11584.2:12037.8]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $7 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:7 with lines ls 3 notitle

unset multiplot
