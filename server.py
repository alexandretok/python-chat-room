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
TIMEOUT = 20
ANTI_FLOOD_TIME_LIMIT = 2 # Tempo limite (em segundos)
ANTI_FLOOD_MSG_QTD = 5 # Quantidade de mensagens que podem ser enviada dentro do tempo limite

# Variaveis globais
listaClientes = []

# Configuracao do socket
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind(('', PORT))
listen_socket.listen(0)

def threadDoCliente(cliente):
	global listaClientes, TIMEOUT, ANTI_FLOOD_MSG_QTD, ANTI_FLOOD_TIME_LIMIT

	# Essa lista guarda o tempo de envio das ultimas 5 mensagens enviadas pelo cliente
	ultimasMensagens = Queue.Queue(ANTI_FLOOD_MSG_QTD)

	cliente.conn.send("Digite seu apelido: ")
	cliente.apelido = cliente.conn.recv(1024).replace("\r\n", "")
	
	broadcast(cliente.apelido + " entrou na sala.")

	# Configura um timeout para saber quando o cliente encerrou a conexao
	cliente.conn.settimeout(TIMEOUT)
	disconnected = False
	quintaUltima = None
	while not disconnected:
		try:
			msg = cliente.conn.recv(1024)

			# Se o cliente se desconectar inesperadamente, o socket recebe uma string vazia
			if msg == "":
				break

			msg = msg.replace("\r\n", "")

			if ultimasMensagens.full():
				quintaUltima = ultimasMensagens.get(False)

			if ultimasMensagens.qsize() == 4 and quintaUltima != None and (time.time() - quintaUltima) <= ANTI_FLOOD_TIME_LIMIT:
				print "Stop the flood!"
				cliente.conn.send("Stop the flood!\n")
			elif msg != "__heart_beat__": # A mensagem ___heart_beat___ serve apenas para nao dar timeout
				broadcast(cliente.apelido + " escreveu: " + msg)
				ultimasMensagens.put(time.time())
		except socket.timeout:
			disconnected = True

	cliente.conn.close()
	listaClientes.remove(cliente)
	broadcast(cliente.apelido + " saiu da sala.")

def recebeComandos():
	while True:
		global listaClientes
		var = raw_input("""
Lista de comandos:
 listar (ls): apresenta uma lista dos usuarios conectados no momento

""")
		if var == "listar" or var == "ls":
			if not len(listaClientes):
				print "Nenhum cliente conectado."
			for cliente in listaClientes:
				print "<" + (cliente.apelido if hasattr(cliente, "apelido") else "_EMPTY_") + ", " + str(cliente.addr[0]) + ", " + str(cliente.addr[1]) + ">"
	

# Envia uma string para todos os clientes conectados
def broadcast(string):
	global listaClientes
	now = datetime.datetime.now();
	for cliente in listaClientes:
		try:
			cliente.conn.send(str(now.hour) + ":"+ str(now.minute) + ":" + str(now.second) + " - " + string + "\n");
		except:
			time.sleep(0)

# Main loop

threadID = 0
threading.Thread(target=recebeComandos).start()

while True:
	# Fica preso aqui enquanto nao receber uma nova conexao
	client_connection, client_address = listen_socket.accept()

	tmp = Object()
	tmp.id = threadID
	tmp.conn = client_connection
	tmp.addr = client_address

	listaClientes.append(tmp)
	
	# Cria e inicia nova thread
	threading.Thread(target=threadDoCliente, args=(tmp,)).start()
	
	# Incrementa ID
	threadID += 1