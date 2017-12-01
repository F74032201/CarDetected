from tkinter import *	
import tkinter.font as font
from tkinter.scrolledtext import *
from threading import Thread
from Transform import *
import threading,os
from Connection import *
from TowerGame import *
import numpy as np
import cv2

start_count = 0


class myThread(Thread):
	"""docstring for myThread"""
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

#Thread for updating the maze
class myThreadTransform(Thread):
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

			# if show_flag:
			# 	cv2.imshow('UP (w to quit)',self.UP.Result)
			# 	cv2.imshow('DP (w to quit)',self.DP.Result)

			# if cv2.waitKey(1) & 0xFF == ord('w'):				
			# 	show_flag = not show_flag
			# 	# cv2.waitKey(1)
			# 	cv2.destroyWindow("UP (w to quit)")
			# 	cv2.destroyWindow("DP (w to quit)")
			# 	# cv2.waitKey(1)
			# 	# cv2.waitKey(1)
			# 	# cv2.waitKey(1)
			# 	# cv2.waitKey(1)


	def stop(self):
		print("Stop connection loop")
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()


class myThreadFrame(Thread):
	def __init__(self, cap):
		Thread.__init__(self)
		self.cap = cap
		self.frame = None

	def run(self):
		while True:
			ret, Frame = self.cap.read()

			self.frame = cv2.resize(Frame,None,fx=1, fy=1, interpolation = cv2.INTER_CUBIC)
			if ret == False:
				break


class GameThread(Thread):
	def __init__(self, Con):
		super(GameThread, self).__init__()
		self.Con = Con
		self.App = App(self.Con)
		
	def run(self):
		for idx in list(self.Con.player):
			if type(self.Con.player[idx]) != type('a'):
				self.Con.player[idx].game_init()
				ChangeColor(self.Con.player[idx].image,self.Con.player[idx].Color)
		self.App.on_execute()

class MazeColorThread(Thread):
	"""Thread for picking maze color."""
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
	os._exit(1)
	r.destroy()
	
		
def convert():
	global start_count,ConThread,Con
	if start_count%2:
		btn_text.set("Start Server")

		#delete Connection obj
		for x in Con.player:
			if type(Con.player[x]) != type('a'):
				Con.player[x].delete()
		Con.player = {Con.server_socket:"Master"}
		ConThread.stop()
		
	else:
		btn_text.set("Close Server")	
		ConThread = myThread(Con)
		ConThread.start()
		print("Waiting")
	start_count=start_count+1

def kick(Con):
	for idx in list(Con.player):
		if type(Con.player[idx]) != type('a'):
			if Con.player[idx].CheckVar.get():
				# Con.player[idx].Connected = False
				# Con.player[idx].delete()
				# del Con.player[idx]
		
				Con.DELETE(idx)
				
def transmit(Con,mes,chatbox):
	tmp_message = mes.get()
	for idx in list(Con.player):
		if type(Con.player[idx]) != type('a'):
			if Con.player[idx].CheckVar.get():
				Con.ser_send_data(idx,tmp_message)
				mes.set('')
				chatbox.insert(INSERT, 'Master send to %s : %s\n' %(Con.player[idx].name,tmp_message))
				chatbox.see(END)
	
def create_refresh4_thread(UP, DP):
	refresh4_thread = RefreahPointsThread(UP, DP)
	refresh4_thread.start()
	print("refresh points")
# def refresh_4(UP,DP):
# 	UP.RefreshPoints()
# 	DP.RefreshPoints()
# 	print("refresh points")

def create_mazecolor_thread(UP, DP):
	mazecolor_thread = MazeColorThread(UP,DP)
	mazecolor_thread.start()
	print("refresh color")	

def MazeUpdate(UP, DP, MazeUpdateBtn):
	TransformThread = myThreadTransform(UP,DP)
	TransformThread.start()
	MazeUpdateBtn.config(state = "disable")

def DisplayCar():
	global Con
	cv2.namedWindow('Car Display')

	while True:
		mapp = cv2.imread("666.jpg")
		for idx in list(Con.player):
			if type(Con.player[idx]) != type('a'):
				if Con.player[idx].CheckVar.get():
					print(Con.player[idx].Color)
					cv2.circle(mapp, Con.player[idx].pos, 5, Con.player[idx].Color, -1)
		
		cv2.imshow("Car Display",mapp)
		print(Con.player[idx].pos)
		print(Con.player[idx].Color)
		
		if cv2.waitKey(1) & 0xFF == ord('d'):
			cv2.destroyWindow("Car Display")
			cv2.waitKey(1)
			cv2.waitKey(1)
			cv2.waitKey(1)
			cv2.waitKey(1)
			break

