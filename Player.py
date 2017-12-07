from tkinter import *	
from threading import Thread
from colors import rgb,hex #pip3 install colors.py
import numpy as np
import cv2
from operator import itemgetter
import imutils
from TowerGame import ChangeColor
from pygame.locals import *
import pygame


class PositionThread(Thread):
	def __init__(self, player):
		super(PositionThread, self).__init__()
		self.player = player
		
	def run(self):
		if self.player.image != None:
			ChangeColor(self.player.image, self.player.Color)
		self.player.RefreshPos()

class SetcolorThread(Thread):
	"""Thread for setting color."""
	def __init__(self, player):
		Thread.__init__(self)
		self.player = player

	def run(self):
		self.player.RefreshColor()

	

class Player(object):
	def __init__(self, root,name,UP,DP,border_H,border_W,block_size):
		super(Player, self).__init__()
		#obj of transformed frame
		self.UP = UP
		self.DP = DP

		self.root = root
		self.name = name
		self.id = 0
		self.done = False
		self.dst_sent = False

		self.pos = (-1,-1)
		self.posUsr = (-1,-1)
		self.border_H = border_H
		self.border_W = border_W
		self.block_size = block_size
		self.picwidth =32
		
		self.x = 0
		self.y = 0
		self.Color = [0,0,0]
		self.team = None
		self.image = None

		self.game_time_min = 0
		self.game_time_sec = 0
		self.game_time_sec10 = 0

		#control the thread to be over
		self.Connected = True
		self.tmp_frame = None
		self.wallHigh = 14.5
		self.carHigh = 10
		self.carDst = (0,0)
		#create thread to refresh position
		self.pos_thread = PositionThread(self)

		self.frame = LabelFrame(self.root,text = self.name,foreground = 'blue')
		self.frame.pack(fill='x',padx=10,pady=8)

		self.CheckVar = IntVar()
		self.C1 = Checkbutton(self.frame, variable = self.CheckVar,onvalue = 1, offvalue = 0).pack(side = LEFT)
		self.SetColorBtn=Button(self.frame,text="Set color",command=self.create_setcolor_thread).pack(side = LEFT)

		self.RGB = Label(self.frame,text = 'color')
		self.RGB.pack(side = RIGHT)
		self.startbt = Button(self.frame, text = "Start", command = self.pos_thread.start).pack(side = LEFT)
		self.HighStr = StringVar()
		self.HighBtn = Button(self.frame,text = "設定車高",command =self.SetCarHigh).pack(side = RIGHT)
		self.SetHighTextBox = Entry(self.frame,width = 8,textvariable = self.HighStr).pack(side = RIGHT)
		
		self.DstStr = StringVar()
		self.DstBtn = Button(self.frame,text = "設定目的地",command =self.SetCarDst).pack(side = RIGHT)
		self.SetDstTextBox = Entry(self.frame,width = 8,textvariable = self.DstStr).pack(side = RIGHT)
		
		self.CarPosStr = StringVar()
		self.CarPosStr.set(str(self.pos))
		self.CarPos = Label(self.frame,textvariable = self.CarPosStr).pack(side = LEFT)
	def delete(self):
		self.frame.destroy()

	def create_setcolor_thread(self):
		setcolor_thread = SetcolorThread(self)
		setcolor_thread.start()

	def RefreshColor(self):
		cv2.namedWindow('Set Color (s to quit)')
		cv2.setMouseCallback('Set Color (s to quit)',self.on_mouse)
		self.tmp_frame = self.DP.Result

		while True:
			# if ret == False:
			# 	break

			
			car = self.FindPos(self.tmp_frame,(0,0))
			cv2.circle( self.tmp_frame, car, 5, (0, 0, 150), -1)
			# print("1")
			cv2.imshow('Set Color (s to quit)',self.tmp_frame)
			cv2.waitKey(1)
			cv2.waitKey(1)
			cv2.waitKey(1)
			cv2.waitKey(1)
			self.tmp_frame = self.DP.Result
			# print("2")
			if cv2.waitKey(1) & 0xFF == ord('s'):
				cv2.destroyWindow("Set Color (s to quit)")
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				break
		#Set label color
		self.RGB.config(bg = '#'+str(rgb(self.Color[2],self.Color[1],self.Color[0]).hex))
		if self.image != None:
			ChangeColor(self.image, self.Color)

		
	def on_mouse(self,event,x,y,flags,param):
		
		if event == cv2.EVENT_LBUTTONDOWN:
			
			#cv2.circle(self.tmp_frame,(x,y),5,[255,255,0],2)
			#print(self.Color)
			self.Color = [int(self.tmp_frame[y,x][0]),int(self.tmp_frame[y,x][1]),int(self.tmp_frame[y,x][2])]
			print(self.Color)
			

	def FindPos(self,src,lastcar):
		# print("in Find")
		#convert RGB to HSV
		hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

		color = np.uint8([[self.Color]])
		
		hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
		 
		hue = hsv_color[0][0][0]

		#sensitivity
		low = hue-4 if hue-4 > -1 else 0
		high = hue+4 if hue+4 < 256 else 255
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
		# cv2.imshow("mask",blurred)

		# find contours in the thresholded image
		cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		

		if (len(cnts)==0):		#can't detect. Use last result.
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
			self.x, self.y = self.pos
			self.x, self.y = (int(self.x / 512 * self.border_W * self.block_size - self.picwidth/2)\
				,int(self.y / 512 * self.border_H * self.block_size - self.picwidth/2))
			self.CarPosStr.set(str((int(self.x + self.picwidth/2), int(self.y + self.picwidth/2))))
			# print(self.pos)

	def game_init(self):
		self.map_width = self.border_W * self.block_size
		self.map_height = self.border_H * self.block_size
		self.step = 32		
		self.direction = 0
		self.angle = 0
		self.image = pygame.image.load("img/car.png").convert()
		self.image = pygame.transform.scale(self.image,(self.picwidth,self.picwidth))

	def update(self):

		#update position of player

		if self.direction == 0:
			self.x += 10
			self.angle = 0

		if self.direction == 1:
			self.x -= 10
			self.angle = 180

		if self.direction == 2:
			self.y -= 10
			self.angle = 90

		if self.direction == 3:
			self.y += 10
			self.angle = 270
	
		if self.x > self.map_width-self.picwidth:
			self.x = self.map_width-self.picwidth
		if self.x < 0:
			self.x = 0
		if self.y > self.map_height-self.picwidth:
			self.y = self.map_height-self.picwidth
		if self.y < 0:
			self.y = 0

	def moveRight(self):
		self.direction = 0
	
	def moveLeft(self):
		self.direction = 1
	
	def moveUp(self):
		self.direction = 2

	def moveDown(self):
		self.direction = 3
	
	def draw(self, surface):
		#print(self.x,self.y)
		surface.blit(self.image,(self.x,self.y))


	def SetCarHigh(self):
		self.carHigh = int(self.HighStr.get())
		print("%s's car high set to %d" %(self.name,self.carHigh))

	def SetCarDst(self):
		tmp = self.DstStr.get()
		tmp = tmp.split(',',1)
		self.carDst = (int(tmp[0]),int(tmp[1]))
		print(self.carDst)
		#print("%s's car Dst set to %d" %(self.name,self.carDst))

