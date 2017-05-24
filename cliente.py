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
init_pair(1, 2, -1) # Alguem entrou na sala
init_pair(2, 6, -1) # Suas proprias mensagens
init_pair(3, 3, -1) # Clientes online

janelaPrincipal = newwin(LINES - 3, COLS - 30, 0, 0)
scrollok(janelaPrincipal, True)
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
	clientSocket.settimeout(1)
	while conectado:
		try:
			msgRecebida = clientSocket.recv(1024).replace("\r\n", "")
			wmove(janelaPrincipal, linha, 1)
			if msgRecebida == "__SAIR__":
				waddstr(janelaPrincipal, "O servidor de chat foi encerrado! Pressione ENTER para sair.", color_pair(3))
				clientSocket.close()
				conectado = False
				update_panels()
				doupdate()
				break
			if msgRecebida.find("__CLIENTES__") > -1:
				clientes = msgRecebida.split(":")[1].split(",")
				for i in range(2, LINES - 4):
					wmove(janelaUsuarios, i, 1)
					wdeleteln(janelaUsuarios)
					winsdelln(janelaUsuarios, 1)
					box(janelaUsuarios)
					if len(clientes) > i - 2:
						color = 3 if clientes[i - 2] != apelido else 2
						waddstr(janelaUsuarios, str(i - 1) + ") " + clientes[i - 2], color_pair(color))
			elif msgRecebida.find("__WARNING__:") > -1:
				waddstr(janelaPrincipal, msgRecebida.replace("__WARNING__:", ""), color_pair(3))
			elif msgRecebida.find("entrou na sala.") > -1:
				waddstr(janelaPrincipal, msgRecebida, color_pair(1))
			elif msgRecebida.find("- " + apelido + " escreveu:") > -1:
				waddstr(janelaPrincipal, msgRecebida, color_pair(2))
			elif msgRecebida != "":
				waddstr(janelaPrincipal, msgRecebida)

			linha += 1
			if linha > LINES - 5:
				wscrl(janelaPrincipal, 1) # Scroll
			update_panels()
			doupdate()
		except:
			time.sleep(0)

threading.Thread(target=threadRecebe).start()
while conectado:
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