def GameRestart(Con,chatbox):
	gamethread = GameThread(Con)
	gamethread.start()

	#send start to everyone
	for idx in list(Con.player):
		if type(Con.player[idx]) != type('a'):
			Con.ser_send_data(idx,"Start")
			chatbox.insert(INSERT, 'Master send to %s : %s\n' %(Con.player[idx].name,"Start"))
			chatbox.see(END)

if __name__ == "__main__":
	win = Tk()

	#create camera obj
	cap = cv2.VideoCapture(0)

	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280);
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720);

	framethread = myThreadFrame(cap)
	framethread.start()
	UP = TransformMaze(framethread)
	UP.Color = [36, 11, 185]
	DP = TransformMaze(framethread)
	DP.Color = [137, 76, 10]
	main_frame = Frame(win)
	main_frame.pack()

	#Font setting
	helv36 = font.Font(family='Helvetica', size=18, weight=font.BOLD)
	btn_text = StringVar()
	#Top
	btn_text.set("Start Server")
	StartServerBtn = Button(main_frame, textvariable= btn_text,command = convert,font = helv36)
	StartServerBtn.pack(side = LEFT)
	ExitBtn = Button(main_frame,text = "結束", command = lambda: Exit(win),font = helv36)
	ExitBtn.pack(side = RIGHT)
	MazeColorBtn = Button(main_frame,text = "設定四角顏色", command = lambda: create_mazecolor_thread(UP,DP),font = helv36)
	MazeColorBtn.pack(side = LEFT)
	Mbtn_text = StringVar()
	Mbtn_text.set("開始校正")
	MazeUpdateBtn = Button(main_frame,text = "開始校正", command = lambda: MazeUpdate(UP,DP,MazeUpdateBtn),font = helv36)
	MazeUpdateBtn.pack(side = LEFT)

	main_frame_chat = LabelFrame(win ,bg = '#a3a8a7')
	main_frame_chat.pack(fill='x',padx=10,pady=8)
	chatbox = ScrolledText(main_frame_chat,height = 5)
	chatbox.pack(padx=10,pady=8)
	chatboxbt = Button(win , text = 'clear' ,command=lambda: chatbox.delete(1.0,END)).pack()

	# printbt = Button(win , text = 'display' ,command=lambda: DisplayCar() ).pack()


	main_frame_player = LabelFrame(win,text = "連線玩家",foreground = 'blue')
	main_frame_player.pack(fill='x',padx=10,pady=2)
	
	main_frame_player_box = LabelFrame(main_frame_player)
	main_frame_player_box.pack(fill='x',padx=10,pady=8)

	main_frame_player_team = LabelFrame(main_frame_player)
	main_frame_player_team.pack(fill='x',padx=10,pady=8)

	# main_frame_player_teamA = LabelFrame(main_frame_player_team,text = "Team A",foreground="red")
	# main_frame_player_teamA.pack(side = LEFT)

	# main_frame_player_teamB = LabelFrame(main_frame_player_team,text = "Team B",foreground="red")
	# main_frame_player_teamB.pack(side = RIGHT)
	
	border_H = 7
	border_W = 7
	block_size = 64
	#create connection obj
	Con = ServerConnection(main_frame_player_team, chatbox , UP, DP,border_H,border_W,block_size)
	Con.OpenServerSocket()

	mes = StringVar()
	refresh_4point = Button(main_frame_player_box , text = "攝影機晃到" , command = lambda:create_refresh4_thread(UP,DP)).pack(side = RIGHT)
	delete_button = Button(main_frame_player_box, text = "踢除" , command = lambda: kick(Con)).pack(side = RIGHT)
	message_button = Button(main_frame_player_box, text="傳送" , command = lambda: transmit(Con,mes,chatbox)).pack(side = RIGHT)	
	message_textbox = Entry(main_frame_player_box, width=16, textvariable = mes).pack(side = RIGHT)
	message_label1 = Label(main_frame_player_box,text="勾選以下用戶做操作:").pack(side = LEFT)	

	
	gamebt = Button(win , text = 'Game Start' ,command= lambda: GameRestart(Con,chatbox) ).pack()


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
