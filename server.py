import socket
import datetime
import threading
import Queue
import time

# Pequena gambiarra para possibilitar um objeto generico
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

def threadDoCliente(cliente):
	global listaClientes

	# Guarda o tempo de envio das ultimas 5 mensagens enviadas pelo cliente
	ultimasMensagens = Queue.Queue(5)

	print str(len(listaClientes)) + " clientes conectados"

	cliente.conn.send("Digite seu apelido: ")
	cliente.apelido = cliente.conn.recv(1024).replace("\r\n", "")
	
	broadcast(cliente.apelido + " entrou na sala.")

	# Configura um timeout para saber quando o cliente encerrou a conexao
	cliente.conn.settimeout(20)
	disconnected = False
	quintaUltima = None
	while not disconnected:
		try:
			msg = cliente.conn.recv(1024).replace("\r\n", "")

			if ultimasMensagens.full():
				quintaUltima = ultimasMensagens.get(False)

			if ultimasMensagens.qsize() == 4 and quintaUltima != None and (time.time() - quintaUltima) <= 2:
				print "Stop the flood!"
				cliente.conn.send("Stop the flood!")
			elif msg != "___heart_beat___": # A mensagem ___heart_beat___ serve apenas para nao dar timeout
				broadcast(cliente.apelido + " escreveu: " + msg)
				print "mensagem recebida em " + str(time.time())
				ultimasMensagens.put(time.time())
		except socket.timeout:
			disconnected = True

	cliente.conn.close()
	listaClientes.remove(cliente)
	broadcast(cliente.apelido + " saiu da sala.")
	print str(len(listaClientes)) + " clientes conectados"

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
	threading.Thread(target=threadDoCliente, args=(tmp,)).start()
	
	# Incrementa ID
	threadID += 1