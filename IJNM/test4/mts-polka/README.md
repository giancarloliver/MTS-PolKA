# Test 4 — MTS-PolKA: Elephant Flows and Mice Flows

## 1. Objetivo e referência publicada

Este diretório contém artefatos associados à execução do MTS-PolKA no Test 4, descrito na Seção 4.4 do artigo.

O experimento compara MTS-PolKA com ECMP, WCMP e RPS em cenário com elephant e mice flows. As métricas apresentadas no artigo são:
- **Flow Completion Time (FCT)** dos elephant flows;
- **latência de caminho** dos mice flows.

**Referência:** artigo IJNM, Seção 4.4, Figuras 17, 18 e 20, Tabela 2 e Apêndice A.

> O repositório também contém um script de análise de retransmissões TCP. Esse artefato adicional não deve ser confundido com as duas métricas que a descrição da Seção 4.4 apresenta para a comparação publicada.

## 2. Cenário descrito no artigo

O cenário utiliza:
- atraso de 1 ms nos enlaces;
- largura de banda de 1 Mbps nos enlaces core;
- largura de banda de 10 Mbps nos enlaces edge;
- dois elephant flows TCP de 100 MB: H2→H6 e H3→H5;
- mice flows TCP de 10 KB entre H1 e H4, com taxa média indicada de quatro fluxos por segundo;
- coleta de tráfego nos destinos H4, H5 e H6;
- coleta de latência com ping.

No cenário MTS-PolKA, os elephant flows usam Perfil 1, com divisão 1:1 entre duas portas ativas, enquanto os mice flows usam Perfil 0. Os switches edge inserem routeID e weightID nos pacotes.

## 3. Arquivos e responsabilidades

| Caminho | Função documentada/observada |
|---|---|
| run_test-4.py | Cria a topologia de 14 hosts, seis switches edge, dois switches core de primeiro nível e cinco de segundo nível; inicia elephant flows, mice flows, monitoramento e pings |
| conf_profile/ | Diretório reservado às configurações de perfis |
| fct_test/ | Dados de monitoramento e arquivos associados à análise de tráfego/FCT |
| latency_test/ | Logs de ping e resultados de latência |
| retransmission/ | Arquivos e resultados da análise adicional de retransmissões |
| plotter_fct.py | Processa CSVs de bwm-ng e plota vazão por interface de destino |
| plotter_latency.py | Extrai tempos dos logs de ping e gera histogramas/boxplot de latência |
| plotter_retransmission.py | Extrai contagens de retransmissões de saídas iperf3 e gera gráfico comparativo |

As implementações dos métodos de comparação ficam separadas em ../../related_works/ (ECMP, WCMP e RPS). As configurações P4 e CLI utilizadas pelo runner MTS-PolKA são referenciadas em ../../../m-polka/, fora de IJNM.

## 4. Execução

O arquivo de execução presente é run_test-4.py:

```sh
cd IJNM/test4/mts-polka
sudo python3 run_test-4.py
```

Os plotters devem ser executados a partir de diretório de trabalho compatível com os caminhos relativos definidos no código. Antes de executá-los, verificar a existência dos diretórios e arquivos de entrada.

```sh
python3 plotter_fct.py
python3 plotter_latency.py
python3 plotter_retransmission.py
```

## 5. Detalhamento dos scripts de análise

### 5.1 plotter_fct.py

Apesar do nome, o código lê CSVs de bwm-ng para as interfaces s1_1-eth1, s1_1-eth2 e s1_1-eth3, calcula valores médios por amostra e plota **vazão ao longo do tempo**. O arquivo de saída definido no script é fct_test/result/fct_rps.png.

Portanto, esse script não demonstra, por si só, o cálculo de FCT. O FCT publicado deve ser rastreado a partir dos registros de início e término dos fluxos (por exemplo, saídas iperf3), com método de cálculo explícito. Não usar o nome do arquivo de saída como prova de que a métrica foi calculada.

