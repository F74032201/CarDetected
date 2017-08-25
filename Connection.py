import socket, select

class ServerConnection:
	def __init__(self):
		self.RECV_BUFFER = 4096 
		self.PORT = 5000
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.CONNECTION_DICT = {}

	def send_data(self,sock, message):
		#Do not send the message to master socket and the client who has send us the message
		for socket in self.CONNECTION_DICT:
			if socket != self.server_socket and socket != sock:
				Name = message[0:message.index('|')]
				if self.CONNECTION_DICT[socket] == Name:    
					try :
						socket.send(message[message.index('|')+1:].encode(encoding='utf-8'))
						print(message[message.index('|')+1:])
					except :
						# broken socket connection may be, chat client pressed ctrl+c for example
						self.CONNECTION_DICT.pop(socket)
						socket.close()
	#Function to broadcast chat messages to all connected clients
	def broadcast_data (self,sock, message):
		#Do not send the message to master socket and the client who has send us the message
		for socket in self.CONNECTION_DICT:
			if socket != self.server_socket and socket != sock :
				try :
					socket.send(message.encode(encoding='utf-8'))	                
				except :
					# broken socket connection may be, chat client pressed ctrl+c for example
					self.CONNECTION_DICT.pop(socket)
					socket.close()

	def OpenServerSocket(self):
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind(("0.0.0.0", self.PORT))
		self.server_socket.listen(10)
		#Name the Server socket of the first of dict
		self.CONNECTION_DICT[self.server_socket] = "Master"
		print ("Chat server started on port " + str(self.PORT))

	def WaitingConnection(self):
		while 1:
			# Get the list sockets which are ready to be read through select
			CONNECTION_LIST = []
			for i in self.CONNECTION_DICT:
			    CONNECTION_LIST.append(i)
			read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

			for sock in read_sockets:
			    #New connection
			    if sock == self.server_socket:
			        # Handle the case in which there is a new connection recieved through server_socket
			        sockfd, addr = self.server_socket.accept()

			        self.CONNECTION_DICT[sockfd] = ''

			        print ("[%s:%s] entered room\n" % addr)
			        sockfd.send("Client hello!\r".encode(encoding='utf-8'))
			        #broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
			     
			    #Some incoming message from a client
			    else:
			        # Data recieved from client, process it
			        try:
			            #In Windows, sometimes when a TCP program closes abruptly,
			            # a "Connection reset by peer" exception will be thrown
			            data = sock.recv(self.RECV_BUFFER).decode('utf-8')
			            #regist id
			            if 'Register:' in data:
			                self.CONNECTION_DICT[sock] = data[9:]
			                print("registed:",data[9:])
			            elif 'Broadcast' in data:
			                self.broadcast_data(sock,data[10:]+'\r') 
			                
			            #sent to specific client   
			            elif '|' in data:
			                self.send_data(sock,data+'\r')
			                
			        except:
			            #broadcast_data(sock, "Client (%s, %s) is offline" % addr)
			            print ("Client (%s, %s) is offline" % addr)
			            sock.close()
			            self.CONNECTION_DICT.pop(sock)
			            continue
		self.server_socket.close()
		print("s close")

	

