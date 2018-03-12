from tkinter import *	
import tkinter.font as font
from tkinter.scrolledtext import *
from threading import Thread, Lock
from Transform import *
import threading,os
from Connection import *
from TowerGame import *
import numpy as np
import cv2

start_count = 0


class myThread(Thread):
	"""
	Thread for waiting connecting
	
	Args:
		Con: connection object created with class ServerConnection

	When clicking the "start" button in UI,The connection socket will open,
	and it can revert when clicking again.
	"""
	def __init__(self, con):
		Thread.__init__(self)
		self.con = con
		self._stop_event = threading.Event()

	def run(self):
		self.con.WaitingConnection()

	def stop(self):
		"""Resume the connecting socket"""
		print("Stop connection loop")
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()

class myThreadTransform(Thread):
	"""
	Thread for updating the maze continually
	
	Args:
		UP: object of class TransformMaze, used to calculate and transform upside four points of map
		DP: object of class TransformMaze, used to calculate and transform downside four points of map
	"""
	def __init__(self, UP, DP):
		Thread.__init__(self)
		self.UP = UP
		self.DP = DP
		self._stop_event = threading.Event()

	def run(self):
		show_flag = True
		while True:
			self.UP.RefreshResult()
			self.DP.RefreshResult()


	def stop(self):
		print("Stop connection loop")
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()


class myThreadFrame(Thread):
	"""
	Thread for reading frame of camera
	
	Args:
		cap: object of class VideoCapture
	"""
	def __init__(self, cap):
		Thread.__init__(self)
		self.cap = cap
		self.frame = None
		self.frame_lock = Lock()

	def run(self):
		while True:
			ret, Frame = self.cap.read()
			self.frame = cv2.resize(Frame,None,fx=1, fy=1, interpolation = cv2.INTER_CUBIC)
			if ret == False:
				break


class GameThread(Thread):
	"""
	Thread for execute the game
	
	Execute function in TowerGame, until game over or quit.
	"""
	def __init__(self, Con):
		super(GameThread, self).__init__()
		self.Con = Con
		self.App = App(self.Con)
		
	def run(self):
		""""""
		for idx in list(self.Con.player):
			if type(self.Con.player[idx]) != type('a'):
				self.Con.player[idx].game_init()
				ChangeColor(self.Con.player[idx].image, self.Con.player[idx].Color)
		self.App.on_execute()

class MazeColorThread(Thread):
	"""Thread for refreshing maze color."""
	def __init__(self, UP,DP):
		Thread.__init__(self)
		self.UP = UP
		self.DP = DP
		
	def run(self):
		self.UP.RefreshColor()
		self.DP.RefreshColor()


class RefreahPointsThread(MazeColorThread):
	"""Thread for refreshing 4 points and show the results."""
	def run(self):
		self.UP.RefreshPoints()
		self.DP.RefreshPoints()
		cv2.namedWindow('UP (w to quit)')
		cv2.namedWindow('DP (w to quit)')
		while 1:
			cv2.imshow('UP (w to quit)',self.UP.Result)
			cv2.imshow('DP (w to quit)',self.DP.Result)
			# click 'w' to quit the window, and use wait keys to keep from crashing
			if cv2.waitKey(1) & 0xFF == ord('w'):
				cv2.destroyWindow("UP (w to quit)")	
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.destroyWindow("DP (w to quit)")				
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				break

def Exit(r):
	"""
	This is the function for terminating program
	
	Args:
		r: window object of TK
	"""
	os._exit(1)
	r.destroy()	
		
def convert():
	"""Once clicking to convert with start and close"""
	global start_count, ConThread, Con
	if start_count%2:
		btn_text.set("Start Server")

		# Delete Connection obj
		for x in Con.player:
			if type(Con.player[x]) != type('a'):
				Con.player[x].delete()
		Con.player = {Con.server_socket:"Master"}		# Create master player for server socket
		ConThread.stop()
		
	else:
		btn_text.set("Close Server")	
		ConThread = myThread(Con)
		ConThread.start()
		print("Waiting")
	start_count=start_count+1

def kick(Con):
	"""
	function for getting rid of specific player
	
	Args:
		Con: connection object created with class ServerConnection
	"""
	for idx in list(Con.player):
		if type(Con.player[idx]) != type('a'):
			if Con.player[idx].CheckVar.get():
				Con.DELETE(idx)
				
def transmit(Con,mes,chatbox):
	"""
	Send text to specific player
	
	Args: 
		Con: connection object created with class ServerConnection
		mes: text in the text box of main window
		chatbox: object of terminal of main window, used to dispkay message between players and server
	"""
	tmp_message = mes.get()
	for idx in list(Con.player):
		if type(Con.player[idx]) != type('a'):
			if Con.player[idx].CheckVar.get():
				Con.ser_send_data(idx,tmp_message)
				mes.set('')
				chatbox.insert(INSERT, 'Master send to %s : %s\n' %(Con.player[idx].name,tmp_message))
				chatbox.see(END)
	
def create_refresh4_thread(UP, DP):
	"""
	Function for creating updating points thread
	
	Args:
		UP: object of class TransformMaze, used to calculate and transform upside four points of map
		DP: object of class TransformMaze, used to calculate and transform downside four points of map
	"""
	refresh4_thread = RefreahPointsThread(UP, DP)
	refresh4_thread.start()
	print("refresh points")

def create_mazecolor_thread(UP, DP):
	"""
	Function for creating refreshing colors thread
	
	Args:
		UP: object of class TransformMaze, used to calculate and transform upside four points of map
		DP: object of class TransformMaze, used to calculate and transform downside four points of map
	"""
	mazecolor_thread = MazeColorThread(UP,DP)
	mazecolor_thread.start()
	print("refresh color")	

