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
1. Download e instalação da VM:
   [[6.7GB Size] - Lubuntu 20.04 x64](https://drive.google.com/file/d/1oozRqFO2KjjxW0Ob47d6Re4i6ay1wdwg/view?usp=sharing) - Mininet-WiFi com P4 (_pass: wifi_).
   - Após o download, acesse a VM com as seguintes credenciais: user: wifi, pass: wifi
3. Clone do GitHub:
```sh
$ git clone https://github.com/rafaelsilvag/m-polka.git
```
```sh
$ make
```  
4. Executar topologia:
```sh
$ sudo python3 run_linear_topology.py
``` 
5. Instalação da lib polka-routing: $ python3 -m pip install polka-routing --user
  Ao instalar a lib, apareceu os alertas:
  Installing collected packages:  
  WARNING: The script isympy is installed in '/home/wifi/.local/bin' which is not on PATH. Consider adding this directory to PATH or, if you prefer to suppress this warning,   use --no-warn-script-location.                  
  Successfully installed mpmath-1.2.1 networkx-2.6.3 pandas-1.3.4 polka-routing-0.2.2 pytz-2021.3 sympy-1.9
  WARNING: You are using pip version 20.2.3; however, version 21.3 is available. You should consider upgrading via the '/usr/bin/python3 -m pip install --upgrade pip'         command.

## Observações:
- Para visualizar os logs, basta executar o código em um novo termina-<nome_switch>-log, como por exemplo, tail -f /tmp/bmv2-s1-log.
- Qualquer alteração realizada nos códigos do projeto, executar o comando make, para compilar o programa com as alterações realizadas.


## 1) Passo a passo da execução básica 

Para compilar os códigos P4 MTS-PolKA, você deve executar o seguinte comando:
```sh
$ cd m-polka/m-polka
$ make
$ cd ..
``` 
É importante notar que para cada modificação, temos que recompilar usando o comando anterior.

Gerar o routeid e o wid:
```sh
$ python3 calc_routeid.py
```

Para criar a topologia usando o Mininet, devemos executar o seguinte comando:
```sh
$ sudo python3 run_linear_topology.py
```

Definição dos rótulos que serão usados por cada nó de núcleo para determinar o estado das portas de saída e perfis de divisão de tráfego correspondentes. Cada nó de núcleo possui duas tabelas estáticas com perfis de tráfego pré-definidos, que são selecionados a partir de operações com os rótulos routeID e wID de cada pacote.

```python
#!/usr/bin/env python3
from polka.tools import calculate_routeid, print_poly
DEBUG=False

def _main():
    print("Insering irred poly (node-ID)")
    s = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], # s1
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1], # s2
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1], # s3
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], # s4
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1], # s5
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], # s6
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1], # s7
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1], # s8
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1], # s9
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1], # s10
    ]
    print("From h1 to h2 ====")
    # defining the nodes from h1 to h2
    nodes = [
        s[0],
        s[1],
        s[2]
        s[4],
	      s[5],
	      s[6],
    ]
    # defining the transmission state for each node from h1 to h2
    o = [
        [1, 1, 0, 1, 1, 0],     # s1   
	      [1, 0],  # s2
        [1, 0],  # s3
	      [1, 0],	# s5	
	      [1, 0],	#s6
	      [0, 0, 0, 0, 0, 1], # s7
    ]
	print_poly(calculate_routeid(nodes, o, debug=DEBUG))
    
    print("From wid h1 to h2 ====")
    # defining the nodes from h1 to h2
    nodes = [
        s[0],
        s[1],
        s[2]
        s[4],
	      s[5],
	      s[6],
    # defining the transmission weight for each node from h1 to h2
    w = [
        [0, 0, 1, 0, 1, 1],     # s1
        [0, 0],  # s2
        [0, 0],  # s3
	      [0, 0],	# s5	
	      [0, 0], # s6
        [0, 0, 0, 0, 0, 0, 0, 0],  # s7
    ]
    print("wid h1 to h2 ====")
    print_poly(calculate_routeid(nodes, w, debug=DEBUG))

    print("From h1 to h2 ====")
    # defining the nodes from h2 to h1
    nodes = [
        s[6],
        s[5],
        s[4],
	      s[2],
	      s[1],
	      s[0],
    ]


  # defining the transmission state for each node from h2 to h1
    o = [
        [1, 1, 0, 1, 1, 0],     # s7
	      [0, 1],  # s6
        [0, 1],  # s5
	      [0, 1],	# s4	
	      [0, 1], # s3
	      [0, 1], # s2        
	      [0, 0, 0, 0, 0, 1], # s1
    ]
    print("routeid h2 to h1 ====")
    print_poly(calculate_routeid(nodes, o, debug=DEBUG))

    print("From h1 to h2 ====")
    # defining the nodes from h1 to h2
    nodes = [
        s[6],
        s[5],
        s[4],
	      s[2],
	      s[1],
	      s[0],
    ]

   # defining the transmission weight for each node from h2 to h1
    w = [
        [0, 0, 1, 0, 1, 1],     # s7
	      [0, 0],  # s6
        [0, 0],  # s5
	      [0, 0],	# s4	
	      [0, 0], # s3
	      [0, 0], # s2        
	      [0, 0, 0, 0, 0, 0], # s1
    ]    
    print("wid h2 to h1 ====")
    print_poly(calculate_routeid(nodes, w, debug=DEBUG)) 
         
if __name__ == '__main__':
    _main()
```



Execute o arquivo calc_routeid-wid.py e obtenha o novo número do routeID wID calculado de h1 para h2.

```sh
m-polka $ python3 calc_routeid.py
Insering irred poly (node-ID)
From h1 to h2 ====
routeid h1 to h2 ====
S=  [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1]]
O=  [[1, 1, 0, 1, 1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [0, 0, 0, 0, 0, 1]]
Len:  96
Poly (list):  [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1]
Poly (int):  73817044396459291349659850249
Poly (bin):  0b111011101000010000000111001010110000111000010100110010101011001010111100000100101001011000001001
Poly (hex):  0xee84072b0e14cab2bc129609
From h1 to h2 ====
wid h1 to h2 ====
S=  [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1]]
O=  [[0, 0, 1, 0, 1, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]
Len:  95
Poly (list):  [1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0]
Poly (int):  37823969743312635090392551816
Poly (bin):  0b11110100011011101000001001001000110001011100011000100100001010111110001000001111001000110001000
Poly (hex):  0x7a37412462e31215f1079188
From h1 to h2 ====
routeid h2 to h1 ====
S=  [[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1]]
O=  [[1, 1, 0, 1, 1, 0], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 0, 0, 0, 0, 1]]
Len:  92
Poly (list):  [1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1]
Poly (int):  4760175146147669529107217697
Poly (bin):  0b11110110000110000110010010111011111001000100111111111100100111000000111111011011110100100001
Poly (hex):  0xf61864bbe44ffc9c0fdbd21
From h1 to h2 ====
wid h2 to h1 ====
S=  [[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1]]
O=  [[0, 0, 1, 0, 1, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0, 0, 0, 0, 0]]
Len:  94
Poly (list):  [1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0]
Poly (int):  18446848090728087715511153268
Poly (bin):  0b1110111001101011100000000001101100011000011100100101001100110010001001100001100011001001110100
Poly (hex):  0x3b9ae006c61c94cc89863274
```

Depois de gerar o routeID para o estado das portas de saída e o wID para o perfis de divisão de tráfego de cada caminho, devemos adicionar o routeID e o wID apropriado relacionado ao destino. Por exemplo, para o destino "h2", a seguinte linha em "e1" (nó edge 1) deve ser modificada da seguinte forma:



```sh
m-polka $ cd m-polka/config/
m-polka/m-polka/config $ cat e1-commands.txt
```



Altere o arquivo e1-commands.txt, o routeID do 10.0.2.2/32 para 817044396459291349659850249 37823969743312635090392551816.:
```sh
default tunnel_encap_process_sr tdrop
table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.1.1/32 => 1 0 00:00:00:00:01:01 0 0
table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.2.2/32 => 2 1 00:00:00:00:02:02 73817044396459291349659850249 37823969743312635090392551816
```

Altere o arquivo e2-commands.txt, o routeID do 10.0.1.1/32 para 4760175146147669529107217697 18446848090728087715511153268.:
```sh
table_set_default tunnel_encap_process_sr tdrop
table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.2.2/32 => 1 0 00:00:00:00:02:02 0 0
table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.1.1/32 => 2 1 00:00:00:00:01:01 4760175146147669529107217697 18446848090728087715511153268
```

No terminal que estiver executando a topologia no Mininet, execute 1 ping de um host para outro, exemplo: h1 ping h2 -c 1 e analisar log para entender a execução.
Abra novo terminal para acompanhar os logs de execução:
Para verificar o nome do arquivo: 
$ cd ~
$ ls /tmp
$ tail -f /tmp/bmv2-<nome_switch>-log





