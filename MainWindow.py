from tkinter import *	
import tkinter.font as font
from threading import Thread
import threading,os
from Connection import *

count = 0
class myThread(Thread):
	"""docstring for myThread"""
	def __init__(self, con):
		super(myThread, self).__init__()
		self.con = con
		self._stop_event = threading.Event()

	def run(self):
		self.con.WaitingConnection()

	def stop(self):
		print("Stop connection loop")
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()

def Exit(r):
	#sys.exit(0)
	os._exit(1)
	r.destroy()
	
		
def convert():
	global count,ConThread,Con
	if count%2:
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
	count=count+1
	

if __name__ == "__main__":
	win = Tk()
	main_frame = Frame(win)
	main_frame.pack()
	main_frame_player = LabelFrame(win,text="連線用戶",foreground='blue')
	main_frame_player.pack(fill='x',padx=10,pady=8)
	
	main_frame_player_box = LabelFrame(main_frame_player)
	main_frame_player_box.pack(fill='x',padx=10,pady=8)

	delete_button = Button(main_frame_player_box,text = "踢除").pack(side = RIGHT)
	message_button = Button(main_frame_player_box,text="傳送").pack(side = RIGHT)
	mes = StringVar()
	message_textbox = Entry(main_frame_player_box,width=16,textvariable = mes).pack(side = RIGHT)
	message_label1 = Label(main_frame_player_box,text="勾選以下用戶做操作:").pack(side = LEFT)
	#create connection obj

	Con = ServerConnection(main_frame_player)
	Con.OpenServerSocket()

	#Font setting
	helv36 = font.Font(family='Helvetica', size=18, weight=font.BOLD)
	btn_text = StringVar()
	btn_text.set("Start Server")
	StartServerBtn = Button(main_frame, textvariable= btn_text,command = convert,font = helv36)
	StartServerBtn.pack(side = LEFT)
	ExitBtn = Button(main_frame,text = "結束", command = lambda: Exit(win),font = helv36)
	ExitBtn.pack(side = RIGHT)

	

	#window size setting
	w = win.winfo_reqwidth() # width for the Tk root
	h = win.winfo_reqheight() # height for the Tk root
	# get screen width and height
	ws = win.winfo_screenwidth() # width of the screen
	hs = win.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (500/2)
	y = (hs/2) - (500/2)
	# set the dimensions of the screen and where it is placed
	win.geometry('%dx%d+%d+%d' % (500, 500, x, y))
	win.mainloop()
