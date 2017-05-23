import threading
import time
from socket import *
from threading import Thread

serverName = 'localhost' # ip do servidor
serverPort = 6666 # porta a se conectar
clientSocket = socket(AF_INET,SOCK_STREAM) # criacao do socket TCP
clientSocket.connect((serverName, serverPort)) # conecta o socket ao servidor
conectado = True

def threadRecebe():
	global clientSocket, conectado
	clientSocket.settimeout(1)
	while conectado:
		try:
			msgRecebida = clientSocket.recv(1024).replace("\n", "")
			if msgRecebida == "__SAIR__":
				clientSocket.close()
				conectado = False
				break
			print msgRecebida
		except:
			time.sleep(0)

threading.Thread(target=threadRecebe).start()
while True:	
	msgAEnviar = raw_input()
	if msgAEnviar == "sair()" or conectado == False:
		clientSocket.close()
		conectado = False
		break
	print "\033[A                             \033[A" # Remove a linha que o usuario digitou
	clientSocket.send(msgAEnviar)