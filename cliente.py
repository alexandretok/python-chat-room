import threading
import time
import socket
import curses, curses.panel

# Configura socket
serverName = 'localhost'
serverPort = 6666
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
conectado = True
flood = 0

linha = 2
apelido = False

# Configura Paineis
stdscr = curses.initscr()
LINES, COLS = stdscr.getmaxyx()
curses.start_color()
curses.use_default_colors()
curses.init_pair(1, 2, -1) # Alguem entrou na sala
curses.init_pair(2, 6, -1) # Suas proprias mensagens
curses.init_pair(3, 3, -1) # Clientes online

janelaPrincipal = curses.newwin(LINES - 3, COLS - 30, 0, 0)
janelaPrincipal.scrollok(True)
janelaPrincipal.move(1, 1)
janelaPrincipal.addstr("Mensagens recebidas:")
painelPrincipal = curses.panel.new_panel(janelaPrincipal)

janelaUsuarios = curses.newwin(LINES - 3, 30, 0, COLS - 30)
janelaUsuarios.box()
janelaUsuarios.scrollok(True)
janelaUsuarios.move(1, 1)
janelaUsuarios.addstr("Usuarios online:")
painelUsuarios = curses.panel.new_panel(janelaUsuarios)

janelaTexto = curses.newwin(3, COLS, LINES - 3, 0)
janelaTexto.keypad(True)
janelaTexto.box()
janelaTexto.move(1, 1)
janelaTexto.addstr("Digite seu apelido: ")
painelTexto = curses.panel.new_panel(janelaTexto)

curses.panel.update_panels()
curses.doupdate()

def threadRecebe():
	global clientSocket, conectado, linha, janelaPrincipal, apelido, janelaUsuarios, flood
	clientSocket.settimeout(1)
	while conectado:
		try:
			msgRecebida = clientSocket.recv(1024).replace("\r\n", "")
			janelaPrincipal.move(linha, 1)

			if msgRecebida == "__SAIR__":
				janelaPrincipal.addstr("O servidor de chat foi encerrado! Pressione ENTER para sair.", curses.color_pair(3))
				clientSocket.close()
				conectado = False
				curses.panel.update_panels()
				curses.doupdate()
				break
			if msgRecebida.find("__CLIENTES__") > -1:
				clientes = msgRecebida.split(":")[1].split(",")
				for i in range(2, LINES - 4):
					janelaUsuarios.move(i, 1)
					janelaUsuarios.deleteln()
					janelaUsuarios.insdelln(1)
					janelaUsuarios.box()
					if len(clientes) > i - 2:
						color = 3 if clientes[i - 2] != apelido else 2
						janelaUsuarios.addstr(str(i - 1) + ") " + clientes[i - 2], curses.color_pair(color))
				curses.panel.update_panels()
				curses.doupdate()
				continue
			elif msgRecebida.find("__WARNING__:") > -1:
				janelaPrincipal.addstr(msgRecebida.replace("__WARNING__:", ""), curses.color_pair(3))
				flood = time.time()
			elif msgRecebida.find("entrou na sala.") > -1:
				janelaPrincipal.addstr(msgRecebida, curses.color_pair(1))
			elif msgRecebida.find("- " + apelido + " escreveu:") > -1:
				janelaPrincipal.addstr(msgRecebida, curses.color_pair(2))
			elif msgRecebida != "":
				janelaPrincipal.addstr(msgRecebida)

			
			if linha > LINES - 5:
				janelaPrincipal.scroll(1) # Scroll
			else:
				linha += 1
			curses.panel.update_panels()
			curses.doupdate()
		except:
			time.sleep(0)

threading.Thread(target=threadRecebe).start()
while conectado:
	msgAEnviar = janelaTexto.getstr()

	# Remove o que o usuario acabou de digitar da caixa de texto
	janelaTexto.move(1, 1)
	janelaTexto.deleteln()
	janelaTexto.insdelln(1)
	janelaTexto.box()
	janelaTexto.move(1, 1)
	janelaTexto.addstr("Digite uma mensagem: ")
	curses.panel.update_panels()
	curses.doupdate()

	if msgAEnviar == "sair()" or conectado == False:
		clientSocket.close()
		conectado = False
		curses.endwin()
		break
	if apelido == False:
		apelido = msgAEnviar

	# Verifica se passaram-se os 10 segundos
	if time.time() - flood < 10:
		continue;
	
	clientSocket.send(msgAEnviar)