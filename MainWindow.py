from tkinter import *    
import tkinter.font as font
from tkinter.scrolledtext import *
from threading import Thread
from Transform import *
import threading,os
from Connection import *
from pacman import *
import numpy as np
import cv2

start_count = 0    # Swithcing count

class my_thread(Thread):
	"""Create a thread for connection"""
	def __init__(self, con):
		Thread.__init__(self)
		self.con = con
		self._stop_event = threading.Event()

	def run(self):
		self.con.WaitingConnection()

	def stop(self):
		print("Stop connection loop")
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()

class thread_transform(Thread):
	"""Thread for updating the maze,and show the resault"""
	def __init__(self, UP, DP):
		Thread.__init__(self)
		self.UP = UP
		self.DP = DP
		self._stop_event = threading.Event()

	def run(self):
		while True:
			self.UP.refresh_result()
			self.DP.refresh_result()
			

class thread_frame(Thread):
	"""Thread for updating the stream from camera."""
	def __init__(self, cap):
		Thread.__init__(self)
		self.cap = cap
		self.frame = None

	def run(self):
		while True:
			ret, Frame = self.cap.read()
			self.frame = cv2.resize(Frame, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
			if ret == False:
				break

class game_thread(Thread):
	"""Thread for executing Pacman"""
	def __init__(self, Con):
		super(game_thread, self).__init__()
		self.Con = Con
		self.App = App(self.Con)
		pygame.mixer.pre_init(44100, -16, 1, 512)
		pygame.init()
		self.App._display_surf = pygame.display.set_mode(\
			(self.App.windowWidth, self.App.windowHeigh), pygame.HWSURFACE)
		pygame.display.set_caption('Pacman')

	def run(self):
		# Initialize all the players in connection.
		for idx in list(self.Con.player):
			# Except for the master (socket).
			if type(self.Con.player[idx]) != type('a'):
				self.Con.player[idx].game_init()
		self.App.on_execute()
		# Delete the object when quit the game.
		del self.App

class MazeColorThread(Thread):
	"""Thread for picking maze color."""
	def __init__(self, UP,DP):
		Thread.__init__(self)
		self.UP = UP
		self.DP = DP
		
	def run(self):
		self.UP.refresh_color()
		self.DP.refresh_color()

class RefreahPointsThread(MazeColorThread):
	"""Thread for refreshing 4 points and show the results."""
	def run(self):
		self.UP.refresh_points()
		self.DP.refresh_points()
		cv2.namedWindow('UP (w to quit)')
		cv2.namedWindow('DP (w to quit)')
		while True:
			# Show the window of the transforming maze
			cv2.imshow('UP (w to quit)', self.UP.result)
			cv2.imshow('DP (w to quit)', self.DP.result)

			if cv2.waitKey(1) & 0xFF == ord('w'):
				cv2.waitKey(1)
				cv2.destroyWindow("UP (w to quit)")
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.destroyWindow("DP (w to quit)")
				# Use waitkey to prevent from crashing
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				break

def Exit(r):
	"""Exit the program."""
	os._exit(1)
	r.destroy()

def convert():
	"""The switching function for starting/closing the server."""
	global start_count, ConThread, Con
	if start_count%2:
		btn_text.set("Start Server")

		# Delete Connection obj
		for x in Con.player:
			# Except for the master (socket).
			if type(Con.player[x]) != type('a'):
				Con.player[x].delete()
				Con.player = {Con.server_socket:"Master"}
				ConThread.stop()
	else:
		btn_text.set("Close Server")
		ConThread = my_thread(Con)
		ConThread.start()
		print("Waiting")
		start_count = start_count+1

def kick(Con):
	"""Kick the chosen players."""
	for idx in list(Con.player):
		# Except for the master (socket).
		if type(Con.player[idx]) != type('a'):
			if Con.player[idx].check_var.get():
				Con.DELETE(idx)

def transmit(Con, mes, chatbox):
	"""Transmit message to chosen player."""
	tmp_message = mes.get()
	for idx in list(Con.player):
		# Except for the master (socket).
		if type(Con.player[idx]) != type('a'):
			if Con.player[idx].check_var.get():
				Con.ser_send_data(idx, tmp_message)
				# Show the message to the Chat box.
				mes.set('')
				chatbox.insert(INSERT, 'Master send to %s : %s\n'\
					%(Con.player[idx].name, tmp_message))
				chatbox.see(END)

def create_refresh4_thread(UP, DP):
	refresh4_thread = RefreahPointsThread(UP, DP)
	refresh4_thread.start()
	print("refresh points")

# def refresh_4(UP, DP):
# 	UP.refresh_points()
# 	DP.refresh_points()
# 	print("refresh points")
def create_mazecolor_thread(UP, DP):
	mazecolor_thread = MazeColorThread(UP,DP)
	mazecolor_thread.start()
	print("refresh color")	

# def maze_color(UP, DP):
# 	UP.refresh_color()
# 	DP.refresh_color()
# 	print("refresh color")

def maze_update(UP, DP, maze_update_btn):
	transform_thread = thread_transform(UP, DP)
	transform_thread.start()
	maze_update_btn.config(state="disable")

def game_restart(Con, chatbox):
	"""Restarting the game and initialization."""
	gamethread = game_thread(Con)
	gamethread.start()

	# Send start to everyone.
	for idx in list(Con.player):
		if type(Con.player[idx]) != type('a'):
			Con.ser_send_data(idx, "Start")
			chatbox.insert(INSERT, 'Master send to %s : %s\n' %(Con.player[idx].name, "Start"))
			chatbox.see(END)

if __name__ == "__main__":
	win = Tk()

	#create camera obj
	cap = cv2.VideoCapture(1)
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

	framethread = thread_frame(cap)
	framethread.start()
	UP = TransformMaze(framethread)
	UP.color = [34, 18, 173]    # red (default) [b, g ,r]
	DP = TransformMaze(framethread)
	DP.color = [132, 80, 35]    # blue (default)
	main_frame = Frame(win)
	main_frame.pack()

	#Font setting
	helv36 = font.Font(family='Helvetica', size=18, weight=font.BOLD)
	btn_text = StringVar()
	#Top
	btn_text.set("Start Server")
	start_server_btn = Button(main_frame, textvariable=btn_text, command=convert, font=helv36)
	start_server_btn.pack(side=LEFT)
	ExitBtn = Button(main_frame, text="結束", command=lambda: Exit(win), font=helv36)
	ExitBtn.pack(side=RIGHT)
	maze_color_btn = Button(main_frame, text="設定四角顏色",\
		command=lambda: create_mazecolor_thread(UP,DP), font=helv36)
	maze_color_btn.pack(side=LEFT)
	Mbtn_text = StringVar()
	Mbtn_text.set("開始校正")
	maze_update_btn = Button(main_frame, text="開始校正",\
		command=lambda: maze_update(UP, DP, maze_update_btn), font=helv36)
	maze_update_btn.pack(side=LEFT)

	main_frame_chat = LabelFrame(win, bg='#a3a8a7')
	main_frame_chat.pack(fill='x', padx=10, pady=8)
	chatbox = ScrolledText(main_frame_chat, height=5)
	chatbox.pack(padx=10, pady=8)
	chatboxbt = Button(win, text='clear',\
		command=lambda: chatbox.delete(1.0, END)).pack()

	main_frame_player = LabelFrame(win, text="連線玩家", foreground='blue')
	main_frame_player.pack(fill='x', padx=10, pady=2)

	main_frame_player_box = LabelFrame(main_frame_player)
	main_frame_player_box.pack(fill='x', padx=10, pady=8)

	main_frame_player_team = LabelFrame(main_frame_player)
	main_frame_player_team.pack(fill='x', padx=10, pady=8)

	border_H = 9+2    # Set Row number.
	border_W = 9+2    # Set Column number.
	block_size = 64    # Width of a lattice.
	# create connection obj
	Con = ServerConnection(main_frame_player_team, chatbox,\
		UP, DP, border_H, border_W, block_size)
	Con.OpenServerSocket()

	mes = StringVar()
	refresh_4point = Button(main_frame_player_box, text="攝影機晃到",\
		command=lambda: create_refresh4_thread(UP,DP)).pack(side=RIGHT)
	delete_button = Button(main_frame_player_box, text="踢除",\
		command=lambda: kick(Con)).pack(side=RIGHT)
	message_button = Button(main_frame_player_box, text="傳送",\
		command=lambda: transmit(Con, mes, chatbox)).pack(side=RIGHT)
	message_textbox = Entry(main_frame_player_box, width=16, textvariable=mes).pack(side=RIGHT)
	message_label1 = Label(main_frame_player_box, text="勾選以下用戶做操作:").pack(side=LEFT)

	gamebt = Button(win, text='Game Start', command=lambda: game_restart(Con, chatbox)).pack()

	#window size setting
	w = win.winfo_reqwidth() # width for the Tk root
	h = win.winfo_reqheight() # height for the Tk root
	# get screen width and height
	ws = win.winfo_screenwidth() # width of the screen
	hs = win.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (700/2)
	y = (hs/2) - (600/2)
	# set the dimensions of the screen and where it is placed
	win.geometry('%dx%d+%d+%d' % (700, 600, x, y))
	win.mainloop()
