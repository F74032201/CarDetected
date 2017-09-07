import numpy as np
import cv2
from operator import itemgetter
import imutils

class CarDetected:

    smoothCar = []
    lastCenter = [(0,0)]
    dst = []
    pos = []

    def __init__(self,Ccolor):
        self.Ccolor = Ccolor #Car color
        self.smoothCar = []
        self.lastCenter = [(0,0)]
        self.dst = []
        self.pos = []

    def FindCar(self,src):

        #convert RGB to HSV
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        color = np.uint8([[self.Ccolor]])
        
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
        

        if (len(cnts)==0):      #can't detect. Use last result.
            self.dst = src
            self.pos = self.lastCenter
            return

        # loop over the contours
        centres = []
        centerX = []
        centerY = []

        #find the max area
        maxArea = 0
        maxNum = 0
        for i in range(0,len(cnts)-1):
            if cv2.contourArea(cnts[i])>maxArea:
                maxArea = cv2.contourArea(cnts[i])
                maxNum = i
        
        moments = cv2.moments(cnts[maxNum])
        car = int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])

        #smooth the car 

        carX = 0
        carY = 0
        
        self.smoothCar.insert(0,car)
        if len(self.smoothCar)>=10:
            for i in range(0,len(self.smoothCar)-1):
                carX += self.smoothCar[i][0] * (2 ** (-i-1))
                carY += self.smoothCar[i][1] * (2 ** (-i-1))
            self.smoothCar.pop()
            car = (int(carX),int(carY))

            if (((self.lastCenter[0]-car[0])**2 + (self.lastCenter[1]-car[1])**2) **0.5 > 32):
                car = self.lastCenter

        self.lastCenter = car

        cv2.circle(src,car,5,(0,255,0),-1)
        # print(car)
        self.dst = src
        self.pos = self.lastCenter

    

class CarRealPosition:

    carHigh = 11
    wallHigh = 14.5
    pos = []
    def __init__(self,Ccolor):
        self.Ccolor = Ccolor #Car color
        self.Up_car = CarDetected(self.Ccolor)
        self.Down_car = CarDetected(self.Ccolor)
    def update(self, up_src, down_src):

        self.Up_car.FindCar(up_src)
        self.Down_car.FindCar(down_src)
     
        lastX = (( self.Up_car.pos[0]*self.carHigh ) + (self.Down_car.pos[0]*(self.wallHigh-self.carHigh)))/self.wallHigh
        lastY = (( self.Up_car.pos[1]*self.carHigh ) + (self.Down_car.pos[1]*(self.wallHigh-self.carHigh)))/self.wallHigh
        
        self.pos = (int(lastX),int(lastY))


class MapTransform:
    point=[]
    #pointDown=[]
    lastpoint=[]
    # map is 8*8
    height=512
    width=512
    size=512

    size_multi=0.5

    def __init__(self,Pcolor):
        self.Pcolor = Pcolor #b,g,r
        self.point=[]
        self.lastpoint=[]
        self.dst = None
        

    def FindPoint(self,lastpoint):
    
        #convert RGB to HSV
        hsv = cv2.cvtColor(self.src, cv2.COLOR_BGR2HSV)
        color = np.uint8([[self.Pcolor]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
        
        hue = hsv_color[0][0][0]

        #sensitivity
        low = hue-10 if hue-10 > -1 else 0
        high = hue+10 if hue+10 < 256 else 255
        #set bound
        lower_range = np.array([low, 50, 40], dtype=np.uint8)
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
        # for x in range(0,len(centres)):
        #   cv2.circle(self.src, centres[x], 5, (0, 0, 150), -1)

        if len(centres)==4:
            lastpoint = centres

        else:
            centres = lastpoint

        self.point = centres

    def SortPoint(self):
    
        self.point.sort(key=itemgetter(1))
        if int(self.point[0][0])>int(self.point[1][0]):
            temp = self.point.pop(0)
            self.point.insert(1,temp)
        if int(self.point[2][0])>int(self.point[3][0]):
            temp = self.point.pop(2)
            self.point.insert(3,temp)   
        # return point

    def Transform(self):
        pts1 = np.float32(self.point)
        pts2 = np.float32([[0,0],[self.width,0],[0,self.height],[self.width,self.height]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        self.dst = cv2.warpPerspective(self.src,M,(self.width,self.height))
        

    def update(self,src):
        self.src = src
        lastpoint = self.point
        self.FindPoint(lastpoint)
        self.SortPoint()
        self.Transform()


if __name__ == "__main__" :

    DP = MapTransform([207,134,174]) #Down Point #purple
    UP = MapTransform([172,91,73]) #Up Point #blue
    car = CarRealPosition([200,113,252])
    cap = cv2.VideoCapture('cut.mov')
    fc = 0
    # out = cv2.VideoWriter('home/shaimejump/Desktop/project/CarDetected/out.mp4',-1,30,(512,512))
    mapp = cv2.imread('map.jpg')
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        DP.update(frame)
        UP.update(frame)

        # cv2.imshow('UP',UP.dst)

        car.update(UP.dst, DP.dst)
        
        output = np.zeros((512,512,3), np.uint8)
        # newsrc = cv2.resize(mapp,None,fx=(512/514), fy=(512/514), interpolation = cv2.INTER_CUBIC)
        cv2.circle(output, car.pos, 5, (0, 0, 150), -1)
        
        # out.write(newsrc)
        if fc%60 == 0:
            cv2.imshow('ggg',output)

        fc = fc + 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
