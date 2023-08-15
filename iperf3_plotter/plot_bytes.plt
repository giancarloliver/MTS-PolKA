set terminal pdf
set output 'bytes.pdf'
set datafile separator " "

set xlabel "Time (sec)"
set ylabel "MBytes"
set yrange [0:*]
set title "Sent data over time"
set key reverse Left outside
set grid
set style data lines

FILES = system("ls -1 *.dat")
plot for [data in FILES] data u 2:4 with lines title data

