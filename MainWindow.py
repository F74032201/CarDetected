from tkinter import *	
from threading import Thread
import threading
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
		
def convert():
	global count,ConThread,Con
	if count%2:
		btn_text.set("Start Server")

		#delete Connection obj
		Con.CONNECTION_DICT = {Con.server_socket:"Master"}	
		ConThread.stop()

	else:
		btn_text.set("Close Server")
		#Con,ConThread = CreateCon()
				
		ConThread = myThread(Con)
		ConThread.start()
		print("Waiting")
	count=count+1
	

if __name__ == "__main__":
	win = Tk()

	#create connection obj
	Con = ServerConnection()
	Con.OpenServerSocket()
	btn_text = StringVar()
	btn_text.set("Start Server")
	StartServerBtn = Button(textvariable= btn_text,command = convert)
	StartServerBtn.pack()



	#window size setting
	w = win.winfo_reqwidth() # width for the Tk root
	h = win.winfo_reqheight() # height for the Tk root
	# get screen width and height
	ws = win.winfo_screenwidth() # width of the screen
	hs = win.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)
	# set the dimensions of the screen and where it is placed
	win.geometry('%dx%d+%d+%d' % (w, h, x, y))
	win.mainloop()
