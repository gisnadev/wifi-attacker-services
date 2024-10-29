from xmlrpc.client import ServerProxy
server = ServerProxy('http://localhost:9001/RPC2')
server.supervisor.getState()
scannerstatus= server.supervisor.getProcessInfo('scanner')
print(scannerstatus)