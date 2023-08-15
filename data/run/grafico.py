import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy

run=1
#csv output format: Type rate:
#  0 unix timestamp
#  1 interface
#  2 bytes_out/s
#  3 bytes_in/s
#  4 bytes_total/s
#  5 bytes_in
#  6 bytes_out
#  7 packets_out/s
#  8 packets_in/s
#  9 packets_total/s
# 10 packets_in
# 11 packets_out
# 12 errors_out/s
# 13 errors_in/s
# 14 errors_in
# 15 errors_out 

taxas = [ 40 ]
samples = 20

linkname=['MIA-SAO','CHI-AMS','MIA-CHI','MIA-CAL','','host2']
colors=['#F6D32D','blue','red','green','','purple']

plt.rc('font', size=16)
plt.rc('axes', titlesize=16)
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=10)
plt.rc('figure', titlesize=16)
for taxa in taxas:
	print(f'Taxa: {taxa}mb')
	y=[[],[],[],[],[]]
	contr = 0
	for router in [ 2, 3, 4, 5, 7]:
		x=[]
		for sample in range(1, samples+1):
			arq=f'iperf_output.csv'
			f=open(arq)
			linhas=f.readlines()
			f.close()

			cont=1
			for dado in linhas:
				if cont < 96:
					if sample == 1:
						x.append(cont)
						y[contr].append([])
					b=dado.split(',')[3]
					fb=float(b)/1024/1024*8
					y[contr][cont-1].append(fb)
					cont=cont+1
		m=[]
#		print('contr:',contr)
		for cont in range(0,len(y[contr])):
			m.append(numpy.mean(y[contr][cont]))
		if linkname[router-2] == "host2":
			#plt.plot(x, m, linestyle='--', linewidth=1, marker='o', markersize=2, label=linkname[router-2], color=colors[router-2])
			plt.plot(x, m, linestyle='--', linewidth=2, label=linkname[router-2], color=colors[router-2])
		else:
			#plt.plot(x, m, linewidth=1, marker='o', markersize=2, label=linkname[router-2], color=colors[router-2])
			plt.plot(x, m, linewidth=2, label=linkname[router-2], color=colors[router-2])
		#plt.plot(x, m, label=linkname[router-2], color=colors[router-2])
		contr = contr+1

	plt.yscale('linear')
	plt.xlabel('Tempo (s)')
	plt.ylabel('Vazão (Mbps)') 
	#plt.legend(title='Link:', bbox_to_anchor=(1.05, 1.0), loc='upper left')
	#plt.tight_layout()
	plt.legend(loc='upper left')
	plt.title('Agregação de fluxos com uso de políticas')
	print(f'Sample {sample}: OK')
	plt.savefig(f'results/run{run}/{taxa}.png')
	plt.clf()

