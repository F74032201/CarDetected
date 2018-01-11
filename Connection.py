import socket, select
from tkinter import *
from tkinter.scrolledtext import *
from Player import *

class ServerConnection:
	def __init__(self,rootA,rootB,chatbox,UP,DP,border_H,border_W,block_size):
		self.UP = UP
		self.DP = DP
		self.rootA = rootA
		self.rootB = rootB
		self.border_H = border_H
		self.border_W = border_W
		self.block_size = block_size
		self.RECV_BUFFER = 4096 
		self.PORT = 5000
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.player = {}
		self.player_num = 0
		self.chatbox = chatbox
		self.game_start = False
		self.towers_pos = [(-1,-1),(-1,-1),(-1,-1)]
		self.base_situation = {'A':'C', 'B':'C'}

	def ser_send_data(self,sock,message):
		#Sending message from server
		tmp_message = 'Master|' + message + '\r'
		try :
			sock.send(tmp_message.encode(encoding='utf-8'))
			if 'POS:' not in message:	
				# Print to the window
				self.chatbox.insert(INSERT, 'Master send to %s : %s\n' %(self.player[sock].name,message))
				self.chatbox.see(END)
		except :
			# broken socket connection may be, chat client pressed ctrl+c for example
			self.DELETE(sock)

	def send_data(self,sock, message):
		#Do not send the message to master socket and the client who has send us the message		
		for socket in self.player:
			if socket != self.server_socket and socket != sock:
				Name = message[0:message.index('|')]
				if self.player[socket].name == Name:    
					try :
						tmp_message = self.player[sock].name + message[message.index('|'):] # src name
						socket.send(tmp_message.encode(encoding='utf-8'))
						print(message[message.index('|')+1:])
						#Print to the window
						self.chatbox.insert(INSERT, '%s send to %s : %s\n' %(self.player[sock].name,Name,message[message.index('|')+1:len(message)-1]))
						self.chatbox.see(END)
						
					except :
						# broken socket connection may be, chat client pressed ctrl+c for example
						self.DELETE(socket)
	#Function to broadcast chat messages to all connected clients
	def broadcast_data (self,sock, message):
		#Do not send the message to master socket and the client who has send us the message
		
		for socket in self.player:
			if socket != self.server_socket and socket != sock :
				try :
					tmp_message = self.player[sock].name + message[message.index('|'):] # src name
					socket.send(tmp_message.encode(encoding='utf-8'))
					'''	
					#Print to the window
					self.chatbox.insert(INSERT, '%s Broadcast : %s\n' %(self.player[sock].name,message[message.index('|')+1:]))
					self.chatbox.see(END)                
					'''
				except :
					# broken socket connection may be, chat client pressed ctrl+c for example
					self.DELETE(socket)

	def OpenServerSocket(self):
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind(("0.0.0.0", self.PORT))
		self.server_socket.listen(10)
		#Name the Server socket of the first of dict
		self.player[self.server_socket] = "Master"
		print ("Chat server started on port " + str(self.PORT))

	def WaitingConnection(self):
		while 1:
			# Get the list sockets which are ready to be read through select
			CONNECTION_LIST = []
			for i in self.player:
			    CONNECTION_LIST.append(i)
			read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

			for sock in read_sockets:
			    #New connection
			    if sock == self.server_socket and not self.game_start:
			        # Handle the case in which there is a new connection recieved through server_socket
			        # If game has started client can't enter the room.
			        sockfd, addr = self.server_socket.accept()
			        self.player[sockfd] = ''

			        print ("[%s:%s] entered room\n" % addr)
			        
			        #broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
			     
			    #Some incoming message from a client
			    else:
			        # Data recieved from client, process it
			        try:
			            #In Windows, sometimes when a TCP program closes abruptly,
			            # a "Connection reset by peer" exception will be thrown
			            data = sock.recv(self.RECV_BUFFER).decode('utf-8')
			            #regist id
			            if 'Register' in data:
			                sock.send("Master|Client hello!\r".encode(encoding='utf-8'))
			                #create player obj
			                if data[8] == 'A':
			                	self.player[sock] =  Player(self.rootA,data[10:],self.UP,self.DP,self.border_H,self.border_W,self.block_size)
			                	self.player[sock].team = "A"
			                elif data[8] == 'B':
			                	self.player[sock] =  Player(self.rootB,data[10:],self.UP,self.DP,self.border_H,self.border_W,self.block_size)
			                	self.player[sock].team = "B"

			                print(self.player[sock])

			            elif 'Broadcast' in data:
			                self.broadcast_data(sock,data+'\r') 

			            elif 'Position' in data:
			            	self.ser_send_data(sock,"POS:"+str((int(self.player[sock].x + 16),int(self.player[sock].y + 16)))\
			            			+ "BaseA:" + str(self.base_situation['A'] + "BaseB:" + str(self.base_situation['B']))\
			            			+ "Towers:" + str(self.towers_pos[0]) + str(self.towers_pos[1]) + str(self.towers_pos[2])\
			            			+ "Blood:" + str(self.player[sock].blood))

			            elif 'AskPos' in data:
			            	for idx in self.player:
			            		if type(self.player[idx]) != type('a'):
			            			if self.player[idx].name == data[7:]:	# Find the player.
			            				if self.player[sock].team == self.player[idx].team:	# Check that are they the same team.
			            					self.ser_send_data(sock, str(self.player[idx].name) + ':' + \
			            						str((int(self.player[idx].x + 16), int(self.player[idx].y + 16))))

			            #sent to specific client   
			            elif '|' in data:
			                self.send_data(sock,data+'\r')
			                
			        except:
			            self.DELETE(sock)
			            continue
		self.server_socket.close()
		print("s close")

	def DELETE(self,socket):
		if type(self.player[socket]) != type('a'):
			self.player[socket].Connected = False
			self.player[socket].delete()
			del self.player[socket]
			socket.close()



	

