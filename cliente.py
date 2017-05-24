import threading
import time
import socket
from unicurses import *

# Configura socket
serverName = 'localhost'
serverPort = 6666
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
conectado = True

linha = 2
apelido = False

# Configura Paineis
stdscr = initscr()
LINES, COLS = getmaxyx(stdscr)
start_color()
use_default_colors()
init_pair(1, 1, -1) # Alguem entrou na sala
init_pair(2, 6, -1) # Suas proprias mensagens
init_pair(3, 9, -1) # Clientes online

janelaPrincipal = newwin(LINES - 3, COLS - 30, 0, 0)
box(janelaPrincipal)
wmove(janelaPrincipal, 1, 1)
waddstr(janelaPrincipal, "Mensagens recebidas:")
painelPrincipal = new_panel(janelaPrincipal)

janelaUsuarios = newwin(LINES - 3, 30, 0, COLS - 30)
box(janelaUsuarios)
scrollok(janelaUsuarios, True)
wmove(janelaUsuarios, 1, 1)
waddstr(janelaUsuarios, "Usuarios online:")
painelUsuarios = new_panel(janelaUsuarios)

janelaTexto = newwin(3, COLS, LINES - 3, 0)
keypad(janelaTexto, True)
box(janelaTexto)
wmove(janelaTexto, 1, 1)
waddstr(janelaTexto, "Digite seu apelido: ")
painelTexto = new_panel(janelaTexto)

update_panels()
doupdate()

def threadRecebe():
	global clientSocket, conectado, linha, janelaPrincipal, apelido, janelaUsuarios
	clientSocket.settimeout(2)
	while conectado:
		try:
			msgRecebida = clientSocket.recv(1024).replace("\n", "")
			if msgRecebida == "__SAIR__":
				clientSocket.close()
				conectado = False
				break
			wmove(janelaPrincipal, linha, 1)
			if msgRecebida.find("__CLIENTES__") > -1:
				clientes = msgRecebida.split(":")[1].split(",")
				for i in range(2, LINES - 4):
					wmove(janelaUsuarios, i, 1)
					if len(clientes) - 1 <= i-2:
						wdeleteln(janelaUsuarios)
						winsdelln(janelaUsuarios, 1)
						box(janelaUsuarios)
					else:
						waddstr(janelaUsuarios, str(i-1) + ") " + clientes[i-2], color_pair(3))
			elif msgRecebida.find("entrou na sala.") > -1:
				waddstr(janelaPrincipal, msgRecebida, color_pair(1))
			elif msgRecebida.find("- " + apelido + " escreveu:") > -1:
				waddstr(janelaPrincipal, msgRecebida, color_pair(2))
			else:
				waddstr(janelaPrincipal, msgRecebida)
			update_panels()
			doupdate()
			linha += 1
		except:
			time.sleep(0)

threading.Thread(target=threadRecebe).start()
while True:
	msgAEnviar = wgetstr(janelaTexto)

	# Remove o que o usuario acabou de digitar da caixa de texto
	wmove(janelaTexto, 1, 1)
	wdeleteln(janelaTexto)
	winsdelln(janelaTexto, 1)
	box(janelaTexto)
	wmove(janelaTexto, 1, 1)
	waddstr(janelaTexto, "Digite uma mensagem: ")
	update_panels()
	doupdate()

	if msgAEnviar == "sair()" or conectado == False:
		clientSocket.close()
		conectado = False
		endwin()
		break
	if apelido == False:
		apelido = msgAEnviar
	clientSocket.send(msgAEnviar)