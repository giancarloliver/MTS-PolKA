#!/bin/bash

if [ $# -ne 1 ]; then
    echo "***************************************"
    echo "Usage: $0 <iperf_json_file>"
    echo "***************************************"
    exit 1
fi

# Run the preprocessor script
./preprocessor.sh "$1" .

if [ $? -ne 0 ]; then
    exit 1
fi

cd results || exit 1
gnuplot ./*.plt 2> /dev/null

