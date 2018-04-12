import numpy as np
import cv2
from operator import itemgetter
import imutils
from threading import Thread, Lock

class TransformMaze(object):
	"""
	Class for transforming maze from trapezoid to square 

	Args:
		framethread: object of reading camera from class myThreadFrame
	"""
	def __init__(self,framethread):
		self.framethread = framethread
		self.Result = None				# Used to save the result of keystone correction.
		self.dst = None					# The result that display image.
		self.Points = None				# 2D list that save the coordinates of four corners.
		self.Color = [0,0,255]			# Color of four corners.
		self.lastpoint = None			# Last identified coordinates of four corners.
		self.width = 512				# Default frame wigth.
		self.height = 512				# Default frame height.
		self.Result_lock = Lock()		# Set a lock mechanism to prevent from race condition problem

	def RefreshResult(self):
		"""
		Use the four points found by color to generate a square resault

		Sort the points such that: first one at upper left, second one at upper right,
		third one at lower left, fourth one at lower right.
		Function warpPerspective will return the resault of correct one.
		"""
		self.Points.sort(key=itemgetter(1))
		if int(self.Points[0][0]) > int(self.Points[1][0]):
			temp = self.Points.pop(0)
			self.Points.insert(1, temp)
		if int(self.Points[2][0]) > int(self.Points[3][0]):
			temp = self.Points.pop(2)
			self.Points.insert(3, temp) 

		pts1 = np.float32(self.Points)
		pts2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
		M = cv2.getPerspectiveTransform(pts1, pts2)

		self.framethread.frame_lock.acquire()
		self.Result = cv2.warpPerspective(self.framethread.frame, M, (self.width, self.height)) 
		self.framethread.frame_lock.release()

	def RefreshColor(self):
		"""
		Mouse click to select the right color, refreshing the points at the meantime.
		"""
		# Create a window titled the string.
		cv2.namedWindow('Set Color (q to quit)')

		# Set click event to acquire the RGB where the mose click.
		cv2.setMouseCallback('Set Color (q to quit)', self.on_mouse)
		show_flag = True

		# Endless loop that let the user select the color and display the result with selected color.
		while True:
			# Lock the resource when altering it.
			self.framethread.frame_lock.acquire()
			self.dst = self.framethread.frame
			self.framethread.frame_lock.release()

			# Find the points with selected color and draw red dot on it.
			self.RefreshPoints()
			
			# Display the result until press 'q'
			if show_flag :
				cv2.imshow('Set Color (q to quit)', self.dst)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				show_flag = False
				# Fill in lines of waitkey to get rid of the bug of opencv.(Crash when destroy the window.)
				cv2.destroyWindow("Set Color (q to quit)")
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				cv2.waitKey(1)
				break	


	def on_mouse(self,event,x,y,flags,param):
		"""
		Set click event, and save the selected color in self.Color.
		"""
		if event == cv2.EVENT_LBUTTONDOWN:
			self.Color = [int(self.dst[y,x][0]),int(self.dst[y,x][1]),int(self.dst[y,x][2])]
			print(self.Color)


	def RefreshPoints(self):
		"""
		Find points of selected color with several OpenCV function

		Returns:
			Lists of found points 

		"""
		# Convert RGB to HSV and set lock when change the source. 
		self.framethread.frame_lock.acquire()
		hsv = cv2.cvtColor(self.framethread.frame, cv2.COLOR_BGR2HSV)
		self.framethread.frame_lock.release()
		color = np.uint8([[self.Color]])
		hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

		# First item of hsv is hue.
		hue = hsv_color[0][0][0]

		# Set the sensitivity.(Collect the area of interval (hue-10, hue+10).)
		low = hue-10 if hue-10 > -1 else 0
		high = hue+10 if hue+10 < 256 else 255
		
		# Set bound with low sensitivity of hue.Saturation and brightness in the interval of (100,255).
		lower_range = np.array([low, 100, 100], dtype=np.uint8)
		upper_range = np.array([high, 255, 255], dtype=np.uint8)
		
		# Create a mask that reverse the selected area.
		mask = cv2.inRange(hsv, lower_range, upper_range)

		# Declare an array that the values are all 1 with the data type. 
		kernel = np.ones((5,5),np.uint8)

		# The erosion will make the object in white smaller.
		erosion = cv2.erode(mask,kernel,iterations = 1)
		# The dilatation will make the object in white bigger and eliminate some small black objects.
		dilation = cv2.dilate(erosion,kernel,iterations = 3)

		# Smooth the image with Gaussian Filter.
		blurred = cv2.GaussianBlur(dilation, (5, 5), 0)

		# Find contours in the thresholded image and save them into cnts.
		cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		
		# Find every center point of contours and save in centres.
		centres = []
		res=[]
		for i in range(len(cnts)):
		    moments = cv2.moments(cnts[i])
		    centres.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
		
		# Draw red dot on the displayed frame.
		for x in range(0,len(centres)):
			cv2.circle(self.dst, centres[x], 5, (0, 0, 150), -1)
		
		# You can watch it to check whether there are 4 points have been recognized.
		print(centres)

		# If there are not 4 contours, it must be wrong then keep the last points as result.
		if len(centres)==4:
		    self.lastpoint = centres
		else:
		    centres = self.lastpoint

		self.Points = centres

