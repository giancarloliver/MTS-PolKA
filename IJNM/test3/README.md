# Test 3 — Multiple Flows and Competition

## 1. Objetivo

Conforme a Seção 4.3 do artigo, este experimento demonstra a operação simultânea de múltiplos fluxos e a migração ágil de um perfil de tráfego para otimizar o uso dos recursos da rede em um cenário de concorrência.

As métricas publicadas são a **vazão dos fluxos nos múltiplos destinos** e a **vazão agregada dos fluxos na origem**.

**Referência:** artigo IJNM, Seção 4.3 — *Multiple Flows and Competition*, Figuras 15 e 16, Tabela 2 e Apêndice A, Tabela A4.

## 2. Fluxos e cenário

| Identificação | Tipo | Origem → destino | Perfil/observação |
|---|---|---|---|
| tcp1 | TCP | H1 → H2 | Inicia com Perfil 0 e passa por migração de perfil |
| tcp2 | TCP | H1 → H5 | Perfil 1, divisão 1:1 entre duas portas ativas |
| udp1 | UDP | H3 → H4 | Taxa configurada em 4 Mbps |

O artigo destaca que, após a migração, tcp1 passa a explorar dois caminhos, reduzindo a competição com udp1. O fluxo tcp2 permanece com divisão 1:1. A Figura 15 apresenta o cenário e a Figura 16 apresenta as vazões observadas.

## 3. O que o runner implementa

O arquivo run_test-3.py:
- cria topologia com cinco switches edge, dois switches core de primeiro nível e cinco switches core de segundo nível;
- inicia servidores iperf3 nos hosts H2, H5 e H4;
- configura entradas no edge para os fluxos;
- inicia dois clientes TCP em H1 e um cliente UDP em H3;
- inicia coleta de vazão com bwm-ng;
- aguarda 10 segundos e altera a entrada do fluxo TCP H1→H2;
- aguarda mais 22 segundos, encerra os processos e extrai dados de interfaces para CSV.

O script está configurado para executar 30 amostras. A temporização codificada e a duração dos clientes devem ser confrontadas com a janela representada na Figura 16; não presumir que os intervalos do runner sejam idênticos à descrição textual do artigo.

## 4. Arquivos

| Caminho | Função |
|---|---|
| run_test-3.py | Cria a topologia, configura os fluxos, executa a migração de perfil e extrai capturas |
| grafico-test-3.py | Lê CSVs selecionados, agrega as amostras e gera o gráfico de vazão |
| conf/ | Diretório reservado às configurações |
| data/ | Diretório destinado às capturas brutas e CSVs extraídos |
| result/ | Diretório destinado ao gráfico |

As configurações P4 e os arquivos CLI dos switches são referenciados em ../../m-polka/.

## 5. Execução

```sh
cd IJNM/test3
sudo python3 run_test-3.py
python3 grafico-test-3.py
```

O plotter utiliza arquivos em data/run/ e salva o gráfico em result/test1.png, conforme os valores definidos no próprio script.

## 6. Processamento e interpretação

O plotter seleciona as interfaces:
- s1_0-eth1 — origem H1 (tcp1 e tcp2);
- s1_1-eth1 — destino H2 (tcp1);
- s1_1-eth2 — destino H4 (udp1);
- s1_1-eth3 — destino H5 (tcp2).

O código agrega os dados de até 30 arquivos por interface e marca no gráfico os instantes de 10 e 20 segundos. A interpretação das curvas deve considerar a correspondência entre interface, fluxo, direção da coluna do CSV e unidade de vazão.

## 7. Notas sobre a implementação versionada

1. **Comandos iperf3 TCP:** o runner monta os comandos dos clientes TCP com `-b -w 1M`; não há valor explícito entre `-b` e `-w`. A documentação registra literalmente essa composição, sem presumir qual seria o parâmetro pretendido.
2. **Temporização:** os clientes TCP recebem `-t 22`; o runner aguarda 10 segundos antes da migração e mais 22 segundos após a alteração da entrada.
3. **Coleta:** após encerrar `iperf3` e `bwm-ng`, o runner executa comandos `grep` para gerar arquivos CSV por interface.
4. **Amostragem do plotter:** o código descarta uma linha inicial e limita a leitura a 208 linhas por arquivo, agregando os arquivos disponíveis para até 30 amostras.
5. **Colunas do CSV:** para `s1_0-eth1`, o plotter utiliza a quarta coluna; para as demais interfaces selecionadas, utiliza a terceira coluna.

As notas descrevem o comportamento do código atualmente versionado. Os arquivos e resultados originais permanecem preservados.

## 8. Preservação

Manter os conjuntos de capturas originais, CSVs derivados e gráfico original. Para qualquer reprocessamento, registrar hashes, ambiente, versão dos scripts, comandos, parâmetros e arquivos resultantes. A existência do gráfico não comprova, isoladamente, que todos os valores foram reproduzidos a partir dos dados brutos.

## Referências

- SANTOS, G. O. et al. *MTS-PolKA: Weighted Multipath Traffic Splitting With Source Routing for Elephant and Mice Flows*. International Journal of Network Management, v. 35, n. 3, e70016, 2025. [DOI 10.1002/nem.70016](https://doi.org/10.1002/nem.70016).
- [Artigo PDF](../IJNM_MTS_Polka.pdf).
- [Implementação MTS-PolKA](../../m-polka/).
