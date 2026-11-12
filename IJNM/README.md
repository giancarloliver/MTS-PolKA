# Artefatos experimentais do artigo MTS-PolKA

Este diretório reúne scripts, configurações, dados e resultados associados à avaliação experimental do MTS-PolKA publicada no *International Journal of Network Management*.

## Referência primária

A organização dos quatro experimentos segue a **Seção 4 — Experimental Evaluation** do artigo:

- [Artigo PDF](IJNM_MTS_Polka.pdf)
- [Artigo publicado — DOI: 10.1002/nem.70016](https://doi.org/10.1002/nem.70016)
- [Repositório de implementação](https://github.com/giancarloliver/MTS-PolKA)

A dissertação de mestrado de 2024 é fonte complementar. Não substitui a nomenclatura, a organização nem os resultados publicados no artigo. Divergências entre artigo, dissertação, scripts, configurações, logs, CSVs e figuras devem permanecer registradas como pendências até serem resolvidas por evidências.

## Organização dos experimentos

| Artigo | Experimento | Objetivo e métricas conforme o artigo | Diretório |
|---|---|---|---|
| Seção 4.1 | **Test 1 — Functional Validation** | Aplicar diferentes perfis de divisão de tráfego a pacotes UDP. Métrica: contagem total de pacotes UDP recebidos em cada porta dos switches. | [test1/](test1/README.md) |
| Seção 4.2 | **Test 2 — Agile Reconfiguration** | Alternar três perfis para um único fluxo, modificando uma entrada no switch edge. Métrica: vazão média nos switches core selecionados durante cada fase. | [test2/](test2/README.md) |
| Seção 4.3 | **Test 3 — Multiple Flows and Competition** | Demonstrar fluxos concorrentes e migração ágil de perfil. Métricas: vazão dos fluxos nos destinos e vazão agregada na origem. | [test3/](test3/README.md) |
| Seção 4.4 | **Test 4 — Comparison With Related Works on Flow Completion Time for Elephant Flows and Latency Analysis for Mice Flows** | Comparar MTS-PolKA, ECMP, WCMP e RPS para elephant e mice flows. Métricas publicadas: FCT dos elephant flows e latência de caminho dos mice flows. | [test4/mts-polka/](test4/mts-polka/README.md) |

A Seção 4.5 do artigo trata das limitações do protótipo; não é um quinto experimento.

## Fontes e força das evidências

| Fonte | O que documenta | Limite de interpretação |
|---|---|---|
| Artigo, Seção 4 | Objetivos, cenários, procedimentos descritos, métricas e resultados publicados | Não comprova que os arquivos atuais reproduzam integralmente cada resultado |
| Artigo, Apêndice A | nodeIDs, perfis estáticos, tabela multipath e identificadores dos experimentos | Deve ser confrontado com as configurações versionadas |
| Scripts Python | Comandos, parâmetros, temporização, caminhos de arquivos e processamento implementado | Código existente não comprova execução bem-sucedida |
| Configurações P4/CLI | Tabelas, perfis, regras e parâmetros instalados | Precisam ser vinculadas ao experimento e à execução correspondente |
| Logs, CSVs e resultados | Evidências de execução, se preservados e identificados | Exigem origem, integridade, versão e vínculo com os scripts |
| Dissertação | Contexto acadêmico e descrição complementar | Não deve prevalecer automaticamente sobre o artigo em caso de divergência |

A cadeia de rastreabilidade esperada é: **artigo/figura → experimento → script → configuração → execução → dado bruto → processamento → resultado**.

## Mapa dos artefatos

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

A implementação P4 e as configurações centrais usadas pelos scripts estão em [m-polka/](../m-polka/), fora de IJNM.

## Notas técnicas sobre os artefatos versionados

1. **Test 1:** o script usa os valores decimais 0, 4 e 11 para identificar os perfis representados em binário no artigo como 0, 100 e 1011. O comando bwm-ng contém a grafia “packtes”; a opção/unidade deve ser validada na versão da ferramenta antes de nova execução.
2. **Test 2:** o runner grava a captura em data/run2/, mas os comandos de extração e o plotter consultam data/run/. O nome correto do plotter é plotter_test-2.py.
3. **Test 3:** o comando dos clientes TCP contém -b sem valor explícito antes de -w; o valor pretendido não deve ser adivinhado. O runner aguarda 10 segundos e depois 22 segundos, o que deve ser confrontado com a janela temporal descrita no artigo e com os logs.
4. **Test 4:** o runner grava os logs de ping em latency_test/data/run/, enquanto o plotter de latência lê latency_test/data/run3/. O plotter_fct.py lê CSVs de bwm-ng e plota vazão por interface; não calcula FCT a partir de tempos de início e término. O script de retransmissões é um artefato adicional do repositório, mas retransmissões não são uma das duas métricas explicitamente apresentadas na descrição do Test 4 do artigo.

As observações acima descrevem o comportamento dos artefatos atualmente versionados. Elas não alteram os resultados publicados nem autorizam a substituição de dados históricos. Qualquer ajuste futuro deverá preservar os arquivos originais e ser identificado em versão própria.

## Limitações da avaliação

A avaliação descrita no artigo foi realizada com Mininet e switches BMv2/P4. Os resultados não devem ser apresentados como validação em hardware físico. As limitações de desempenho do switch em software e o escopo do plano de controle devem ser considerados na interpretação. O artigo aponta avaliação em hardware programável, análise de reordenação e estudos adicionais de escalabilidade como trabalhos futuros.

## Preservação e reprodução

- Não sobrescrever nem substituir silenciosamente scripts, configurações, logs, CSVs, figuras ou resultados originais.
- Corrigir scripts apenas em novas cópias/versões identificadas.
- Registrar hashes dos arquivos de entrada, versão do script, parâmetros, ambiente, comando, data e saídas de cada reprocessamento.
- Não declarar reprodução integral apenas porque um script foi iniciado ou executado.
- Não substituir resultados publicados por valores recalculados sem documentar a origem dos dados e explicar as diferenças.
- Manter divergências entre artigo, dissertação e artefatos como pendências até haver evidência suficiente.

**Situação documental:** este diretório funciona como inventário e mapa de rastreabilidade. Não certifica que todos os experimentos tenham sido reproduzidos nem que todas as pendências tenham sido sanadas.
