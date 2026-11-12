# Test 1 — Functional Validation

## 1. Objetivo

Conforme a Seção 4.1 do artigo, este experimento demonstra a funcionalidade da divisão de tráfego mediante a aplicação de diferentes perfis a pacotes UDP.

A métrica publicada é a **contagem total de pacotes UDP recebidos em cada porta dos switches**. O cenário aplica os perfis na origem, no switch core S1_0; os demais switches mantêm o Perfil 0, que encaminha o tráfego pela primeira porta ativa.

**Referência:** artigo IJNM, Seção 4.1 — *Functional Validation*, Figuras 11, 12 e 13, Tabela 2 e Apêndice A (Tabela A4).

## 2. Cenário e perfis

O runner configura dois switches edge, dois switches core de primeiro nível e cinco switches core de segundo nível, além dos hosts H1 e H2. O tráfego de teste é UDP, gerado com iperf3 a 10 Mbps, com tamanho total configurado em 100.000.000 bytes.

| Perfil no artigo (binário) | Identificador decimal no laço do script | Finalidade descrita |
|---|---:|---|
| 0 | 0 | Encaminhamento por uma porta ativa |
| 100 | 4 | Distribuição ponderada em múltiplas portas |
| 1011 | 11 | Distribuição ponderada em múltiplas portas |

Os valores 4 e 11 no script correspondem às representações binárias 100 e 1011. Para cada caso, o runner associa MAC, routeID e weightID à entrada tunnel_encap_process_sr do switch edge E1.

## 3. Arquivos

| Caminho | Função |
|---|---|
| run_test1.py | Cria a topologia, inicia monitoramento, instala a entrada do fluxo no edge e executa tráfego UDP para cada perfil |
| conf/ | Diretório reservado às configurações do experimento |
| data/ | Diretório destinado às capturas das execuções |
| result/ | Diretório destinado aos resultados e gráficos |

As configurações dos switches P4 referenciadas pelo script ficam em ../../m-polka/, fora deste diretório.

## 4. Execução

Executar a partir do diretório do experimento:

```sh
cd IJNM/test1
sudo python3 run_test1.py
```

O script limpa o estado anterior do Mininet, cria a topologia, inicia o servidor iperf3 em H2, inicia bwm-ng, instala a entrada de fluxo no edge E1, envia o fluxo UDP de H1 para H2 e encerra os processos. A saída de monitoramento é direcionada a data/run/<perfil>-tmp.bwm.

## 5. Resultados e interpretação

As Figuras 11, 12 e 13 do artigo são a referência para a apresentação dos três perfis. Deve-se confrontar a contagem de pacotes recebidos nas portas ativas com os perfis e identificadores do Apêndice A.

A proporção configurada não garante contagens inteiras exatamente iguais em toda execução finita. A validação deve confrontar os dados brutos com a distribuição prevista e com a configuração efetivamente instalada.

## 6. Notas sobre a implementação versionada

- **Monitoramento bwm-ng:** o runner contém o argumento `-u packtes` na chamada da ferramenta. Esta documentação descreve o código versionado, sem afirmar que a opção foi validada em uma instalação específica.
- **Saída de dados:** o runner grava as capturas em `data/run/`; esse diretório deve existir antes da execução.
- **Identificação dos dados:** os arquivos de captura devem ser interpretados em conjunto com o perfil executado, a configuração P4 e a figura do artigo correspondente.
- **Interfaces:** a interpretação das portas observadas deve considerar as configurações do Apêndice A, Tabela A4, e os arquivos de configuração efetivamente utilizados.

## 7. Preservação

Manter os dados e resultados originais sem alteração. Ajustes no runner, monitoramento ou processamento devem ocorrer em nova versão identificada, registrando dependências, parâmetros, comando, data e hashes.

## Referências

- SANTOS, G. O. et al. *MTS-PolKA: Weighted Multipath Traffic Splitting With Source Routing for Elephant and Mice Flows*. International Journal of Network Management, v. 35, n. 3, e70016, 2025. [DOI 10.1002/nem.70016](https://doi.org/10.1002/nem.70016).
- [Artigo PDF](../IJNM_MTS_Polka.pdf).
- [Implementação MTS-PolKA](../../m-polka/).
