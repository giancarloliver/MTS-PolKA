#!/bin/bash

# Verificar n�mero de par�metros � 2
if [ $# -ne 2 ]; then
    echo "Uso: $0 <iperf_json_input> <output_directory>"
    exit 1
fi

# Verificar se o par�metro passado � um arquivo
if [ ! -f "$1" ]; then
    echo "Erro: $1 n�o � um arquivo. Saindo..."
    exit 2
fi

# Verificar se o par�metro passado � um JSON v�lido
jq empty < "$1" >> /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Erro: $1 n�o � um arquivo JSON v�lido. Saindo..."
    exit 3
fi

# Converter a sa�da JSON do iperf para CSV
res=$(jq -r '.intervals[].streams[] | [.socket, .start, .end, .seconds, .bytes, .bits_per_second, .packets, .omitted, .sender] | @csv' "$1")

# Criar diret�rio de sa�da
mkdir -p "$2"

# Inserir nova linha em cada registro
# Ordenar o arquivo (por padr�o, ser� ordenado pelo socket ou pelo cliente)
# Redirecionar a sa�da para um arquivo no diret�rio especificado com o nome iperf.csv
echo "$res" | tr ' ' '\n' | sort > "$2/iperf.csv"

# Processar o arquivo de fluxo
awk -F, '{print ($1, int($2), int($3), ($5/1024)/1024, $6/1024/1024, $7, $9, $8)}' "$2/iperf.csv" | sort -n -k 2 > "$2/results/flow.dat"

# Executar script GNUplot para o arquivo processado e gerar PDF
gnuplot <<- GNUPLOT_SCRIPT
    set term pdf
    set output "$2/results/bytes.pdf"
    plot "$2/results/flow.dat" using 2:5 with lines title "Bytes"
GNUPLOT_SCRIPT