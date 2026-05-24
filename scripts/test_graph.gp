set terminal png size 800,300 background '#ffffff'
set output '/home/ramblinray/mound/graphs/temp_test.png'

set datafile separator ','
set xdata time
set timefmt '%Y-%m-%d %H:%M:%S'
set format x '%m/%d\n%H:%M'

set title 'Temperature'
set ylabel 'F'
set grid
set style line 1 lc rgb '#2C3E50' lw 2

plot '/home/ramblinray/mound/data/2026-05.txt' \
     using 1:3 with lines ls 1 notitle
