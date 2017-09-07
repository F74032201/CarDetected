from tkinter import *	
from threading import Thread
from colors import rgb,hex #pip3 install colors.py
import numpy as np
import cv2
from operator import itemgetter
import imutils

class PositionThread(Thread):
	def __init__(self, player):
		super(PositionThread, self).__init__()
		self.player = player
		
	def run(self):
		self.player.RefreshPos()

class Player(object):
	def __init__(self, root,name,UP,DP):
		super(Player, self).__init__()
		#obj of transformed frame
		self.UP = UP
		self.DP = DP

		self.root = root
		self.name = name
		self.pos = [0,0]
		self.Color = [0,0,0]

		#control the thread to be over
		self.Connected = True
		self.tmp_frame = None
		self.wallHigh = 14.5
		self.carHigh = 10
		#create thread to refresh position
		self.pos_thread = PositionThread(self)

		self.frame = LabelFrame(self.root,text = self.name,foreground = 'blue')
		self.frame.pack(fill='x',padx=10,pady=8)

		self.CheckVar = IntVar()
		self.C1 = Checkbutton(self.frame, variable = self.CheckVar,onvalue = 1, offvalue = 0).pack(side = LEFT)
		self.SetColorBtn=Button(self.frame,text="Set color",command=self.RefreshColor).pack(side = LEFT)

		self.RGB = Label(self.frame,text = 'color')
		self.RGB.pack(side = RIGHT)
		self.startbt = Button(self.frame, text = "Start", command = self.pos_thread.start).pack(side = LEFT)
		self.CarPosStr = StringVar()
		self.CarPosStr.set(str(self.pos))
		self.CarPos = Label(self.frame,textvariable = self.CarPosStr).pack(side = LEFT)
	def delete(self):
		self.frame.destroy()

	def RefreshColor(self):
		cv2.namedWindow('Set Color')
		cv2.setMouseCallback('Set Color',self.on_mouse)
		self.tmp_frame = self.UP.framethread.frame

		while True:
			# if ret == False:
			# 	break

			
			self.FindPos(self.tmp_frame,(0,0))
			print("1")
			cv2.imshow('Set Color',self.tmp_frame)
			self.tmp_frame = self.UP.framethread.frame
			print("2")
			if cv2.waitKey(1) & 0xFF == ord('s'):
				cv2.destroyWindow("Set Color")
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				break
		
	def on_mouse(self,event,x,y,flags,param):
		
		if event == cv2.EVENT_LBUTTONDOWN:
			
			#cv2.circle(self.tmp_frame,(x,y),5,[255,255,0],2)
			#print(self.Color)
			self.Color = [int(self.tmp_frame[y,x][0]),int(self.tmp_frame[y,x][1]),int(self.tmp_frame[y,x][2])]
			print(self.Color)
			#Set label color
			# self.RGB.config(bg = '#'+str(rgb(self.Color[0],self.Color[1],self.Color[2]).hex))

	def FindPos(self,src,lastcar):
		# print("in Find")
		#convert RGB to HSV
		hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

		color = np.uint8([[self.Color]])
		
		hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
		 
		hue = hsv_color[0][0][0]

		#sensitivity
		low = hue-5 if hue-5 > -1 else 0
		high = hue+5 if hue+5 < 256 else 255
		#set bound
		lower_range = np.array([low, 100, 100], dtype=np.uint8)
		upper_range = np.array([high, 255, 255], dtype=np.uint8)
		#make a mask
		mask = cv2.inRange(hsv, lower_range, upper_range)
		
		kernel = np.ones((5,5),np.uint8)

		opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
		closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
		
		dilation = cv2.dilate(opening,kernel,iterations = 10)
		erosion = cv2.erode(dilation,kernel,iterations = 5)
		
		
		blurred = cv2.GaussianBlur(dilation, (5, 5), 0)

		# find contours in the thresholded image
		cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		

		if (len(cnts)==0):		#can't detect. Use last result.
			# self.dst = src
			# ?self.pos = self.lastCenter
			print("QQ")
			return lastcar

		#find the max area
		maxArea = 0
		maxNum = 0
		for i in range(0,len(cnts)-1):
			if cv2.contourArea(cnts[i])>maxArea:
				maxArea = cv2.contourArea(cnts[i])
				maxNum = i
		
		moments = cv2.moments(cnts[maxNum])
		car = int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])

		cv2.circle( src, car, 5, (0, 0, 150), -1)
		return car

	def RefreshPos(self):
		Upos = [0,0]
		Dpos = [0,0]
		while self.Connected:
			#Find positions of two parallel planes
			Upos = self.FindPos(self.UP.Result,Upos)
			Dpos = self.FindPos(self.DP.Result,Dpos)

			#Calculate real position
			lastX = (( Upos[0] * self.carHigh ) + (Dpos[0] * (self.wallHigh - self.carHigh))) / self.wallHigh
			lastY = (( Upos[1] * self.carHigh ) + (Dpos[1] * (self.wallHigh - self.carHigh))) / self.wallHigh

			self.pos = (int(lastX),int(lastY))
			self.CarPosStr.set(str(self.pos))
			print(self.pos)


