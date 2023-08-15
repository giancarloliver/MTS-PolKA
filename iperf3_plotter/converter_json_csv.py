# -*- coding: utf-8 -*-
import pandas as pd

def json_to_csv(json_file, csv_file):
    # Lê o arquivo JSON e cria um DataFrame
    data = pd.read_json(json_file)
    
    # Converte o DataFrame em um arquivo CSV
    data.to_csv(csv_file, index=False)

# Exemplo de uso
json_to_csv('test_results.json', 'test_results.csv')
