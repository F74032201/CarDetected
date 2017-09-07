from tkinter import *	
import tkinter.font as font
from tkinter.scrolledtext import *
from threading import Thread
from Transform import *
import threading,os
from Connection import *
import numpy as np
import cv2

start_count = 0
maze_count = 0

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
		while True:
			self.UP.RefreshResult()
			self.UP.RefreshResult()

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
			ret, self.frame = self.cap.read()
			if ret == False:
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
				Con.DELETE(idx)
				
def transmit(Con,mes):
	tmp_message = mes.get()
	for idx in list(Con.player):
		if type(Con.player[idx]) != type('a'):
			if Con.player[idx].CheckVar.get():
				Con.ser_send_data(idx,tmp_message)
				mes.set('')
	
def refresh_4(UP,DP):
	UP.RefreshPoints()
	DP.RefreshPoints()
	print("refresh points")

def MazeColor(UP,DP):
	UP.RefreshColor()
	DP.RefreshColor()
	print("refresh color")	

def MazeUpdate(UP,DP,MazeUpdateBtn):
	TransformThread = myThreadTransform(UP,DP)
	TransformThread.start()
	MazeUpdateBtn.config(state = DISABLE)



if __name__ == "__main__":
	win = Tk()

	#create camera obj
	cap = cv2.VideoCapture(0)
	framethread = myThreadFrame(cap)
	framethread.start()
	UP = TransformMaze(framethread)
	DP = TransformMaze(framethread)

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
	MazeColorBtn = Button(main_frame,text = "設定四角顏色", command = lambda: MazeColor(UP,DP),font = helv36)
	MazeColorBtn.pack(side = LEFT)
	Mbtn_text = StringVar()
	Mbtn_text.set("開始校正")
	MazeUpdateBtn = Button(main_frame,text = "開始校正", command = lambda: MazeUpdate(UP,DP,MazeUpdateBtn),font = helv36)
	MazeUpdateBtn.pack(side = LEFT)

	main_frame_chat = LabelFrame(win ,bg = '#a3a8a7')
	main_frame_chat.pack(fill='x',padx=10,pady=8)
	chatbox = ScrolledText(main_frame_chat,height = 15)
	chatbox.pack(padx=10,pady=8)
	chatboxbt = Button(win , text = 'clear' ,command=lambda: chatbox.delete(1.0,END)).pack()

	main_frame_player = LabelFrame(win,text = "連線玩家",foreground = 'blue')
	main_frame_player.pack(fill='x',padx=10,pady=2)
	
	main_frame_player_box = LabelFrame(main_frame_player)
	main_frame_player_box.pack(fill='x',padx=10,pady=8)

	
	#create connection obj
	Con = ServerConnection(main_frame_player , chatbox , UP, DP)
	Con.OpenServerSocket()

	mes = StringVar()
	refresh_4point = Button(main_frame_player_box , text = "攝影機晃到" , command = lambda:refresh_4(UP,DP)).pack(side = RIGHT)
	delete_button = Button(main_frame_player_box, text = "踢除" , command = lambda: kick(Con)).pack(side = RIGHT)
	message_button = Button(main_frame_player_box, text="傳送" , command = lambda: transmit(Con,mes)).pack(side = RIGHT)	
	message_textbox = Entry(main_frame_player_box, width=16, textvariable = mes).pack(side = RIGHT)
	message_label1 = Label(main_frame_player_box,text="勾選以下用戶做操作:").pack(side = LEFT)	

	

	

	#window size setting
	w = win.winfo_reqwidth() # width for the Tk root
	h = win.winfo_reqheight() # height for the Tk root
	# get screen width and height
	ws = win.winfo_screenwidth() # width of the screen
	hs = win.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (600/2)
	y = (hs/2) - (600/2)
	# set the dimensions of the screen and where it is placed
	win.geometry('%dx%d+%d+%d' % (600, 600, x, y))
	win.mainloop()
