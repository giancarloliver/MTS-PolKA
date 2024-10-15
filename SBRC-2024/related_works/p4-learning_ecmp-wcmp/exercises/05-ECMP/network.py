from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

edges = []
hosts = []

BW = 10
BWE = 100

# Network general options
net.setLogLevel('info')

# Network definition
net.addP4Switch('s10', cli_input='sw-commands/s10-commands.txt')
net.addP4Switch('s20', cli_input='sw-commands/s20-commands.txt')
net.addP4Switch('s21', cli_input='sw-commands/s21-commands.txt')
net.addP4Switch('s22', cli_input='sw-commands/s22-commands.txt')
net.addP4Switch('s23', cli_input='sw-commands/s23-commands.txt')
net.addP4Switch('s24', cli_input='sw-commands/s24-commands.txt')
net.addP4Switch('s11', cli_input='sw-commands/s11-commands.txt')
net.addP4Switch('e1', cli_input='sw-commands/e1-commands.txt')
net.addP4Switch('e2', cli_input='sw-commands/e2-commands.txt')
net.setP4SourceAll('p4src/ecmp.p4')


net.addHost('h1')
net.addHost('h2')

# Conexões entre switches e hosts
net.addLink("h1", "e1", port2=1, bw=BWE)
net.addLink("e1", "s10", port1=2, bw=BWE)

net.addLink("h2", "e2", port2=1, bw=BWE)
net.addLink("e2", "s11", port1=2, bw=BWE)

# Conexões entre switches
net.addLink("s10", "s20", bw=BW)
net.addLink("s10", "s21", bw=BW)
net.addLink("s10", "s22", bw=BW)
net.addLink("s10", "s23", bw=BW)
net.addLink("s10", "s24", bw=BW)
net.addLink("s20", "s11", bw=BW)
net.addLink("s21", "s11", bw=BW)
net.addLink("s22", "s11", bw=BW)
net.addLink("s23", "s11", bw=BW)
net.addLink("s24", "s11", bw=BW)

# Assignment strategy
net.mixed()

# Nodes general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()