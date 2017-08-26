import numpy as np
import cv2
from operator import itemgetter
import imutils



lastCenter_up_cam1 = [(0,0)]
lastCenter_down_cam1 = [(0,0)]
smoothCar_up_cam1 = []
smoothCar_down_cam1 = []

lastCenter_up_cam2 = [(0,0)]
lastCenter_down_cam2 = [(0,0)]
smoothCar_up_cam2 = []
smoothCar_down_cam2 = []

point=[]
point2=[]
point_cam2 = []
point2_cam2 = []

countt =0
i=0
# map is 6*10
height=512
width=512
size=512

size_multi=0.5
def find_car_cam1(src,b,g,r,Up):
    global lastCenter_up_cam1,lastCenter_down_cam1,smoothCar_up_cam1,smoothCar_down_cam1

    smoothCar = smoothCar_up_cam1 if Up else smoothCar_down_cam1
    lastCenter = lastCenter_up_cam1 if Up else lastCenter_down_cam1
    #convert RGB to HSV
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

    color = np.uint8([[[b, g, r]]])
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
    

    if (len(cnts)==0):
        return src,lastCenter

    # loop over the contours
    centres = []
    centerX = []
    centerY = []

    #find the max area
    maxArea = 0
    maxNum = 0
    for i in range(len(cnts)):
        if cv2.contourArea(cnts[i])>maxArea:
            maxArea = cv2.contourArea(cnts[i])
            maxNum = i
    moments = cv2.moments(cnts[maxNum])
    car = int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])

    #smooth the car 

    carX = 0
    carY = 0
    
    smoothCar.insert(0,car)
    if len(smoothCar)>=10:
        for i in range(0,len(smoothCar)-1):
            carX += smoothCar[i][0] * (2 ** (-i-1))
            carY += smoothCar[i][1] * (2 ** (-i-1))
        smoothCar.pop()
        car = (int(carX),int(carY))

        if (((lastCenter[0]-car[0])**2 + (lastCenter[1]-car[1])**2) **0.5 > 32):
            car = lastCenter
    if Up:
        lastCenter_up_cam1 = car
        smoothCar_up_cam1 = smoothCar
    else:
        lastCenter_down_cam1 = car
        smoothCar_down_cam1 = smoothCar

    cv2.circle(src,car,5,(0,255,0),-1)
    print(car)
    return src,car
    #cv2.imshow("mask", mask)
    #cv2.imshow("point",dst)
def find_car_cam2(src,b,g,r,Up):
    global lastCenter_up_cam2,lastCenter_down_cam2,smoothCar_up_cam2,smoothCar_down_cam2

    smoothCar = smoothCar_up_cam2 if Up else smoothCar_down_cam2
    lastCenter = lastCenter_up_cam2 if Up else lastCenter_down_cam2
    #convert RGB to HSV
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

    color = np.uint8([[[b, g, r]]])
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

    
    #cv2.imshow('n',blurred)
    # find contours in the thresholded image
    cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    

    if (len(cnts)==0):
        return src,lastCenter

    # loop over the contours
    centres = []
    centerX = []
    centerY = []

    #find the max area
    maxArea = 0
    maxNum = 0
    for i in range(len(cnts)):
        if cv2.contourArea(cnts[i])>maxArea:
            maxArea = cv2.contourArea(cnts[i])
            maxNum = i
    moments = cv2.moments(cnts[maxNum])
    car = int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])

    #smooth the car 

    carX = 0
    carY = 0
    
    smoothCar.insert(0,car)
    if len(smoothCar)>=10:
        for i in range(0,len(smoothCar)-1):
            carX += smoothCar[i][0] * (2 ** (-i-1))
            carY += smoothCar[i][1] * (2 ** (-i-1))
        smoothCar.pop()
        car = (int(carX),int(carY))

        #if (((lastCenter[0]-car[0])**2 + (lastCenter[1]-car[1])**2) **0.5 > 32):
            #car = lastCenter
    if Up:
        lastCenter_up_cam2 = car
        smoothCar_up_cam2 = smoothCar
    else:
        lastCenter_down_cam2 = car
        smoothCar_down_cam2 = smoothCar
        
    cv2.circle(src,car,5,(0,255,0),-1)
    print(car)
    return src,car