### 5.2 plotter_latency.py

O script lê cinco arquivos de ping, um para cada caminho (path1 a path5), extrai os valores de latência e produz histogramas e um boxplot. O resultado é direcionado a latency_test/result/latency_mts-polka3.pdf.

O script pressupõe que os logs contenham a estrutura textual esperada pelo processamento. A validade dessa extração deve ser conferida com os logs reais.

### 5.3 plotter_retransmission.py

O script procura em retransmission/data/run/ os arquivos ecmp.txt, wcmp.txt, rps.txt e mts-polka.txt, extrai a contagem de retransmissões de uma linha de resumo do iperf3 e gera retransmission/result/retransmissions_tcp.pdf.

Esse processamento é uma análise complementar do repositório. A origem e a integridade dos quatro arquivos devem ser demonstradas antes de atribuir os valores a uma execução ou método. Retransmissões TCP não são medição direta de reordenação de pacotes.

## 6. Pendências de auditoria

1. **Nome do runner:** a documentação anterior citava run_test.py; o arquivo presente é run_test-4.py.
2. **Diretório de logs de latência:** o runner grava os arquivos de ping em latency_test/data/run/, mas plotter_latency.py lê latency_test/data/run3/. A divergência impede presumir que o plotter consuma diretamente os logs produzidos pelo runner atual.
3. **FCT versus vazão:** plotter_fct.py plota vazão de interfaces a partir de CSVs de bwm-ng; não calcula o tempo de conclusão dos fluxos. É necessário localizar e documentar a fonte dos valores de FCT usados na Figura 18.
4. **Mice flows e distribuição temporal:** o artigo descreve quatro fluxos por segundo seguindo distribuição de Poisson. No código, o intervalo é obtido por np.random.poisson(1 / lambda_rate) e usado em time.sleep. Isso gera atrasos inteiros segundo uma distribuição de Poisson; não equivale automaticamente a um processo de chegadas Poisson com intervalos exponenciais. Registrar a diferença sem alterar a descrição publicada.
5. **Duração e amostras:** o runner define samples = 1, duration = 400 e lambda_rate = 4. Conferir a duração real, o número de mice flows iniciados e os horários de término dos elephant flows.
6. **Arquivos de retransmissão:** confirmar a origem dos quatro arquivos de entrada, a existência de dados para cada método e a correspondência entre os resumos iperf3 e as execuções comparadas.
7. **Caminhos relativos:** confirmar o diretório de trabalho exigido por cada plotter e a criação prévia dos diretórios data/ e result/.
8. **Comparabilidade:** manter separados os artefatos MTS-PolKA e os artefatos ECMP/WCMP/RPS. Para cada método, identificar configuração, script, execução, dados brutos e processamento.
9. **Resultados publicados:** não substituir valores ou gráficos do artigo por saídas de nova execução sem identificar dados de origem, método de cálculo e diferenças encontradas.

## 7. Preservação e reprodução

- Preservar scripts, configurações, logs, CSVs e resultados originais.
- Fazer correções em cópias versionadas, sem sobrescrever artefatos históricos.
- Registrar hashes, dependências, ambiente, parâmetros, comandos, data e arquivos de saída.
- Para FCT, documentar precisamente instante inicial, instante final e regra de cálculo.
- Para latência, preservar logs de ping originais e documentar parser e critérios de exclusão de amostras.
- Para retransmissões, preservar arquivos iperf3 completos e documentar como a contagem foi extraída.

## Referências

- SANTOS, G. O. et al. *MTS-PolKA: Weighted Multipath Traffic Splitting With Source Routing for Elephant and Mice Flows*. International Journal of Network Management, v. 35, n. 3, e70016, 2025. [DOI 10.1002/nem.70016](https://doi.org/10.1002/nem.70016).
- [Artigo PDF](../../IJNM_MTS_Polka.pdf).
- [Diretório dos métodos relacionados](../related_works/).
- [Implementação MTS-PolKA](../../../m-polka/).
