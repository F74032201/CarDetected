import numpy as np
import cv2
from operator import itemgetter
import imutils


class TransformMaze(object):
    """Information of transformed maze and result."""
    def __init__(self, framethread):
        self.framethread = framethread
        self.result = None
        self.dst = None
        self.points = None
        self.color = [0, 0, 255]
        self.lastpoint = None
        self.width = 512
        self.height = 512

    def refresh_result(self):
        """Save transformed result into object's result."""
        self.points.sort(key=itemgetter(1))     # Sort points in order to transform.
        if int(self.points[0][0]) > int(self.points[1][0]):
            temp = self.points.pop(0)
            self.points.insert(1, temp)
        if int(self.points[2][0]) > int(self.points[3][0]):
            temp = self.points.pop(2)
            self.points.insert(3, temp)

        # Transform
        pts1 = np.float32(self.points)
        pts2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
        perspective_transform_result = cv2.getPerspectiveTransform(pts1, pts2)
        self.result = cv2.warpPerspective(self.framethread.frame,\
            perspective_transform_result, (self.width, self.height))

    def refresh_color(self):
        """Set color of the car."""
        cv2.namedWindow('Set Color (q to quit)')
        cv2.setMouseCallback('Set Color (q to quit)', self.on_mouse)
        show_flag = True

        while True:
            self.dst = self.framethread.frame
            self.refresh_points()
            if show_flag:
                cv2.imshow('Set Color (q to quit)', self.dst)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                show_flag = False
                break
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.destroyWindow("Set Color (q to quit)")
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)

    def on_mouse(self, event, x, y, flags, param):
        """Select color after clicking mouse."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.color = [int(self.dst[y, x][0]), int(self.dst[y, x][1]), int(self.dst[y, x][2])]
            print(self.color)


    def refresh_points(self):
        """Find four points."""
        # convert RGB to HSV
        hsv = cv2.cvtColor(self.framethread.frame, cv2.COLOR_BGR2HSV)
        color = np.uint8([[self.color]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

        hue = hsv_color[0][0][0]

        # sensitivity
        low = hue-10 if hue-10 > -1 else 0
        high = hue+10 if hue+10 < 256 else 255
        # set bound
        lower_range = np.array([low, 100, 100], dtype=np.uint8)
        upper_range = np.array([high, 255, 255], dtype=np.uint8)
        # make a mask
        mask = cv2.inRange(hsv, lower_range, upper_range)
        kernel = np.ones((5, 5), np.uint8)

        # closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,kernel)
        erosion = cv2.erode(mask, kernel, iterations=1)
        dilation = cv2.dilate(erosion, kernel, iterations=3)
        blurred = cv2.GaussianBlur(dilation, (5, 5), 0)

        # Find contours in the thresholded image.
        cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        # Loop over the contours.
        centres = []

        for i in range(len(cnts)):
            moments = cv2.moments(cnts[i])
            centres.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
        for x in range(0, len(centres)):
            cv2.circle(self.dst, centres[x], 5, (0, 0, 150), -1)
        print(centres)
        # If numbers of contours aren't 4, then record the last points.
        if len(centres) == 4:
            self.lastpoint = centres
        else:
            centres = self.lastpoint

        self.points = centres
        