def find_center_cam1(src,b,g,r,lastpoint):
    
    #convert RGB to HSV
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    color = np.uint8([[[b, g, r]]])
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
    for x in range(0,len(centres)):
        cv2.circle(src, centres[x], 5, (0, 0, 150), -1)

    if len(centres)==4:
        lastpoint = centres

    else:
        centres = lastpoint

    

    return centres

def find_center_cam2(src,b,g,r,lastpoint):
    global countt
    #convert RGB to HSV
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    color = np.uint8([[[b, g, r]]])
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
    erosion = cv2.erode(closing,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 3)
    
    
    
    blurred = cv2.GaussianBlur(dilation, (5, 5), 0)

    newsrc = cv2.resize(blurred,None,fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
    

    
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
        cv2.circle(src, centres[x], 5, (0, 0, 150), -1)


    if len(centres)==4:
        lastpoint = centres

    else:
        centres = lastpoint

    
    print(centres)
    return centres

def sortpoint(point):
#    global point
    
    point.sort(key=itemgetter(1))
    if int(point[0][0])>int(point[1][0]):
        temp=point.pop(0)
        point.insert(1,temp)
    if int(point[2][0])>int(point[3][0]):
        temp=point.pop(2)
        point.insert(3,temp)
#    point.sort(key=lambda tup: tup[1])
#    newpoint=sorted(point, key=lambda tup: (tup[1], tup[0]))
#    point.sort(key=itemgetter(0))
    return point

def transform(src,dst,point):
    global size,width,height
#    src=cv2.resize(src,(0,0), fx=size_multi, fy=size_multi)
    pts1 = np.float32(point)
    pts2 = np.float32([[0,0],[width,0],[0,height],[width,height]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(src,M,(width,height))
    
    return dst
            
    
def cut_and_trans(img,src,point):
    
    img=cv2.resize(img,(0,0), fx=size_multi, fy=size_multi)
#    src1=cv2.resize(src,(0,0), fx=size_multi, fy=size_multi)
    
    cv2.namedWindow('image')
    cv2.setMouseCallback('image',draw_circle)
    
    while(1):
        cv2.imshow('image',img)
        k = cv2.waitKey(1) & 0xFF
        if k==27:
            break

    cv2.destroyAllWindows()
    sortpoint(point)
    
    dst = np.zeros((512,512,3), np.uint8)
    dst = transform(src,dst,point)
    
    return dst

cap1 = cv2.VideoCapture('/home/shaimejump/Desktop/project/CarDetected/cut.mov')
out = cv2.VideoWriter('qqqqqq.mov',-1,30,(512,512))


mapp = cv2.imread('ccc2.jpg')
mapp = cv2.flip(mapp,-1)


carHigh = 11
wallHigh = 14.5
lastY = 0
lastX = 0
last = 0

trans_count=0
trans_count2=0
cam_count = 0
while(True):
    cam_count = cam_count%2
    # Capture frame-by-frame
    ret, frame = cap1.read()
    if cam_count == 0:
        trans_count=trans_count%10
        if trans_count==0:
            point=find_center_cam1(frame,172,91,73,point) #blue
            point2=find_center_cam1(frame,207,134,174,point2) #red

            if len(point)==4:
                point=sortpoint(point)
            if len(point2)==4:
                point2=sortpoint(point2)

        trans_count=trans_count+1

        dst = np.zeros((512,512,3), np.uint8)
        dst=transform(frame,dst,point) 
        dst,B_car = find_car_cam1(dst,200,113,252,True)

        dst2 = np.zeros((512,512,3), np.uint8)
        dst2=transform(frame,dst2,point2)
        dst2,R_car = find_car_cam1(dst2,200,113,252,False)
     
        lastX = (( B_car[0]*carHigh ) + (R_car[0]*(wallHigh-carHigh)))/wallHigh
        lastY = (( B_car[1]*carHigh ) + (R_car[1]*(wallHigh-carHigh)))/wallHigh
        
        last = (int(lastX),int(lastY))
        cam_count = cam_count + 1
    else:
        cam_count = cam_count + 1
        continue
   

    newsrc = cv2.resize(mapp,None,fx=(512/514), fy=(512/514), interpolation = cv2.INTER_CUBIC)
    cv2.circle(newsrc, last, 5, (0, 0, 150), -1)


    out.write(newsrc)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


