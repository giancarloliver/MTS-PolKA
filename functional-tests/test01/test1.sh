#!/bin/bash
# executar "./test2.sh rx" no host2
# executar "./test2.sh tx" no host1

declare -g RUN=1
declare -g OPT=$1
declare -g INTERFACE="h2-eth0"  # interface de saída do host1 para o edge1
declare -g IP="10.0.2.2"      # ip do host2
declare -g IPERFTIME=120
declare -g SLEEPTIME=120
declare -g DELAY=2
declare -g SAMPLES=20 # Número de vezes que o teste será realizado.


iperfrx () {
	iperf3 -s -p 5000 # UDP
}

iperftx () {
	FILENAME="$1"
	BANDWIDTH="$2"
	
	sleep ${DELAY}
	echo "Enviando na taxa de ${BANDWIDTH}m pelo tunel ${tun}"
	iperf3 -c $IP -k 10000 -u -b ${BANDWIDTH}m -p 5000 1>/dev/null &  ### UDP
	sleep $((${SLEEPTIME} - ${DELAY})) 2> /dev/null
	killall iperf
	killall bwm-ng
	mkdir -p data/run${RUN}/${BANDWIDTH}
	grep ${INTERFACE} tmp.bwm > data/run${RUN}/${BANDWIDTH}/${FILENAME}.csv
	rm tmp.bwm
	sleep "${DELAY}"
}

main() {
    bwm-ng -t 1000 -o csv -u bytes -T rate -C ',' > tmp.bwm &
	if [ "${OPT}" == "tx" ]; then
		killall iperf
		
		for j in 40; do
			echo "Considerando uma banda de ${j}Mbits/s"
			for i in $(seq 1 $SAMPLES); do
				start_time=$(date +%s)
				echo "Sample # ${i}: Started in: ${start_time}"
				iperftx "a${i}" "$j"
				end_time=$(date +%s)
				echo "Sample # ${i}: Finished in: ${end_time}"
			done
		done
	fi
	
	if [ "${OPT}" == "rx" ]; then
		iperfrx
	fi

	if [ "${OPT}" == "" ]; then
		echo "Informe tx ou rx"
	fi
}

main