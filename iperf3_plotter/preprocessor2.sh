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

# Contar o n�mero de fluxos do iperf
num_fluxos=$(jq '.intervals[0].streams | length' "$1")

# Verificar se o n�mero de fluxos � v�lido
if [[ ! $num_fluxos =~ ^[0-9]+$ ]]; then
    echo "Erro: Falha ao determinar o n�mero de fluxos. Saindo..."
    exit 4
fi

# Criar diret�rio 'results' para armazenar os dados de todos os fluxos
mkdir -p "$2/results"
rm -rf "$2/results"/*

# Dividir o arquivo iperf.csv em arquivos de fluxos individuais
split -l 1 --numeric-suffixes=1 --additional-suffix=".dat" "$2/iperf.csv" "$2/results/flow_"

# Renomear os arquivos de fluxo para remover os zeros � esquerda nos nomes dos arquivos
for arquivo in "$2/results/flow_"*".dat"; do
    novo_arquivo=$(echo "$arquivo" | sed 's/flow_0*/flow_/')
    mv "$arquivo" "$novo_arquivo" 2>/dev/null
done

# Processar cada arquivo de fluxo
for arquivo in "$2/results/flow_"*".dat"; do
    awk -F, '{print ($1, int($2), int($3), ($5/1024)/1024, $6/1024/1024, $7, $9, $8)}' "$arquivo" | sort -n -k 2 > "$arquivo.processed"
done

# Executar script GNUplot para cada arquivo processado
for arquivo_processado in "$2/results/flow_"*".dat.processed"; do
    gnuplot /usr/bin/*.plt "$arquivo_processado" 2> /dev/null
done
``