def MazeColor(UP,DP):
	"""
	Function for refreshing four-points colors of map on the frame
	
	Args:
		UP: object of class TransformMaze, used to calculate and transform upside four points of map
		DP: object of class TransformMaze, used to calculate and transform downside four points of map
	"""
	UP.RefreshColor()
	DP.RefreshColor()

	print("refresh color")	

def MazeUpdate(UP,DP,MazeUpdateBtn):
	"""
	Function for creating thread of transforming trapezoid into square 
	
	Args:
		UP: object of class TransformMaze, used to calculate and transform upside four points of map
		DP: object of class TransformMaze, used to calculate and transform downside four points of map
		MazeUpdateBtn: buttun object to create thread for transforming
	"""
	TransformThread = myThreadTransform(UP,DP)
	TransformThread.start()
	MazeUpdateBtn.config(state = "disable")

def GameRestart(Con,chatbox):
	"""
	Function triggered by clicking restart button to create or recreate a new game

	Args:
		Con: connection object created with class ServerConnection
		chatbox: object of terminal of main window
	"""
	print("restart1")
	gamethread = GameThread(Con)
	gamethread.start()
	Con.game_start = True

	print("restart ok")
	# send start to everyone
	for idx in list(Con.player):
		if type(Con.player[idx]) != type('a'):
			Con.ser_send_data(idx,"Start")

if __name__ == "__main__":
	win = Tk()

	cap = cv2.VideoCapture(0)		# create camera obj

	# set camera view border
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280);
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720);

	framethread = myThreadFrame(cap)
	framethread.start()

	UP = TransformMaze(framethread)
	UP.Color = [36, 11, 185]		# default color of red
	DP = TransformMaze(framethread)
	DP.Color = [137, 76, 10]		# default color of blue
	main_frame = Frame(win)
	main_frame.pack()

	helv36 = font.Font(family='Helvetica', size=18, weight=font.BOLD)		# Font setting
	
	btn_text = StringVar()		# button text variable
	btn_text.set("Start Server")

	# Click button to trigger function of connection available or not
	StartServerBtn = Button(main_frame, textvariable= btn_text,command = convert, font = helv36)
	StartServerBtn.pack(side = LEFT)
	# Click button to exit the program
	ExitBtn = Button(main_frame,text = "結束", command = lambda: Exit(win), font = helv36)
	ExitBtn.pack(side = RIGHT)
	# Click button to set upside and downside color of corners, use mouse to click the area of colors in the corner
	MazeColorBtn = Button(main_frame, text = "設定四角顏色", command = lambda: create_mazecolor_thread(UP, DP), font = helv36)
	MazeColorBtn.pack(side = LEFT)

	Mbtn_text = StringVar()		# button text variable
	Mbtn_text.set("開始校正")
	# Click button to start thread for transforming trapezoid into square
	MazeUpdateBtn = Button(main_frame, text = "開始校正", command = lambda: MazeUpdate(UP, DP, MazeUpdateBtn), font = helv36)
	MazeUpdateBtn.pack(side = LEFT)

	# Set the frame of terminal
	main_frame_chat = LabelFrame(win, bg = '#a3a8a7')
	main_frame_chat.pack(fill='x', padx=10, pady=8)
	# Create terminal object
	chatbox = ScrolledText(main_frame_chat, height = 5)
	chatbox.pack(padx=10, pady=8)
	# Button for clearing terminal text 
	chatboxbt = Button(win , text = 'clear', command=lambda: chatbox.delete(1.0, END)).pack()

	main_frame_player = LabelFrame(win,text = "連線玩家",foreground = 'blue')
	main_frame_player.pack(fill='x',padx=10,pady=2)
	
	main_frame_player_box = LabelFrame(main_frame_player)
	main_frame_player_box.pack(fill='x',padx=10,pady=8)

	main_frame_player_team = LabelFrame(main_frame_player)
	main_frame_player_team.pack(fill='x',padx=10,pady=8)

	main_frame_player_teamA = LabelFrame(main_frame_player_team,text = "Team A",foreground="red")
	main_frame_player_teamA.pack(side = LEFT)

	main_frame_player_teamB = LabelFrame(main_frame_player_team,text = "Team B",foreground="red")
	main_frame_player_teamB.pack(side = RIGHT)
	
	border_H = 9
	border_W = 9
	block_size = 64
	# create connection obj
	Con = ServerConnection(main_frame_player_teamA,main_frame_player_teamB, chatbox , UP, DP, border_H, border_W, block_size)
	Con.OpenServerSocket()

	mes = StringVar()
	refresh_4point = Button(main_frame_player_box , text = "攝影機晃到" , command = lambda:create_refresh4_thread(UP,DP)).pack(side = RIGHT)
	delete_button = Button(main_frame_player_box, text = "踢除" , command = lambda: kick(Con)).pack(side = RIGHT)
	message_button = Button(main_frame_player_box, text="傳送" , command = lambda: transmit(Con,mes,chatbox)).pack(side = RIGHT)	
	message_textbox = Entry(main_frame_player_box, width=16, textvariable = mes).pack(side = RIGHT)
	message_label1 = Label(main_frame_player_box,text="勾選以下用戶做操作:").pack(side = LEFT)	
	
	gamebt = Button(win , text = 'Game Start' ,command = lambda: GameRestart(Con,chatbox) ).pack()


	#window size setting
	w = win.winfo_reqwidth() # width for the Tk root
	h = win.winfo_reqheight() # height for the Tk root
	# get screen width and height
	ws = win.winfo_screenwidth() # width of the screen
	hs = win.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (1080/2)
	y = (hs/2) - (600/2)
	# set the dimensions of the screen and where it is placed
	win.geometry('%dx%d+%d+%d' % (1080, 600, x, y))
	win.mainloop()
