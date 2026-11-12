# IJNM experimental artifacts — MTS-PolKA

Este diretório reúne os artefatos experimentais associados ao artigo *MTS-PolKA: Weighted Multipath Traffic Splitting With Source Routing for Elephant and Mice Flows*.

## 1. Referência primária e critério de organização

A referência primária para identificar, organizar e descrever os experimentos é o próprio artigo, especificamente a **Seção 4 — “Experimental Evaluation”**:

- [Artigo completo — IJNM_MTS_Polka.pdf](IJNM_MTS_Polka.pdf)
- [Versão publicada na Wiley — DOI: 10.1002/nem.70016](https://doi.org/10.1002/nem.70016)

Os quatro experimentos devem ser apresentados na ordem e com os objetivos definidos nas subseções 4.1 a 4.4 do artigo. A subseção 4.5 (“Prototype Limitations”) documenta limitações do protótipo e não constitui um quinto experimento.

A dissertação de mestrado pode ser consultada como fonte complementar. Ela não substitui a organização, a nomenclatura, a metodologia nem os resultados publicados no artigo. Quando houver divergência entre artigo, dissertação, scripts, configurações, logs, CSVs ou figuras, a divergência deve permanecer registrada como pendência de auditoria até ser esclarecida.

### Hierarquia e natureza das evidências

| Fonte | Papel no inventário | O que pode sustentar |
|---|---|---|
| Artigo IJNM, Seção 4 e Apêndice A | Referência primária | Organização, objetivos, metodologia, cenários, métricas, resultados publicados e configurações descritas no artigo |
| Scripts em `IJNM/` | Evidência de implementação | Procedimentos codificados, comandos, parâmetros, temporização, caminhos de entrada e saída |
| Configurações em `IJNM/` e `m-polka/` | Evidência de configuração | Topologias, perfis, regras, identificadores e parâmetros efetivamente registrados nos arquivos |
| Logs, CSVs e resultados armazenados | Evidência de execução | Saídas preservadas das execuções, desde que sua origem e integridade sejam identificadas |
| Dissertação | Fonte complementar | Contexto adicional e elementos para confronto, sem reorganizar os experimentos do artigo |

A presença de um script ou arquivo de resultado no repositório não comprova, isoladamente, que ele reproduz integralmente uma figura ou resultado do artigo. Essa correspondência exige rastreabilidade entre versão do script, configuração, execução, dado bruto, método de processamento e resultado publicado.

## 2. Organização dos experimentos conforme a Seção 4

O artigo descreve quatro experimentos. A tabela abaixo reproduz sua organização e relaciona os diretórios existentes no repositório. Os caminhos são referências aos artefatos encontrados na estrutura documentada deste diretório; a associação não certifica, por si só, que todos os dados foram reconciliados com as figuras publicadas.

| Referência no artigo | Objetivo e métrica publicados | Artefatos associados no repositório |
|---|---|---|
| **4.1 — Test 1: Functional Validation** | Demonstrar diferentes perfis de divisão de tráfego com pacotes UDP. Métrica: contagem total de pacotes UDP recebidos em cada porta dos switches. | `test1/run_test1.py`, `test1/conf/`, `test1/data/`, `test1/result/` |
| **4.2 — Test 2: Agile Reconfiguration** | Avaliar a reconfiguração ágil dos perfis de um fluxo e observar sua estabilidade durante as transições. Métrica: vazão média registrada nos switches core selecionados durante cada fase. | `test2/run_test-2.py`, `test2/conf/`, `test2/data/`, `test2/result/`, `test2/plotter_test-2.py` |
| **4.3 — Test 3: Multiple Flows and Competition** | Demonstrar fluxos concorrentes e migração ágil de perfil para otimizar o uso dos recursos. Métricas: vazão dos fluxos em múltiplos destinos e vazão agregada na origem. | `test3/run_test-3.py`, `test3/conf/`, `test3/data/`, `test3/result/`, `test3/grafico-test-3.py` |
| **4.4 — Test 4: Comparison With Related Works on Flow Completion Time for Elephant Flows and Latency Analysis for Mice Flows** | Comparar MTS-PolKA com ECMP, WCMP e RPS em cenários com elephant e mice flows. Métricas indicadas na Tabela 2: FCT e retransmissões TCP para elephant flows; latência média para mice flows. | `test4/scenario/`, `test4/mts-polka/`, `test4/related_works/` |

### 2.1 Seção 4.1 — Test 1: Functional Validation

O artigo descreve a aplicação dos perfis 0, 100 e 1011 na origem, em S1_0, enquanto os demais switches mantêm o Perfil 0 no cenário descrito. As Figuras 11, 12 e 13 apresentam, respectivamente, os cenários/resultados dos perfis 0, 100 e 1011.

- **Referência publicada:** Seção 4.1; Figuras 11, 12 e 13; Tabela 2; Apêndice A, Tabela A4.
- **Artefatos a rastrear:** `test1/run_test1.py`, arquivos de configuração em `test1/conf/`, capturas em `test1/data/` e resultados em `test1/result/`; configurações de switches em `m-polka/`, quando referenciadas pelo script.
- **Verificação necessária:** relacionar os parâmetros e comandos do script às configurações de cada perfil e aos dados usados para produzir as Figuras 11–13.
- **Pendência já identificada:** o comando de monitoramento em `test1/run_test1.py` contém a grafia `packtes`. A opção válida do `bwm-ng` deve ser verificada na versão efetivamente utilizada antes de qualquer nova execução. Não alterar a captura histórica.

### 2.2 Seção 4.2 — Test 2: Agile Reconfiguration

O artigo descreve três fases de 10 segundos: Perfil 0, seguido do Perfil 100 e, por fim, do Perfil 1011. A alteração é realizada na entrada do fluxo no switch de borda, com captura de tráfego nas portas ativas dos switches S2_0, S2_2 e S1_1. A Figura 14 apresenta o resultado publicado.

- **Referência publicada:** Seção 4.2; Figura 14; Tabela 2; Apêndice A, Tabela A4.
- **Artefatos a rastrear:** `test2/run_test-2.py`, `test2/conf/`, `test2/data/`, `test2/result/` e `test2/plotter_test-2.py`.
- **Verificação necessária:** confrontar os instantes de alteração dos perfis, a duração das fases, os pontos de captura e o cálculo da vazão média com a descrição do artigo e a Figura 14.
- **Pendências já identificadas:**
  1. O script grava a captura de monitoramento em `data/run2/`, enquanto os comandos de extração e o plotter consultam `data/run/`. A divergência de caminhos deve ser corrigida somente em uma cópia versionada do script.
  2. O `test2/README.md` cita `plotter-test-2.py`, mas o arquivo presente é `plotter_test-2.py`.

### 2.3 Seção 4.3 — Test 3: Multiple Flows and Competition

O artigo descreve três fluxos concorrentes: TCP H1–H2 (tcp1), TCP H1–H5 (tcp2) e UDP H3–H4 (udp1), este último a 4 Mbps. Entre 0 e 10 segundos, tcp1 utiliza um caminho com Perfil 0, tcp2 utiliza Perfil 1 em dois caminhos e udp1 utiliza Perfil 0. Entre 10 e 20 segundos, tcp1 é migrado para Perfil 1 e passa a utilizar dois caminhos anteriormente ociosos. As Figuras 15 e 16 apresentam, respectivamente, o cenário e os resultados.

- **Referência publicada:** Seção 4.3; Figuras 15 e 16; Tabela 2; Apêndice A, Tabela A4.
- **Artefatos a rastrear:** `test3/run_test-3.py`, `test3/conf/`, `test3/data/`, `test3/result/` e `test3/grafico-test-3.py`.
- **Verificação necessária:** relacionar cada fluxo, destino, perfil, caminho, instante de migração e série de vazão às Figuras 15 e 16.
- **Pendências já identificadas:**
  1. Há comandos de cliente TCP com o parâmetro `-b` sem valor explícito antes de `-w`. O valor pretendido deve ser estabelecido por evidência antes de qualquer correção.
  2. A duração e a sequência efetivas dos comandos do script devem ser confrontadas com a janela de 0 a 20 segundos descrita no artigo. Não presumir equivalência sem examinar os tempos de execução e os logs.

### 2.4 Seção 4.4 — Test 4: Comparison With Related Works

O artigo compara MTS-PolKA, ECMP, WCMP e RPS em um cenário com fluxos elephant e mice. O cenário descrito inclui atraso de 1 ms, enlaces core de 1 Mbps e enlaces edge de 10 Mbps; dois elephant flows TCP de 100 MB e mice flows TCP de 10 KB, com taxa indicada de quatro fluxos por segundo. A Figura 17 apresenta o cenário MTS-PolKA; a Figura 18 apresenta a comparação de FCT; e a Figura 20 apresenta a comparação de latência.

- **Referência publicada:** Seção 4.4; Figuras 17, 18 e 20; Tabela 2; Apêndice A, Tabelas A1–A4.
- **Artefatos MTS-PolKA:** `test4/mts-polka/conf_profile/`, `test4/mts-polka/fct_test/`, `test4/mts-polka/latency_test/`, `test4/mts-polka/retransmission/`, `test4/mts-polka/run_test-4.py` e os plotters presentes no diretório.
- **Artefatos de comparação:** `test4/related_works/ecmp/`, `test4/related_works/wcmp/` e `test4/related_works/rps/`. Devem ser tratados separadamente dos artefatos de implementação do MTS-PolKA.
- **Verificação necessária:** rastrear separadamente FCT, retransmissões TCP e latência; identificar os arquivos brutos e o procedimento de cálculo de cada métrica. Não atribuir a um plotter o cálculo de uma métrica que ele apenas representa ou não processa.
- **Pendências já identificadas:**
  1. `test4/mts-polka/README.md` cita `run_test.py`, enquanto o arquivo presente é `run_test-4.py`; também há divergência de grafia no diretório de latência.
  2. `run_test-4.py` grava logs de ping em `latency_test/data/run/`, enquanto `plotter_latency.py` consulta `latency_test/data/run3/`.
  3. `plotter_fct.py` deve ser inspecionado quanto à métrica efetivamente calculada: a existência do nome “fct” não comprova que o script derive FCT. O cálculo deve ser rastreado até logs de início/fim ou resumos do iperf, com método explicitado.
  4. `plotter_retransmission.py` espera arquivos denominados `ecmp.txt`, `wcmp.txt`, `rps.txt` e `mts-polka.txt`. A origem, integridade e correspondência desses arquivos com as execuções comparativas precisam ser verificadas.
  5. A rotina de geração de mice flows e a distribuição temporal dos intervalos entre fluxos devem ser comparadas com a descrição do artigo. Não substituir a distribuição documentada por outra interpretação sem evidência.
  6. Retransmissões TCP não devem ser apresentadas como medição direta de reordenação de pacotes. São métricas distintas.

## 3. Configuração experimental — Apêndice A

O Apêndice A integra a referência primária de configuração dos experimentos. Sua rastreabilidade deve ser mantida separada da descrição dos resultados:

| Elemento publicado | Referência no artigo | Evidência a confrontar no repositório |
|---|---|---|
| Identificadores dos switches core (`nodeIDs`) | Tabela A1 | Configurações P4 e arquivos de configuração dos experimentos |
| Perfis estáticos (`table static profiles`) | Tabela A2 | Entradas de configuração das tabelas nos switches core |
| Distribuição por posição de porta (`table multipath`) | Tabela A3 | Entradas de configuração e lógica P4 |
| Identificadores por experimento (`profileIDs`, `routeIDs`, `weightIDs`, `portIDs`) | Tabela A4 | Scripts de cálculo, comandos de configuração e regras nos switches edge/core |

O artigo informa que os cálculos polinomiais/RNS utilizam biblioteca Python com o pacote `galoistools` da biblioteca SymPy e que a aplicação do plano de controle interage com os switches por meio da CLI do `bmv2 simple_switch` e da porta Thrift RPC. A configuração estática dos switches core é apresentada no Apêndice A. Esses elementos devem ser conferidos com os arquivos efetivamente presentes, sem presumir que todo cálculo esteja implementado em um único script.

## 4. Limitações do protótipo — Seção 4.5

A Seção 4.5 do artigo deve ser usada como contexto para interpretar os resultados, não como experimento adicional. O artigo registra limitações relacionadas ao uso do `bmv2 simple_switch` com arquitetura `v1model`, à capacidade de processamento do switch em software, à ausência de uma avaliação mais profunda de desempenho e escalabilidade em dispositivos físicos e ao fato de monitoramento, escalonamento de fluxos, filas e alocação de caminhos terem sido considerados entradas predefinidas do plano de controle e estarem fora do escopo do trabalho.

Consequentemente, o inventário não deve descrever a avaliação em Mininet/BMv2 como validação em hardware físico. A possibilidade de validação futura em Tofino e ns-3 é apresentada no artigo como trabalho futuro.

## 5. Estrutura de arquivos documentada

```text
IJNM/
├── IJNM_MTS_Polka.pdf
├── README.md
├── scenario/
├── test1/
│   ├── conf/
│   ├── data/
│   ├── result/
│   ├── README.md
│   └── run_test1.py
├── test2/
│   ├── conf/
│   ├── data/
│   ├── result/
│   ├── README.md
│   ├── run_test-2.py
│   └── plotter_test-2.py
├── test3/
│   ├── conf/
│   ├── data/
│   ├── result/
│   ├── README.md
│   ├── run_test-3.py
│   └── grafico-test-3.py
└── test4/
    ├── scenario/
    ├── mts-polka/
    │   ├── conf_profile/
    │   ├── fct_test/
    │   ├── latency_test/
    │   ├── retransmission/
    │   ├── README.md
    │   ├── run_test-4.py
    │   ├── plotter_fct.py
    │   ├── plotter_latency.py
    │   └── plotter_retransmission.py
    └── related_works/
        ├── ecmp/
        ├── wcmp/
        └── rps/
```

O diretório `m-polka/`, com a implementação P4 e configurações dos switches, está fora de `IJNM/`, na raiz do repositório. A estrutura acima é a estrutura documentada; a presença, completude e conteúdo de cada arquivo devem ser verificados na auditoria de cada artefato.

## 6. Referências de execução

Os comandos abaixo indicam os nomes de scripts documentados no repositório. Não constituem, por si só, garantia de reprodução: antes de executá-los, conferir dependências, diretórios, parâmetros, arquivos de entrada e destino das saídas.

```sh
cd IJNM/test1
sudo python3 run_test1.py

cd ../test2
sudo python3 run_test-2.py
python3 plotter_test-2.py

cd ../test3
sudo python3 run_test-3.py
python3 grafico-test-3.py

cd ../test4/mts-polka
sudo python3 run_test-4.py
python3 plotter_fct.py
python3 plotter_latency.py
python3 plotter_retransmission.py
```

## 7. Pendências de auditoria e preservação

As divergências descritas neste README são achados preliminares e devem ser detalhadas na matriz `REVISAO_AUDITORIA/MATRIZ_PENDENCIAS_POR_ARQUIVO.md`, com identificação do arquivo, evidência observada, impacto, correção proposta, responsável e situação.

Regras obrigatórias:

1. Não sobrescrever nem substituir silenciosamente scripts, configurações, logs, CSVs, figuras ou resultados experimentais originais.
2. Corrigir scripts somente em cópias ou versões novas, identificadas e versionadas.
3. Para cada reprocessamento, registrar arquivos de entrada, hashes, versão do script, parâmetros, ambiente, comando executado, data, saída e método de cálculo.
4. Não substituir valores publicados no artigo por resultados recalculados sem apresentar a origem dos dados e explicar a diferença.
5. Não declarar um experimento reproduzido apenas porque o script foi executado; verificar a cadeia completa entre configuração, execução, dados brutos, processamento e resultado.
6. Manter divergências entre artigo, dissertação e artefatos como pendências até haver evidência suficiente para resolvê-las.

## 8. Situação do inventário

Este README organiza os artefatos conforme a Seção 4 do artigo e estabelece o mapa de rastreabilidade. **Não representa declaração de que todas as pendências foram sanadas nem certificação de reprodução integral dos resultados publicados.** O inventário permanece em estado de auditoria até que scripts, configurações, dados brutos e resultados sejam reconciliados.
