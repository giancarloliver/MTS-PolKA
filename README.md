# MTS-PolKA: Divisão de tráfego multicaminho em proporção de peso com roteamento na fonte

O artigo apresenta a abordagem MTSPolKA para otimizar o tráfego em redes de data centers com múltiplos caminhos redundantes, visando equilibrar a carga de forma dinâmica e eficiente entre os caminhos para maximizar a largura de banda. A abordagem é baseada em roteamento de fonte multicaminho, permitindo que a fonte faça escolhas de distribuição usando rótulos nos pacotes. Isso possibilita a divisão dinâmica do tráfego sem reconfigurações complexas nas tabelas de comutação. Ao contrário de abordagens anteriores, a MTS-PolKA utiliza sistema numérico de resíduos para roteamento de fonte sem armazenamento de estado. Testes demonstram eficácia na distribuição de tráfego e melhorias em relação a abordagens convencionais. MTS-PolKA é uma solução inovadora para otimização do tráfego em redes de data centers, pois permite alterar a distribuição de tráfego de forma simultânea em todos os switches do caminho.


## Organização dos arquvivos

- \<data> - diretório onde são armazenados os dados adquiridos no experimento
- \<envio> - diretório onde os scripts de envio de mensagens.
- \<m-polka> - diretório onde estão os aruivos em p4 de configuração dos switches edges e core.
- \<topologia> - diretório onde estão os arquivos da topogia.
- calc_routeid-wid.py- calcula do routeid e wid das portas de transmissão.
- run_cenario_topology.py - executa o mininet com a topologia MTS-PolKA.

## Cenário

![](topologia/Cenario_MTS-PolKA-Cenario_WM-Polka-01.drawio.png)

## Execução iniciais
1. Download e instalação da VM
2. Clone do GitHub: $ git clone https://github.com/giancarloliver/MTS-PolKA.git   
3. make
4. Executar topologia: $ sudo python3 run_linear_topology.py
Não pingou de h1 para h2
5. Instalação da lib polka-routing: $ python3 -m pip install polka-routing --user
  Ao instalar a lib, apareceu os alertas:
  Installing collected packages:  
  WARNING: The script isympy is installed in '/home/wifi/.local/bin' which is not on PATH. Consider adding this directory to PATH or, if you prefer to suppress this warning,   use --no-warn-script-location.                  
  Successfully installed mpmath-1.2.1 networkx-2.6.3 pandas-1.3.4 polka-routing-0.2.2 pytz-2021.3 sympy-1.9
  WARNING: You are using pip version 20.2.3; however, version 21.3 is available. You should consider upgrading via the '/usr/bin/python3 -m pip install --upgrade pip'         command.

## Observações:
- Para visualizar os logs, basta executar o código em um novo termina-<nome_switch>-log, como por exemplo, tail -f /tmp/bmv2-s1-log.
- Qualquer alteração realizada nos códigos do projeto, executar o comando make, para compilar o programa com as alterações realizadas.




=======
# MTS-PolKA
>>>>>>> ba173979e91ff3814d336e6a6ffba071a9b868f8
