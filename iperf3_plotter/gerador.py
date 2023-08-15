# -*- coding: utf-8 -*-
import json
import io

# Caminho para o arquivo JSON
caminho_arquivo = 'test_results.json'

# Abrir o arquivo JSON usando a codificação 'latin1'
with open('test_results.json', 'r', encoding='latin1') as file:
    data = json.load(file)

# Interpretação dos dados
pacotes_enviados = dados['pacotes_enviados']
tempo_execucao = dados['tempo_execucao']
largura_banda = dados['largura_banda']

# Exemplo de impressão dos dados interpretados
print(f'Pacotes enviados: {pacotes_enviados}')
print(f'Tempo de execução: {tempo_execucao} segundos')
print(f'Largura de banda: {largura_banda} Mbps')
