import matplotlib.pyplot as plt
import numpy

run=1
test = 1
taxa = 100
#csv output format: Type rate:
#unix timestamp;iface_name;bytes_out/s;bytes_in/s;bytes_total/s;bytes_in;bytes_out;packets_out/s;packets_in/s;packets_total/s;packets_in;packets_out;errors_out/s;errors_in/s;errors_in;errors_out\n

plt.rc('font', size=16)
plt.rc('axes', titlesize=16)
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=10)
plt.rc('figure', titlesize=16)

x = []
y = []
for sample in range(1, 4):
    
	arq=f"run/data/a{sample}.csv"
	test = test+1
	print(arq)
	f=open(arq)
	linhas=f.readlines()
	f.close()

	cont=1
	for dado in linhas:
		if sample == 1:
			x.append(cont)
			y.append([])
		b=dado.split(',')[2]
		fb=float(b)/1024/1024*8
		y[cont-1].append(fb)
		cont=cont+1
		if cont > 177:
			break
m=[]
d=[]
for cont in range(0,len(y)):
	m.append(numpy.mean(y[cont]))
	#d.append(numpy.std(y[cont]))
#plt.errorbar(x,m,yerr=d, fmt='-', linewidth=1, color='red')
plt.plot(x, m, linewidth=2, marker='o', markersize=3, color='blue')
print(f'a{sample}: OK')
plt.xlabel('Tempo (s)') 
plt.ylabel('Vazão (Mbps)') 
plt.title(f'Reação da migração de perfis')
plt.savefig(f'data/run/{taxa}.png')
plt.clf()