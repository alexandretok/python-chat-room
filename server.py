import socket
import datetime
import threading

class Object(object):
    pass

# Constantes
PORT = 6666

# Variaveis globais
listaClientes = []

# Configura socket
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind(('', PORT))
listen_socket.listen(0)

def configuracaoNovoCliente(cliente):
	global listaClientes

	cliente.conn.send("Digite seu apelido: ");
	cliente.apelido = cliente.conn.recv(1024).replace("\r\n", "")
	broadcast(cliente.apelido + " entrou na sala.")

	# Configura um timeout para saber quando o cliente encerrou a conexao
	cliente.conn.settimeout(10)
	disconnected = False
	while not disconnected:
		try:
			msg = cliente.conn.recv(1024).replace("\r\n", "")
		except socket.timeout:
			disconnected = True

	cliente.conn.close()
	listaClientes.remove(cliente)
	broadcast(cliente.apelido + " saiu da sala.")

# Envia uma string para todos os clientes conectados
def broadcast(string):
	global listaClientes
	now = datetime.datetime.now();
	for cliente in listaClientes:
		cliente.conn.send(str(now.hour) + ":"+ str(now.minute) + ":" + str(now.second) + " - " + string + "\n");

# Main loop

threadID = 0

while True:
	# Fica preso aqui enquanto nao receber uma nova conexao
	client_connection, client_address = listen_socket.accept()

	tmp = Object()
	tmp.id = threadID
	tmp.conn = client_connection

	listaClientes.append(tmp)
	
	# Cria e inicia nova thread
	threading.Thread(target=configuracaoNovoCliente, args=(tmp,)).start()
	
	# Incrementa ID
	threadID += 1