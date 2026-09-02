
set terminal png size 1000,1550 background '#ffffff'
set output '/home/ramblinray/mound/graphs/today.png'

set datafile separator ','
set xdata time
set timefmt '%Y-%m-%dT%H:%M:%S'
set format x '%H:%M'
set xtics rotate by -45 font ',9'
set xrange ['2026-09-02T00:00:00':'2026-09-02T23:59:59']

set grid lc rgb '#e0e0e0' lw 1
set border lc rgb '#999999'
set tics textcolor rgb '#555555'
set style line 1 lc rgb '#2C3E50' lw 1.5
set style line 2 lc rgb '#c0392b' lw 1.5
set style line 3 lc rgb '#27ae60' lw 1.5
set style line 4 lc rgb '#8e44ad' lw 1.5
set style line 5 lc rgb '#16a085' lw 1.5

set multiplot layout 8,1 \
    title 'MOUND -- 2026-09-02' font ',13' \
    margins 0.12, 0.97, 0.04, 0.96 \
    spacing 0,0.02

set ylabel 'Air Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [70.9:104.1]
set ytics font ',9'
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $2 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:2 with lines ls 1 notitle

set ylabel 'Humidity (%)' font ',9' textcolor rgb '#555555'
set yrange [44.6:73.2]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $3 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:3 with lines ls 1 notitle

set ylabel 'Pressure (hPa)' font ',9' textcolor rgb '#555555'
set yrange [989.6:991.9]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $4 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:4 with lines ls 1 notitle

set ylabel 'Light (lux)' font ',9' textcolor rgb '#555555'
set yrange [0:2204.8]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $5 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:($5 >= 99999 ? 1/0 : ($5 < 0 ? 0 : $5)) with lines ls 1 notitle

set ylabel 'Soil Temp (F)' font ',9' textcolor rgb '#555555'
set yrange [75.4:88.6]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $6 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:6 with lines ls 2 notitle

set ylabel 'Soil Moisture' font ',9' textcolor rgb '#555555'
set yrange [-657.4:8443.4]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $7 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:7 with lines ls 3 notitle

set ylabel 'Battery Voltage (V)' font ',9' textcolor rgb '#555555'
set yrange [12.7:14.7]
plot '/tmp/mound_clean.txt' using 1:($8==1 ? $9 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:9 with lines ls 4 notitle

set ylabel 'Battery Current (mA)' font ',9' textcolor rgb '#555555'
set yrange [-843.5:184.0]
plot 0 with lines lc rgb '#cccccc' lw 1 notitle, \
     '/tmp/mound_clean.txt' using 1:($8==1 ? $10 : 1/0) with impulses lc rgb '#4a9eff' lw 3 notitle, \
     '/tmp/mound_clean.txt' using 1:10 with lines ls 5 notitle

unset multiplot
