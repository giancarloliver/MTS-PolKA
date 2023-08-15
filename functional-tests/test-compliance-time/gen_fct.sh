#!/bin/bash

SAMPLES=3
DELAY=10

main()
{
	declare -a arr=("10.0.2.2")
	declare -i it=0
	for ip in "${arr[@]}"
	do
		echo "IP $ip"
		mkdir "$it"
		cd "$it"
		rm -rf *
		h2 iperf -s
		for i in `seq $SAMPLES`
		do
			echo "Starting: Iperf $i: h1 to $ip"
			h1 iperf -c h2 -M 1200 -n 100000000 -yc 2> /dev/null >>fct.log
			# iperf -c $ip -M 1200 -n 100000000 -yc 2> /dev/null >>fct.log
			sleep $DELAY
			#echo "Ending: Iperf $i"
			#killall iperf 2>/dev/null			
		done
		cat fct.log | cut -d ',' -f 7 | cut -d '-' -f 2 >> a1_${it};
		cd ..
		it=it+1
	done
	
	
}

main "$@"
