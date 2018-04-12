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
	"""
	Thread for updating player's position.

	Args:
		player: object of individual player.
	"""
	def __init__(self, player):
		super(PositionThread, self).__init__()
		self.player = player
		
	def run(self):
		if self.player.image != None:
			ChangeColor(self.player.image, self.player.Color)
		self.player.RefreshPos()

class SetcolorThread(Thread):
	"""
	Create a thread to set color of player, triggered by button 'set color'.
	
	Args:
		player: object of individual player.
	"""
	def __init__(self, player):
		Thread.__init__(self)
		self.player = player

	def run(self):
		self.player.RefreshColor()

class Player(object):
	"""
	A class to collect information of players, and provide some functions
	to change players' information.

	Args:
		root: Object of mainwindow.
		name: Player's ID.
		UP, DP: object of class TransformMaze, used to calculate and transform upside, downside four points of map.
		border_H, border_W: Range of coordinates in x, y.
		block_size: Size of one unit of coordinates.

	"""
	def __init__(self, root,name,UP,DP,border_H,border_W,block_size):
		super(Player, self).__init__()
		#obj of transformed frame
		self.UP = UP
		self.DP = DP
		self.root = root
		self.name = name
		self.border_H = border_H
		self.border_W = border_W
		self.block_size = block_size

		self.blood = 180			# initial blood of player.
		self.blood_count = 180		# set a count of decreasing blood.
		self.stay_time = 0			# The time that the player stays.
		self.stay_pos = (-1,-1)		# The position that the player stays. 
		self.still_alive = True		# Record whether the player is alive.
		self.score = 0				# Record how many scores did the player get.
		self.picwidth =32			# The car icon picture size.	
		self.BaseOpen = False		# Record whether the team's base is open.
		
		self.x = 0					# Player's current coordinates.
		self.y = 0
		self.Color = [0,0,0]		# Car's color.
		self.team = None			# Player's team.
		self.image = None			# The car's image.

		# integer that record the time.
		self.game_time_min = 0
		self.game_time_sec = 0
		self.game_time_sec10 = 0

		# control the thread to be over.
		self.Connected = True
		self.tmp_frame = None
		self.wallHigh = 10
		self.carHigh = 10

		# create thread to refresh position.
		self.pos_thread = PositionThread(self)

		# Frame of each player on the main window.
		self.frame = LabelFrame(self.root,text = self.name,foreground = 'blue')
		self.frame.pack(fill='x',padx=10,pady=8)

		# Check button value. When the check box is selected the value would be 1, otherwise 0.
		self.CheckVar = IntVar()
		self.C1 = Checkbutton(self.frame, variable = self.CheckVar, onvalue = 1, offvalue = 0).pack(side = LEFT)
		
		# Button that trigger function 'create_setcolor_thread' to set the car's color.
		self.SetColorBtn=Button(self.frame, text="Set color", command=self.create_setcolor_thread).pack(side = LEFT)

		# Label for showing the selected color. 
		self.RGB = Label(self.frame,text = '   ')
		self.RGB.pack(side = LEFT)

		# Button that start the thread 'pos_thread' to start the game.
		self.startbt = Button(self.frame, text = "Start", command = self.pos_thread.start).pack(side = LEFT)

		# Blood and score label.	
		self.BSVar = StringVar()
		self.BSVar.set('HP:'+str(self.blood) + '/score:'+str(self.score))
		self.BSlabel = Label(self.frame, textvariable = self.BSVar)
		self.BSlabel.bind("<Button-1>", self.blood_add)			# Left click the label to add blood.
		self.BSlabel.bind("<Button-3>", self.blood_minus)		# Right click the label to minus blood.
		self.BSlabel.pack(side = RIGHT)

		# Button that set car high.
		self.HighStr = StringVar()
		self.HighBtn = Button(self.frame,text = "設定車高",command =self.SetCarHigh).pack(side = RIGHT)
		self.SetHighTextBox = Entry(self.frame,width = 4,textvariable = self.HighStr).pack(side = RIGHT)

		# Label that display car position.
		self.CarPosStr = StringVar()
		self.CarPosStr.set(str(self.pos))
		self.CarPos = Label(self.frame,textvariable = self.CarPosStr).pack(side = LEFT)
	
	def delete(self):
		"""Delete the frame on main window."""
		self.frame.destroy()

	def blood_add(self ,event):
		"""Add 1 blood and change the label."""
		self.blood += 1
		self.BSVar.set('HP:'+str(self.blood) + '/score:'+str(self.score))

	def blood_minus(self ,event):
		"""Minus 1 blood and change the label."""
		self.blood -= 1
		self.BSVar.set('HP:'+str(self.blood) + '/score:'+str(self.score))

	def create_setcolor_thread(self):
		"""function for creating a thread to set color of player."""
		setcolor_thread = SetcolorThread(self)
		setcolor_thread.start()

	def RefreshColor(self):
		"""
		Show the window and select the color of player. Press s to quit the loop.
		"""
		# Create a window titled the string.
		cv2.namedWindow('Set Color (s to quit)')

		# Set click event to acquire the RGB where the mose click.
		cv2.setMouseCallback('Set Color (s to quit)',self.on_mouse)
		
		# Lock the resource when altering it.
		self.DP.Result_lock.acquire()
		self.tmp_frame = self.DP.Result
		self.DP.Result_lock.release()

		# Endless loop that show the result of DP and let the user select the color.
		while True:
			# Find the position of player's color and print a red point on it. 
			car = self.FindPos(self.tmp_frame, self.DP.Result_lock, (0,0))
			cv2.circle( self.tmp_frame, car, 5, (0, 0, 150), -1)

			# Show the frame that has been changed.
			cv2.imshow('Set Color (s to quit)',self.tmp_frame)
			cv2.waitKey(1)
			cv2.waitKey(1)
			cv2.waitKey(1)
			cv2.waitKey(1)
			self.DP.Result_lock.acquire()
			self.tmp_frame = self.DP.Result
			self.DP.Result_lock.release()

			# Fill in lines of waitkey to get rid of the bug of opencv.(Crash when destroy the window.)
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
		"""Click event and save select color."""
		if event == cv2.EVENT_LBUTTONDOWN:			
			#cv2.circle(self.tmp_frame,(x,y),5,[255,255,0],2)
			#print(self.Color)
			self.Color = [int(self.tmp_frame[y,x][0]),int(self.tmp_frame[y,x][1]),int(self.tmp_frame[y,x][2])]
			print(self.Color)
			

	def FindPos(self, src, lock, lastcar):
		"""
		Function that update position of selected color of player.

		Args:
			src: The frame has been transformed.
			lock: Set a lock mechanism to prevent from race condition problem.
			lastcar: Last time position.

		Returns: 
			car: Calculated position.
		"""

		# Convert RGB to HSV and set lock when change the source. 
		lock.acquire()
		hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
		lock.release()
		color = np.uint8([[self.Color]])
	
		hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
		
		# First parameter of hsv is hue.
		hue = hsv_color[0][0][0]

		# Set the sensitivity.(Collect the area of interval (hue-4, hue+4).)
		low = hue-4 if hue-4 > -1 else 0
		high = hue+4 if hue+4 < 256 else 255

		# Set bound with low sensitivity of hue.Saturation and brightness in the interval of (100,255).
		lower_range = np.array([low, 100, 100], dtype=np.uint8)
		upper_range = np.array([high, 255, 255], dtype=np.uint8)

		# Create a mask that reverse the selected area.
		mask = cv2.inRange(hsv, lower_range, upper_range)
		
		# Declare an array that the values are all 1 with the data type. 
		kernel = np.ones((5,5), np.uint8)

		# Apply Opening Morphological Transformation to remove small objects.
		opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
		
		# The dilatation will make the object in white bigger and eliminate some small black objects.
		dilation = cv2.dilate(opening, kernel, iterations = 10)
		# The erosion will make the object in white smaller with the disappear black objects.
		erosion = cv2.erode(dilation, kernel, iterations = 5)
		
		# Smooth the image with Gaussian Filter.
		blurred = cv2.GaussianBlur(dilation, (5, 5), 0)

		# Find contours in the thresholded image and save them into cnts.
		cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		
		# If there is no contours, use the last result.
		if (len(cnts)==0):		
			return lastcar

		# Find the largest area in cnts.
		maxArea = 0
		maxNum = 0
		for i in range(0,len(cnts)-1):
			if cv2.contourArea(cnts[i])>maxArea:
				maxArea = cv2.contourArea(cnts[i])
				maxNum = i
		
		# Save the center point(coordinate) of the largest area into car.			
		moments = cv2.moments(cnts[maxNum])
		car = int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])
		
		return car

	def RefreshPos(self):
		"""
		Calculate the acurrate position by Interpolation method.
		Continuous computation on the server side.
		"""
		Upos = [0,0]
		Dpos = [0,0]

		# Endless loop until the player disconnect.
		while self.Connected:
			# Find positions of two parallel planes
			Upos = self.FindPos(self.UP.Result,self.UP.Result_lock,Upos)
			Dpos = self.FindPos(self.DP.Result,self.DP.Result_lock,Dpos)
			
			# Calculate real position with Interpolation method.
			lastX = (( Upos[0] * self.carHigh ) + (Dpos[0] * (self.wallHigh - self.carHigh))) / self.wallHigh
			lastY = (( Upos[1] * self.carHigh ) + (Dpos[1] * (self.wallHigh - self.carHigh))) / self.wallHigh

			# Convert the coordinate from 512*512 to custom size(default 579*576).
			self.x, self.y = (int(lastX / 512 * self.border_W * self.block_size - self.picwidth/2)\
				, int(lastY / 512 * self.border_H * self.block_size - self.picwidth/2))
			# Change the coordinate label on the mainwindow.
			self.CarPosStr.set(str((int(lastX + self.picwidth/2), int(lastY + self.picwidth/2))))

	def game_init(self):
		"""
		Initialize some variable when game start.
		"""
		self.map_width = self.border_W * self.block_size
		self.map_height = self.border_H * self.block_size
		self.direction = 0		# direction of right left up down(0~3).
		self.angle = 0			# Polar coordinates.

		# Load car icon into image and adjust the size.
		self.image = pygame.image.load("img/car.png").convert()		
		self.image = pygame.transform.scale(self.image, (self.picwidth, self.picwidth))

		# Set the font to display blood volume of the game window.
		self.bloodfont = pygame.font.SysFont('Comic Sans MS', 20)
		self._blood_surf = self.bloodfont.render("Hp:"+str(self.blood), False, (0, 0, 0))

	def update(self):
		""""Update position of player by each move."""
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
		# update score and blood
		self.BSVar.set('HP:'+str(self.blood) + '/score:'+str(self.score))

	def moveRight(self):
		self.direction = 0
	
	def moveLeft(self):
		self.direction = 1
	
	def moveUp(self):
		self.direction = 2

	def moveDown(self):
		self.direction = 3
	
	def draw(self, surface):
		# Draw the image onto the game window at its accurrate position.
		surface.blit(self.image,(self.x,self.y))
		surface.blit(self._blood_surf, (self.x-7, self.y-10))


	def SetCarHigh(self):
		# Set the car height by the textbox.
		self.carHigh = int(self.HighStr.get())
		print("%s's car high set to %d" %(self.name,self.carHigh))

	def big_pos(self):
		"""Return the roughly position of nxn."""
		return (int((self.x+16) / self.block_size), int((self.y+16) / self.block_size))

