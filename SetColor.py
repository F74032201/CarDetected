from tkinter import *
import sys


class popupWindow(object):
	def __init__(self,master):
		top=self.top=Toplevel(master)
		#set position
		w = top.winfo_reqwidth() # width for the Tk root
		h = top.winfo_reqheight() # height for the Tk root
		ws = master.winfo_screenwidth() # width of the screen
		hs = master.winfo_screenheight() # height of the screen
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		top.geometry('%dx%d+%d+%d' % (w, h, x, y))

		self.value_B=-1
		self.value_G=-1
		self.value_R=-1

		self.l1=Label(top,text="B:")
		self.l1.pack()
		self.BGR_B=Entry(top)
		self.BGR_B.pack()
		#textbox for enter bgr
		self.l2=Label(top,text="G:")
		self.l2.pack()
		self.BGR_G=Entry(top)
		self.BGR_G.pack()

		self.l3=Label(top,text="R:")
		self.l3.pack()
		self.BGR_R=Entry(top)
		self.BGR_R.pack()

		self.b=Button(top,text='Ok',command=self.cleanup)
		self.b.pack()
	def cleanup(self):
		self.value_B=self.BGR_B.get()
		self.value_G=self.BGR_G.get()
		self.value_R=self.BGR_R.get()
		self.top.destroy()