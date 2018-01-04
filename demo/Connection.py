import socket, select
from tkinter import *
from tkinter.scrolledtext import *
from Player import *

class ServerConnection:
	"""Server connection object.
	
	Args:
		root: TK window object.
		chatbox: An object you can write something on,
			which is used to record message between players and server.
		UP,DP: Objects of transformed maze above and below.
		border_H,border_W: Row and Column number you've set. 
		block_size: Width of a lattice you've set.
	"""
	def __init__(self,root,chatbox,UP,DP,border_H,border_W,block_size):
		self.UP = UP
		self.DP = DP
		self.root = root
		self.border_H = border_H
		self.border_W = border_W
		self.block_size = block_size
		self.RECV_BUFFER = 4096 
		self.PORT = 5000
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.player = {}			# Dict used to collect players information.
		self.chatbox = chatbox

	def ser_send_data(self,sock,message):
		"""Sending message from server.
		
		Args:
			sock: Socket of the player that you want to send to.
			message: String content.
		"""
		tmp_message = 'Master|' + message + '\r'
		# print(message)
		try :
			sock.send(tmp_message.encode(encoding='utf-8'))
			"""
			# Print to the window
			self.chatbox.insert(INSERT, 'Master send to %s : %s\n' %(self.player[sock].name,message))
			self.chatbox.see(END)
			"""
		except :
			# If socket connection failed, delete the player and socket.
			self.DELETE(sock)

	def send_data(self,sock, message):
		"""Message transmitting between players.
		
		Do not send the message to master socket and 
		the client who has send us the message.
		"""
		for socket in self.player:
			if socket != self.server_socket and socket != sock:
				Name = message[0:message.index('|')]
				if self.player[socket].name == Name:    
					try :
						tmp_message = self.player[sock].name + message[message.index('|'):] # src name
						socket.send(tmp_message.encode(encoding='utf-8'))
						
						# Print to the window
						self.chatbox.insert(INSERT, '%s send to %s : %s\n' %(self.player[sock].name,Name,message[message.index('|')+1:len(message)-1]))
						self.chatbox.see(END)
						
					except :
						# If socket connection failed, delete the player and socket.
						self.DELETE(socket)

	def broadcast_data (self,sock, message):
		"""Broadcast chat messages to all connected clients.
		
		Do not send the message to master socket and 
		the client who has send us the message.
		"""
		for socket in self.player:
			if socket != self.server_socket and socket != sock :
				try :
					tmp_message = self.player[sock].name + message[message.index('|'):] # src name
					socket.send(tmp_message.encode(encoding='utf-8'))
					"""
					#Print to the window
					self.chatbox.insert(INSERT, '%s Broadcast : %s\n' %(self.player[sock].name,message[message.index('|')+1:]))
					self.chatbox.see(END)                
					"""
				except :
					# If socket connection failed, delete the player and socket.
					self.DELETE(socket)

	def OpenServerSocket(self):
		"""Server socket setting to multiclient."""
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind(("0.0.0.0", self.PORT))
		self.server_socket.listen(10)
		# Name the Server socket of the first of dict.
		self.player[self.server_socket] = "Master"
		print ("Chat server started on port " + str(self.PORT))

	def WaitingConnection(self):
		"""Cope with new clients and receiving message from clients. """
		while 1:
			# Get the list sockets which are ready to be read through select.
			CONNECTION_LIST = []
			for i in self.player:
				CONNECTION_LIST.append(i)
			read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

			for sock in read_sockets:
				# New connection
				if sock == self.server_socket:
					# Handle the case in which there is a new connection recieved through server_socket
					sockfd, addr = self.server_socket.accept()
					self.player[sockfd] = ''
					print ("[%s:%s] entered room\n" % addr)
				 
				# Some incoming message from a client.
				else:
					try:
						"""Distinguish the message from clients.
						In Windows, sometimes when a TCP program closes abruptly,
						a "Connection reset by peer" exception will be thrown.
						"""
						data = sock.recv(self.RECV_BUFFER).decode('utf-8')
				
						if 'Register' in data:			# New player join the game.
							sock.send("Master|Client hello!\r".encode(encoding='utf-8'))
							# Create player object.
							self.player[sock] =  Player(self.root,data[10:],self.UP,self.DP,\
								self.border_H,self.border_W,self.block_size)
							print(self.player[sock])

						elif 'Broadcast' in data:
							self.broadcast_data(sock,data+'\r') 

						elif 'Position' in data:		# Send player's position back.
							self.ser_send_data(sock,"POS:"+str((int(self.player[sock].x),int(self.player[sock].y))))
  
						elif '|' in data:				# Message transmitting between players.
							self.send_data(sock,data+'\r')
							
					except:
						self.DELETE(sock)
						continue
		self.server_socket.close()
		print("s close")

	def DELETE(self,socket):
		"""Delete the player and close the socket."""
		if type(self.player[socket]) != type('a'):
			self.player[socket].Connected = False
			self.player[socket].delete()
			del self.player[socket]
			socket.close()



	

