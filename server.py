import socket
import datetime
import threading
import Queue
import time
import readline
import re

# Pequena gambiarra para possibilitar um objeto generico
class Object(object):
    pass

# Constantes
PORT = 6666
# TIMEOUT = 60
ANTI_FLOOD_TIME_LIMIT = 2 # Tempo limite (em segundos)
ANTI_FLOOD_MSG_QTD = 5 # Quantidade de mensagens que podem ser enviada dentro do tempo limite

# Variaveis globais
listaClientes = []
sair = False

# Configuracao do socket
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind(('', PORT))
listen_socket.settimeout(1)
listen_socket.listen(0)

def threadDoCliente(cliente):
	global listaClientes, TIMEOUT, ANTI_FLOOD_MSG_QTD, ANTI_FLOOD_TIME_LIMIT, sair

	# Essa lista guarda o tempo de envio das ultimas 5 mensagens enviadas pelo cliente
	ultimasMensagens = Queue.Queue(ANTI_FLOOD_MSG_QTD)

	# cliente.conn.send("Digite seu apelido: ")
	cliente.apelido = cliente.conn.recv(1024).replace("\r\n", "")

	atualizarClientesOnline()

	time.sleep(1)
	
	broadcast(cliente.apelido + " entrou na sala.")

	# Configura um timeout para saber quando o cliente encerrou a conexao
	# cliente.conn.settimeout(TIMEOUT)
	disconnected = False
	quintaUltima = None
	while not disconnected and not sair:
		try:
			msg = cliente.conn.recv(1024)

			# Se o cliente se desconectar inesperadamente, o socket recebe uma string vazia
			if msg == "":
				break

			msg = msg.replace("\r\n", "")

			# Altera o apelido do cliente
			if re.match(r'^(nome)(\(.+\))$', msg):
				apelido = msg.split("(")[1][0:-1]
				apelidoAnterior = cliente.apelido
				cliente.apelido = apelido
				atualizarClientesOnline()
				time.sleep(1)
				broadcast(apelidoAnterior + " alterou seu apelido para " + apelido)
				
				continue

			if ultimasMensagens.full():
				quintaUltima = ultimasMensagens.get(False)

			if ultimasMensagens.qsize() == 4 and quintaUltima != None and (time.time() - quintaUltima) <= ANTI_FLOOD_TIME_LIMIT:
				cliente.conn.send("__WARNING__:Voce nao pode enviar mais de 5 mensagens a cada 2 segundos.\r\n")
			else:
				broadcast(cliente.apelido + " escreveu: " + msg)
				ultimasMensagens.put(time.time())
		except socket.timeout:
			disconnected = True

	cliente.conn.close()
	listaClientes.remove(cliente)
	broadcast(cliente.apelido + " saiu da sala.")
	time.sleep(1)
	atualizarClientesOnline()

def recebeComandos():
	global listaClientes, sair
	while not sair:
		var = raw_input("""
Lista de comandos:
 listar (ls): apresenta uma lista dos usuarios conectados no momento
 sair   (q) : encerrar servidor

""")
		if var == "listar" or var == "ls":
			if not len(listaClientes):
				print "Nenhum cliente conectado."
			else:
				for cliente in listaClientes:
					print "<" + (cliente.apelido if hasattr(cliente, "apelido") else "Anonimo") + ", " + str(cliente.addr[0]) + ", " + str(cliente.addr[1]) + ">"
		elif var == "sair" or var == "q":
			sair = True
			broadcast("__SAIR__", True)
			
	

# Envia uma string para todos os clientes conectados
def broadcast(string, raw = False):
	global listaClientes
	now = datetime.datetime.now();
	for cliente in listaClientes:
		try:
			if not raw:
				cliente.conn.send(str(now.hour).zfill(2) + ":"+ str(now.minute).zfill(2) + ":" + str(now.second).zfill(2) + " - " + string + "\r\n");
			else:
				cliente.conn.send(string);
		except:
			time.sleep(0)

def atualizarClientesOnline():
	clientesOnline = "__CLIENTES__:"
	for cliente in listaClientes:
		clientesOnline += cliente.apelido + ","
	clientesOnline = clientesOnline[:-1]
	broadcast(clientesOnline, True)

# Main loop

threadID = 0
threading.Thread(target=recebeComandos).start()

while not sair:
	try:
		# Fica preso aqui enquanto nao receber uma nova conexao
		client_connection, client_address = listen_socket.accept()

		tmp = Object()
		tmp.id = threadID
		tmp.conn = client_connection
		tmp.addr = client_address
		tmp.apelido = "Anonimo"

		listaClientes.append(tmp)
	
		# Cria e inicia nova thread
		threading.Thread(target=threadDoCliente, args=(tmp,)).start()
	
		# Incrementa ID
		threadID += 1
	except:
		time.sleep(0)
