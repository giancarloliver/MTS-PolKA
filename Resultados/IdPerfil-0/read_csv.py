import pandas as pd

# Especifique o caminho do arquivo CSV
caminho_arquivo = 'resultado-IdPerfil-0.csv'

# Use a função read_csv do pandas para ler o arquivo CSV
dados = pd.read_csv(caminho_arquivo)

# Exiba os dados
print(dados)

