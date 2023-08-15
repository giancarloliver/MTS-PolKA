#!/bin/bash

declare -g RUN=1
declare -g OPT=$1
declare -g INTERFACE="h2-eth0"  # interface de saída do host1 para o edge1
declare -g IP="10.0.2.2"      # IP do host2
declare -g IPERFTIME=120
declare -g SLEEPTIME=5
declare -g DELAY=2
declare -g SAMPLES=20 # Número de vezes que o teste será realizado.

iperfrx () {
    iperf3 -s 
}

iperftx () {
    FILENAME="$1"
    BANDWIDTH="$2"
    sleep ${DELAY}
    echo "Enviando pacotes UDP de 10.0.1.1 para 10.0.2.2 na taxa de ${BANDWIDTH}m (Amostra ${i})"
    iperf3 -c $IP -k 10000 -u -b ${BANDWIDTH}m 1 > /dev/null
    sleep ${SLEEPTIME}
    sleep "${DELAY}"
}

main() {
    if [ "${OPT}" == "tx" ]; then
        for j in 40; do
            echo "Considerando uma banda de ${j}Mbits/s"
            for i in $(seq 1 $SAMPLES); do
                start_time=$(date +%s)
                echo "Amostra # ${i}: Iniciada em: ${start_time}"
                iperftx "a${i}" "$j"
                end_time=$(date +%s)
                echo "Amostra # ${i}: Concluída em: ${end_time}"
            done
        done
    elif [ "${OPT}" == "rx" ]; then
        iperfrx
    else
        echo "Informe tx ou rx"
    fi
}

main
