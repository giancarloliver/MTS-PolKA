# Test 2 — Agile Reconfiguration

## 1. Objetivo

Conforme a Seção 4.2 do artigo, este experimento avalia a reconfiguração ágil dos perfis de divisão de tráfego para um único fluxo, observando a estabilidade durante as transições. A reconfiguração é realizada por alteração de uma entrada de fluxo em um switch edge, que insere routeID e weightID nos pacotes.

A métrica publicada é a **vazão média registrada nos switches core selecionados durante cada fase**.

**Referência:** artigo IJNM, Seção 4.2 — *Agile Reconfiguration*, Figura 14, Tabela 2 e Apêndice A, Tabela A4.

## 2. Cenário e sequência de perfis

O artigo descreve três fases consecutivas de 10 segundos:

| Fase | Perfil no artigo (binário) | Identificador decimal no script |
|---|---|---:|
| 1 | 0 | 0 |
| 2 | 100 | 4 |
| 3 | 1011 | 11 |

Os valores 4 e 11 são as representações decimais dos identificadores binários 100 e 1011. O runner configura tunnel_encap_process_sr no switch edge E1 e captura vazão nas interfaces selecionadas dos switches S2_0, S2_2 e S1_1.

O código executa 30 amostras. Em cada amostra, inicia um servidor iperf3 em H2, inicia o monitoramento e transmite UDP de H1 para H2 com -t 35 e -b 10M. Em seguida, aplica os três perfis, aguardando 10 segundos após cada alteração. A duração configurada no iperf3 e os tempos efetivos devem ser considerados na interpretação da janela de coleta.

## 3. Arquivos

| Caminho | Função |
|---|---|
| run_test-2.py | Cria a topologia, inicia 30 amostras, executa o fluxo UDP, alterna os perfis e extrai arquivos por interface |
| plotter_test-2.py | Lê CSVs de vazão, agrega as amostras e gera o gráfico de migração de perfil |
| conf/ | Diretório reservado às configurações |
| data/ | Diretório destinado às capturas e arquivos derivados |
| result/ | Diretório destinado aos gráficos |

As configurações P4 e os arquivos CLI utilizados pelo runner ficam em ../../m-polka/.

## 4. Execução

```sh
cd IJNM/test2
sudo python3 run_test-2.py
python3 plotter_test-2.py
```

O nome correto do plotter é **plotter_test-2.py**; não usar plotter-test-2.py.

## 5. Processamento do plotter

O plotter lê arquivos com padrão data/run/<switch>-a<amostra>.csv, considera as interfaces S2_0, S2_2 e S1_1, descarta linhas iniciais e agrega os valores das 30 amostras para gerar a curva. O gráfico é salvo em result/test-2.png.

A conversão de colunas e unidades deve ser validada com o formato CSV efetivamente produzido pela versão de bwm-ng utilizada.

## 6. Notas sobre a implementação versionada

1. **Arquivos de captura:** o runner grava o arquivo bruto em `data/run2/`, enquanto os comandos de extração e o plotter referenciam `data/run/`. Essa diferença faz parte do comportamento do código atualmente versionado.
2. **Estrutura de saída:** os diretórios `data/run/` e `data/run2/` são utilizados pelo fluxo de execução e devem estar disponíveis.
3. **Intervalo de coleta:** a função `monitor_bwm_ng` calcula o argumento de `-t` como `interval_sec * 100`; com `interval_sec=1.0`, o valor enviado é 100.
4. **Amostragem do gráfico:** o plotter descarta as 12 primeiras linhas e limita a leitura a 287 linhas por arquivo.
5. **Interpretação:** a estabilidade visualizada na figura deve ser interpretada com base na métrica de vazão coletada. O script não implementa, por si só, uma medição independente de perda de pacotes.

Corrigir os caminhos e o processamento somente em cópia versionada, preservando scripts, dados e gráficos originais.

## 7. Preservação e rastreabilidade

Para cada amostra, registrar arquivo bruto, CSVs extraídos, versões do runner e plotter, configuração dos switches, ambiente, parâmetros e resultado produzido. Não substituir a Figura 14 nem os dados publicados por uma nova execução sem documentar origem e diferenças.

## Referências

- SANTOS, G. O. et al. *MTS-PolKA: Weighted Multipath Traffic Splitting With Source Routing for Elephant and Mice Flows*. International Journal of Network Management, v. 35, n. 3, e70016, 2025. [DOI 10.1002/nem.70016](https://doi.org/10.1002/nem.70016).
- [Artigo PDF](../IJNM_MTS_Polka.pdf).
- [Implementação MTS-PolKA](../../m-polka/).
