# CarDetected

A system let robot embedded with an Arduino like single-board microcontrollers connected with wifi,and the interface shows the real-time position of the robot.
The computer will act a part of server.

## Installation

First clone to this github.

User requires [OpenCV](http://opencv.org/) with python3.

Please reference to this [tutorial](https://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/) for Ubuntu.

#### Enter the virtual environment
```sh
$ workon cv
```
#### Install other package
```sh
(cv) $ sudo apt install python3-tk
(cv) $ pip install -r requirements.txt
```

## Running the test
Plug in your web cam.
```sh
(cv) $ python MainWindow.py
```
![Imgur](https://i.imgur.com/f5a45dP.png)

If you click the button and it did not open with webcam ,please try to edit the file MainWindow.py of this line.

Change the number of the argument of VideoCapture to right camera number of usb.
```sh
...
cap = cv2.VideoCapture(1)
...
```

## Connect with your robot

Check out both computer and the robot connecting to the same wifi.

And check out the server ip with command ifconfig
```sh
$ ifconfig
```

Then change the ip to your robot's code.

### Before you Start the server , please set the map first.
![Imgur](https://i.imgur.com/4UQTU5P.png)
