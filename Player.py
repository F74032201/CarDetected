from tkinter import *	
from threading import Thread
from colors import rgb,hex #pip3 install colors.py
import numpy as np
import cv2
from operator import itemgetter
import imutils
from pygame.locals import *
import pygame

from pacman import *


class PositionThread(Thread):
	def __init__(self, player):
		super(PositionThread, self).__init__()
		self.player = player
		
	def run(self):
		# if self.player.image != None:
		# 	ChangeColor(self.player.image, self.player.Color)
		self.player.RefreshPos()

class Player(object):
	last_x = 256+32
	last_y = 384+32
	def __init__(self, root,name,UP,DP,border_H,border_W,block_size):
		super(Player, self).__init__()
		#obj of transformed frame
		self.UP = UP
		self.DP = DP

		self.root = root
		self.name = name
		self.id = 0
		self.done = False

		self.pos = (-1,-1)
		self.posUsr = (-1,-1)
		self.border_H = border_H
		self.border_W = border_W
		self.block_size = block_size

		self.map_width = self.border_W * self.block_size
		self.map_height = self.border_H * self.block_size

		self.picwidth =32
		self.direction = 0
		self.angle = 0

		self.x = 0
		self.y = 0
		self.Color = [0,0,0]
		self.team = None


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
		self.HighStr = StringVar()
		self.HighBtn = Button(self.frame,text = "設定車高",command =self.SetCarHigh).pack(side = RIGHT)
		self.SetHighTextBox = Entry(self.frame,width = 8,textvariable = self.HighStr).pack(side = RIGHT)
		
		
		self.CarPosStr = StringVar()
		self.CarPosStr.set(str(self.pos))
		self.CarPos = Label(self.frame,textvariable = self.CarPosStr).pack(side = LEFT)

	def delete(self):
		self.frame.destroy()

	def RefreshColor(self):
		cv2.namedWindow('Set Color (s to quit)')
		cv2.setMouseCallback('Set Color (s to quit)',self.on_mouse)
		self.tmp_frame = self.DP.framethread.frame

		while True:
			# if ret == False:
			# 	break

			
			self.FindPos(self.tmp_frame,(0,0))
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
			self.x, self.y = self.pos
			self.x, self.y = (int(self.x / 512 * self.border_W * self.block_size)\
				,int(self.y / 512 * self.border_H * self.block_size))
			self.x, self.y = (self.x - self.block_size, self.y - self.block_size)
			self.CarPosStr.set(str((self.x, self.y)))
			# print(self.pos)

	def game_init(self):

		self.move_x = 0
		self.move_y = 0
		self.life = 10
		self.step = 8

		self._image_0 = pygame.image.load("img/pacman.png").convert()
		self._image_0 = pygame.transform.scale(self._image_0,(self.picwidth,self.picwidth))
		eraseBG(self._image_0)
		self._image_1 = pygame.image.load("img/pacman_1.png").convert()
		self._image_1 = pygame.transform.scale(self._image_1,(self.picwidth,self.picwidth))
		eraseBG(self._image_1)
		self._image_2 = pygame.image.load("img/pacman_2.png").convert()
		self._image_2 = pygame.transform.scale(self._image_2,(self.picwidth,self.picwidth))
		eraseBG(self._image_2)
		self._image_3 = pygame.image.load("img/pacman_3.png").convert()
		self._image_3 = pygame.transform.scale(self._image_3,(self.picwidth,self.picwidth))
		eraseBG(self._image_3)

		self.image = self._image_0

		self.image_count=0

	def update(self):
		#update position of player

		self.checkDir()

		self.angle = 0

		if self.direction == 0:
			# self.x += self.step
			self.angle = 0

		if self.direction == 1:
			# self.x -= self.step
			self.angle = 180

		if self.direction == 2:
			# self.y -= self.step
			self.angle = 90

		if self.direction == 3:
			# self.y += self.step
			self.angle = 270

		if self.image_count == 0:
			self.image = pygame.transform.rotate(self._image_0, self.angle)
		if self.image_count == 1:
			self.image = pygame.transform.rotate(self._image_1, self.angle)
		if self.image_count == 2:
			self.image = pygame.transform.rotate(self._image_2, self.angle)
		if self.image_count == 3:
			self.image = pygame.transform.rotate(self._image_3, self.angle)

	def show_x(self):
		# return self.x
		return self.x - self.picwidth/2
	def show_y(self):
		# return self.y
		return self.y - self.picwidth/2
	def map_x(self):
		r = int(self.x/self.block_size)
		return r
	def map_y(self):
		r = int(self.y/self.block_size)
		return r

	def checkDir(self):
		self.move_x = self.move_x + self.x - self.last_x
		self.move_y = self.move_y + self.y - self.last_y
		if abs(self.move_x) > abs(self.move_y) and abs(self.move_x) > 16:
			if self.move_x > 0:
				self.moveRight()
			else:
				self.moveLeft()
			self.move_x = 0
			self.move_y = 0
		elif abs(self.move_y) > 16:
			if self.move_y > 0:
				self.moveDown()
			else:
				self.moveUp()
			self.move_x = 0
			self.move_y = 0
		

	def moveRight(self):
		self.direction = 0
	
	def moveLeft(self):
		self.direction = 1
	
	def moveUp(self):
		self.direction = 2

	def moveDown(self):
		self.direction = 3
	
	def draw(self, surface):
		surface.blit(self.image,(self.x-self.picwidth/2,self.y-self.picwidth/2))


	def SetCarHigh(self):
		self.carHigh = int(self.HighStr.get())
		print("%s's car high set to %d" %(self.name,self.carHigh))


