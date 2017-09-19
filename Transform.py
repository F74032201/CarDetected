import numpy as np
import cv2
from operator import itemgetter
import imutils


class TransformMaze(object):
	def __init__(self,framethread):
		self.framethread = framethread
		self.Result = None
		self.dst = None
		self.Points = None
		self.Color = [0,0,255]
		self.lastpoint = None
		self.TransformContinue = True
		self.width = 512
		self.height = 512


	#for thread
	def RefreshResult(self):
		#Sorting points
		self.Points.sort(key=itemgetter(1))
		if int(self.Points[0][0])>int(self.Points[1][0]):
			temp = self.Points.pop(0)
			self.Points.insert(1,temp)
		if int(self.Points[2][0])>int(self.Points[3][0]):
			temp = self.Points.pop(2)
			self.Points.insert(3,temp) 

		#Transform
		pts1 = np.float32(self.Points)
		pts2 = np.float32([[0,0],[self.width,0],[0,self.height],[self.width,self.height]])
		M = cv2.getPerspectiveTransform(pts1,pts2)
		self.Result = cv2.warpPerspective(self.framethread.frame,M,(self.width,self.height)) 

	def RefreshColor(self):
		cv2.namedWindow('Set Color')
		cv2.setMouseCallback('Set Color',self.on_mouse)
		show_flag = True

		while True:
			# if ret == False:
			# 	break

			self.dst = self.framethread.frame
			self.RefreshPoints()
			
			if show_flag :
				cv2.imshow('Set Color',self.dst)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				
				show_flag = False

				break
		cv2.waitKey(1)
		cv2.destroyWindow("Set Color")
		cv2.waitKey(1)
		cv2.waitKey(1)
		cv2.waitKey(1)
		cv2.waitKey(1)


	def on_mouse(self,event,x,y,flags,param):
		
		if event == cv2.EVENT_LBUTTONDOWN:
			
			#cv2.circle(self.dst,(x,y),5,[255,255,0],2)
			#print(self.Color)
			self.Color = [int(self.dst[y,x][0]),int(self.dst[y,x][1]),int(self.dst[y,x][2])]
			print(self.Color)


	def RefreshPoints(self):
		#convert RGB to HSV
		hsv = cv2.cvtColor(self.framethread.frame, cv2.COLOR_BGR2HSV)
		color = np.uint8([[self.Color]])
		hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

		hue = hsv_color[0][0][0]

		#sensitivity
		low = hue-10 if hue-10 > -1 else 0
		high = hue+10 if hue+10 < 256 else 255
		#set bound
		lower_range = np.array([low, 100, 100], dtype=np.uint8)
		upper_range = np.array([high, 255, 255], dtype=np.uint8)
		#make a mask
		mask = cv2.inRange(hsv, lower_range, upper_range)
		kernel = np.ones((5,5),np.uint8)

		closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,kernel)
		erosion = cv2.erode(mask,kernel,iterations = 1)
		dilation = cv2.dilate(erosion,kernel,iterations = 3)


		blurred = cv2.GaussianBlur(dilation, (5, 5), 0)

		#newsrc = cv2.resize(blurred,None,fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)


		# find contours in the thresholded image
		cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		# loop over the contours
		centres = []
		res=[]
		for i in range(len(cnts)):
		    moments = cv2.moments(cnts[i])
		    centres.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
		for x in range(0,len(centres)):
			cv2.circle(self.dst, centres[x], 5, (0, 0, 150), -1)
		print(centres)
		if len(centres)==4:
		    self.lastpoint = centres

		else:
		    centres = self.lastpoint

		self.Points = centres

