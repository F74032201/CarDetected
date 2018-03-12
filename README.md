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

### Before you Start the server , please set the map first
![Imgur](https://i.imgur.com/4UQTU5P.png)


### Set the color of car
After the car has successfully connected to the server, tk window will show a new controller block, press the button "Set color" in it.

![](https://i.imgur.com/M07bdGm.png)

The window "Set color" will show, all you need to do is  to click the color block on the top of car.

![](https://i.imgur.com/Th5MKOE.png)

The color in controller block will update.


### Start

After all, click the button "Start", server will print the position of car beside the button.

## GameStart

### When click "GameStart"

Will call function "GameRestart(Con,chatbox)" to create a new gamethread, and make the game start.

```python=
class GameThread(Thread):
	def __init__(self, Con):
		super(GameThread, self).__init__()
		self.Con = Con
		self.App = App(self.Con)
		
	def run(self):
		for idx in list(self.Con.player):
			if type(self.Con.player[idx]) != type('a'):
				self.Con.player[idx].game_init()
				ChangeColor(self.Con.player[idx].image,self.Con.player[idx].Color)
		self.App.on_execute()

```
self.App.on_execute() is define in TowerGame.py
```python=
	def on_execute(self):
		while(self._running):
			pygame.event.pump()
			keys = pygame.key.get_pressed()

			self.on_loop()
			self.on_render()
			
			time.sleep(100.0 / 1000.0)
			if (keys[pygame.K_ESCAPE]):
				print("esc")
				self._running = False
		self.on_cleanup()
		return
```
As it called, game will start by doing a loop again and again, each of it will do two thing.
self.on_loop() do every judgment, such as blood controlling and time updating and most important, decision of win or lose.
self.on_render() is a painter of the game, will draw the picture according to the game infomation.
At the end of game, will execute self.on_cleanup() to delete the object that is useless in next rount.






