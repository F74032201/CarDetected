from pygame.locals import *
import pygame
import time
from random import randint
import os

from walltest import *

block = []
vertexlist=[]
map_width = 576
map_height = 576
block_size = 64
w = int(map_width/block_size)
h = int(map_height/block_size)
class Vertex:
	vid = [0,0]
	adj = []
	src = None
	def __init__(self, vid):
		self.vid = vid
		self.adj = []
		self.src = None


_sound_library = {}
def play_sound(path):
  global _sound_library
  sound = _sound_library.get(path)
  if sound == None:
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = pygame.mixer.Sound(canonicalized_path)
    _sound_library[path] = sound
  sound.play()
# def Adjacency():
# 	global w, h, wall_v, wall_h, vertexlist, block

	

# 	for i in range(0, w):
# 		for j in range(0, h):
# 			v = Vertex([i,j])
# 			if i!=0:
# 				if not ([j,i] in wall_v):
# 					v.adj.append([i-1,j])
# 			if i!=(w-1):
# 				if not ([j,i+1] in wall_v):
# 					v.adj.append([i+1,j])
# 			if j!=0:
# 				if not ([j,i] in wall_h):
# 					v.adj.append([i,j-1])
# 			if j!=(h-1):
# 				if not ([j+1,i] in wall_h):
# 					v.adj.append([i,j+1])
# 			vertexlist.append(v)
# 			if len(v.adj) == 0: #check if block
# 				block.append(v.vid)

# 			print(v.vid)
# 			print(v.adj)
# 	# for v in vertexlist:
def Adjacency():
	global w, h, wall_v, wall_h, vertexlist, block

	# vertexlist = [Vertex()]

	for i in range(0, w):
		for j in range(0, h):
			v = Vertex([i,j])
			vertexlist.append(v)

	for i in range(0, w):
		for j in range(0, h):

			if i!=0:
				if not ([i,j] in wall_v):
					vertexlist[i*w+j].adj.append(vertexlist[(i-1)*w+j])
			if i!=(w-1):
				if not ([i+1,j] in wall_v):
					vertexlist[i*w+j].adj.append(vertexlist[(i+1)*w+j])
			if j!=0:
				if not ([i,j] in wall_h):
					vertexlist[i*w+j].adj.append(vertexlist[i*w+(j-1)])
			if j!=(h-1):
				if not ([i,j+1] in wall_h):
					vertexlist[i*w+j].adj.append(vertexlist[i*w+(j+1)])

	for v in vertexlist:
		if len(v.adj) == 0: #check if block
			block.append(v.vid)

		# print(v.vid)
		# for a in v.adj:
		# 	print(a.vid, end=" ")
		# print()

		
def ChooseDir(ghost,pacman):
	global vertexlist, block, w, h

	if ghost == pacman:
		return -1
	g_x = ghost[0]
	g_y = ghost[1]
	p_x = pacman[0]
	p_y = pacman[1]
	p = vertexlist[p_x*w+p_y]
	V = list(vertexlist)
	visted = [False]*(w*h)
	Q =[]
	Q.append(V[g_x*w+g_y])
	# print(V[g_x*w+g_y].vid,end=",")
	visted[g_x*w+g_y] = True
	for i in block:
		visted[i[0]*w+i[1]] = True
	for i in vertexlist:
		i.src = None

	while visted.count(False):
		t = Q.pop(0)
		for i in t.adj:

			if not visted[i.vid[0]*w+i.vid[1]]:
				Q.append(i)
				visted[i.vid[0]*w+i.vid[1]] = True
				i.src = t
				# print(i.vid,end=",")

	temp = V[pacman[0]*w+pacman[1]]
	
	# print("path:")
	while (temp.src).src != None and temp.src != None:
		temp = temp.src	
		# print(temp.vid,temp.src.vid)
	if temp.vid[0] == g_x:
		if temp.vid[1] > g_y:
			return 3
		else :
			return 2
	elif temp.vid[0] < g_x:
		return 1
	else:
		return 0
def ChooseDir2(ghost,pacman):
	global vertexlist, block, w, h

	if ghost == pacman:
		return -1
	g_x = ghost[0]
	g_y = ghost[1]
	p_x = pacman[0]
	p_y = pacman[1]
	p = vertexlist[p_x*w+p_y]
	V = list(vertexlist)
	visted = [False]*(w*h)
	Q =[]
	Q.append(V[g_x*w+g_y])
	# print(V[g_x*w+g_y].vid,end=",")
	visted[g_x*w+g_y] = True
	for i in block:
		visted[i[0]*w+i[1]] = True
	for i in vertexlist:
		i.src = None

	while visted.count(False):
		t = Q.pop(0)
		# print(len(t.adj),"yo")
		for i in range(0,len(t.adj)):

			j = len(t.adj)-1 - i
			# print(j)
			if not visted[t.adj[j].vid[0]*w+t.adj[j].vid[1]]:
				Q.append(t.adj[j])
				visted[t.adj[j].vid[0]*w+t.adj[j].vid[1]] = True
				t.adj[j].src = t
				# print(i.vid,end=",")

	temp = V[pacman[0]*w+pacman[1]]
	
	# print("path:")
	while (temp.src).src != None and temp.src != None:
		temp = temp.src	
		# print(temp.vid,temp.src.vid)
	if temp.vid[0] == g_x:
		if temp.vid[1] > g_y:
			return 3
		else :
			return 2
	elif temp.vid[0] < g_x:
		return 1
	else:
		return 0
def ChooseDir_PowerMode(ghost,pacman):
	global vertexlist, block, w, h

	g_x = ghost[0]
	g_y = ghost[1]
	p_x = pacman[0]
	p_y = pacman[1]
	p = vertexlist[p_x*w+p_y]
	V = list(vertexlist)
	visted = [False]*(w*h)
	Q =[]
	Q.append(V[p_x*w+p_y])
	# print(V[g_x*w+g_y].vid,end=",")
	visted[p_x*w+p_y] = True
	for i in block:
		visted[i[0]*w+i[1]] = True
	for i in vertexlist:
		i.src = None

	while visted.count(False):
		t = Q.pop(0)
		for i in t.adj:
			if not visted[i.vid[0]*w+i.vid[1]]:
				Q.append(i)
				visted[i.vid[0]*w+i.vid[1]] = True
				i.src = t
				# print(i.vid,end=",")

	# t is the far place of pacman
	f_x = t.vid[0]
	f_y = t.vid[1]

	if g_x == f_x and g_y == f_y:
		for v in vertexlist:
			if [g_x, g_y] == v.vid:
				i = randint(0,len(v.adj)-1)
				print(i)
				if v.adj[i].vid[0] == g_x:
					if v.adj[i].vid[1] > g_y:
						return 3
					else :
						return 2
				elif v.adj[i].vid[0] < g_x:
					return 1
				else:
					return 0

	V = list(vertexlist)
	visted = [False]*(w*h)
	Q =[]
	Q.append(V[g_x*w+g_y])
	# print(V[g_x*w+g_y].vid,end=",")
	visted[g_x*w+g_y] = True
	for i in block:
		visted[i[0]*w+i[1]] = True
	for i in vertexlist:
		i.src = None

	while visted.count(False):
		t = Q.pop(0)
		for i in t.adj:
			if not visted[i.vid[0]*w+i.vid[1]]:
				Q.append(i)
				visted[i.vid[0]*w+i.vid[1]] = True
				i.src = t

	temp = V[f_x*w+f_y]
	# print("path:")
	while (temp.src).src != None and temp.src != None:
		temp = temp.src	
		# print(temp.vid,temp.src.vid)
	if temp.vid[0] == g_x:
		if temp.vid[1] > g_y:
			return 3
		else :
			return 2
	elif temp.vid[0] < g_x:
		return 1
	else:
		return 0

def ChangeColor(image,color):
	w, h = image.get_size()
	r, g, b = color
	o_r, o_g, o_b, _ = image.get_at((5, 5))
	for x in range(w):
		for y in range(h):
			if image.get_at((x, y))[0] != o_r or image.get_at((x, y))[1] != o_g or image.get_at((x, y))[2] != o_b:
				a = image.get_at((x, y))[3]
				image.set_at((x, y), pygame.Color(r, g, b, a))
			else:
				image.set_at((x, y), pygame.Color(0, 0, 0, 0))
	image.set_colorkey( (0,0,0), RLEACCEL )


def eraseBG(image):
	w, h = image.get_size()
	for x in range(w):
		for y in range(h):
			if image.get_at((x, y))[0] == 0 and image.get_at((x, y))[1] == 0 and image.get_at((x, y))[2] == 0:
				image.set_at((x, y), pygame.Color(0, 0, 0, 0))
	image.set_colorkey( (0,0,0), RLEACCEL )
# class Player:
# 	x = 256+32
# 	y = 384+32
# 	last_x = 256+32
# 	last_y = 384+32
# 	step = 0
# 	direction = 0
# 	map_width = 576
# 	map_height = 576
# 	picwidth =32

# 	color = [0,0,0]
# 	team = None
# 	block_size = 64
# 	# map_x = int(x/block_size)
# 	# map_y = int(y/block_size)player
	
# 	def __init__(self):
# 		self.life = 10
# 		self.x = 0
# 		self.y = 0
# 		self.step = 8
# 		self.angle = 0
# 		self._image_0 = pygame.image.load("img/pacman.png").convert()
# 		self._image_0 = pygame.transform.scale(self._image_0,(self.picwidth,self.picwidth))
# 		self._image_1 = pygame.image.load("img/pacman_1.png").convert()
# 		self._image_1 = pygame.transform.scale(self._image_1,(self.picwidth,self.picwidth))
# 		self._image_2 = pygame.image.load("img/pacman_2.png").convert()
# 		self._image_2 = pygame.transform.scale(self._image_2,(self.picwidth,self.picwidth))
# 		self._image_3 = pygame.image.load("img/pacman_3.png").convert()
# 		self._image_3 = pygame.transform.scale(self._image_3,(self.picwidth,self.picwidth))
		
# 		self.image = self._image_0

# 		self.image_count=0
# 		#initial position , no collision
		
# 	def update(self):
# 		#update position of player
# 		self.angle = 0

# 		if self.direction == 0:
# 			self.x += self.step
# 			self.angle = 0

# 		if self.direction == 1:
# 			self.x -= self.step
# 			self.angle = 180

# 		if self.direction == 2:
# 			self.y -= self.step
# 			self.angle = 90

# 		if self.direction == 3:
# 			self.y += self.step
# 			self.angle = 270
	
# 		# if self.x > self.map_width-self.picwidth:
# 		# 	self.x = self.map_width-self.picwidth
# 		# if self.x < 0:
# 		# 	self.x = 0
# 		# if self.y > self.map_height-self.picwidth:
# 		# 	self.y = self.map_height-self.picwidth
# 		# if self.y < 0:
# 		# 	self.y = 0

# 		if self.image_count == 0:
# 			self.image = pygame.transform.rotate(self._image_0, self.angle)
# 		if self.image_count == 1:
# 			self.image = pygame.transform.rotate(self._image_1, self.angle)
# 		if self.image_count == 2:
# 			self.image = pygame.transform.rotate(self._image_2, self.angle)
# 		if self.image_count == 3:
# 			self.image = pygame.transform.rotate(self._image_3, self.angle)

	# def show_x(self):
	# 	return self.x - self.picwidth/2
	# def show_y(self):
	# 	return self.y - self.picwidth/2
	# def map_x(self):
	# 	r = int(self.x/self.block_size)
	# 	return r
	# def map_y(self):
	# 	r = int(self.y/self.block_size)
	# 	return r

	# def moveRight(self):
	# 	self.direction = 0
	
	# def moveLeft(self):
	# 	self.direction = 1
	
	# def moveUp(self):
	# 	self.direction = 2

	# def moveDown(self):
	# 	self.direction = 3
	
	# def draw(self, surface):
	# 	surface.blit(self.image,(self.x-self.picwidth/2,self.y-self.picwidth/2))

class Dot:
	def __init__(self,x,y):
		self.x = x
		self.y = y
	def draw(self, surface):
		pygame.draw.circle(surface, [200, 200, 25], (self.x, self.y), 5, 0)

class Pellet:
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.draw_count = 0 
	def draw(self, surface):
		if self.draw_count < 4:
			pygame.draw.circle(surface, [200, 200, 25], (self.x, self.y), 10, 0)
		self.draw_count = (self.draw_count + 1) % 8

class Wall:
	x = 0
	y = 0
	def __init__(self,x,y):
		self.x = x
		self.y = y
	def draw_v(self, surface):
		# pygame.draw.circle(surface, [0, 0, 255], (self.x, self.y), 5, 0)
		pygame.draw.rect(surface, [0, 0, 255], (self.x-2.5, self.y-32, 5, 64))
	def draw_h(self, surface):
		# pygame.draw.circle(surface, [0, 0, 255], (self.x, self.y), 5, 0)
		pygame.draw.rect(surface, [0, 0, 255], (self.x-32, self.y-2.5, 64, 5))

class Ghost:
	x = 320-32
	y = 320-32
	last_x = 320-32
	last_y = 320-32
	step = 4
	direction = 0
	move_c = 0
	pause_c = 0
	map_width = 576
	map_height = 576
	picwidth =32


	color = [255,0,0]
	block_size = 64
	# map_x = int((x+picwidth/2)/block_size)
	# map_y = int((y+picwidth/2)/block_size)

	def __init__(self):
		self._image = pygame.image.load("img/Blinky.png").convert()
		self._image = pygame.transform.scale(self._image,(self.picwidth,self.picwidth))
		eraseBG(self._image)
		self.image = self._image
		self.power_mode = False
		

	def on_init(self):
		self.x = 320-32
		self.y = 320-32
		self.last_x = 320-32
		self.last_y = 320-32
		self.direction = 0
		self.move_c = 0
		self.pause_c = 16	
		self.__init__()

	def update(self):

		if self.pause_c !=0:
			self.pause_c -= 1
			
		else:
			if self.direction == 0:
				self.x += self.step

			if self.direction == 1:
				self.x -= self.step

			if self.direction == 2:
				self.y -= self.step
				# self.y = self.y
			if self.direction == 3:
				self.y += self.step
		
			if self.x > self.map_width-self.picwidth:
				self.x = self.map_width-self.picwidth
			if self.x < 0:
				self.x = 0
			if self.y > self.map_height-self.picwidth:
				self.y = self.map_height-self.picwidth
			if self.y < 0:
				self.y = 0

	def show_x(self):
		return self.x - self.picwidth/2
	def show_y(self):
		return self.y - self.picwidth/2
	def map_x(self):
		r = int(self.x/self.block_size)
		return r
	def map_y(self):
		r = int(self.y/self.block_size)
		return r
	def draw(self, surface):
		surface.blit(self.image,(self.x-self.picwidth/2,self.y-self.picwidth/2))


class Game:
	picwidth = 32
	def isCollision_ghost(self,x1,y1,x2,y2,bsize):
		
		if x1 >= x2 and x1 <= x2+bsize:
			if y1 >= y2 and y1 <= y2+bsize:
				return True
		# if x1+self.picwidth >= x2 and x1+self.picwidth <= x2+bsize:
		# 	if y1 >= y2 and y1 <= y2+bsize:
		# 		return True
		# if x1 >= x2 and x1 <= x2+bsize:
		# 	if y1+self.picwidth >= y2 and y1+self.picwidth <= y2+bsize:
		# 		return True
		# if x1+self.picwidth >= x2 and x1+self.picwidth <= x2+bsize:
		# 	if y1+self.picwidth >= y2 and y1+self.picwidth <= y2+bsize:
		# 		return True

		return False

	def isCollision_dot(self,x1,y1,x2,y2,bsize):
		
		if x1 >= x2 and x1 <= x2+bsize:
			if y1 >= y2 and y1 <= y2+bsize:
				return True
		return False

	def isCollision_wall_v(self,x1,y1,x2,y2,bsize):
		if x1 >= x2 and x1 <= x2+bsize:
			if y1 >= y2 and y1 <= y2+bsize:
				return True
		if x1 >= x2 and x1 <= x2+bsize:
			if y1+self.picwidth >= y2 and y1+self.picwidth <= y2+bsize:
				return True
		if x1 >= x2 and x1 <= x2+bsize:
			if y1-self.picwidth >= y2 and y1-self.picwidth <= y2+bsize:
				return True
		return False

	def isCollision_wall_h(self,x1,y1,x2,y2,bsize):
		if x1 >= x2 and x1 <= x2+bsize:
			if y1 >= y2 and y1 <= y2+bsize:
				return True
		if x1+self.picwidth >= x2 and x1+self.picwidth <= x2+bsize:
			if y1 >= y2 and y1 <= y2+bsize:
				return True
		if x1-self.picwidth >= x2 and x1-self.picwidth <= x2+bsize:
			if y1 >= y2 and y1 <= y2+bsize:
				return True
		return False


class App:

	GameWidth = 576
	GameHeight = 576
	textsurfHeight = 30
	windowHeigh = GameHeight + textsurfHeight
	windowWidth =576
	player = []
	ghost = []
	dot = []
	pellet = []
	wall_v = []
	wall_h = []
	player_num = 0
	ghost_num = 0
	point = 0
	teamB_point = 0

	def __init__(self,Con):
		self._running = True
		self._display_surf = None
		self._image_surf = None
		self._text_surf = None
		self._msg_box_surf = None
		self.Con = Con
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a'):
				self.sock = i
		self.game = Game()
		

	def on_init(self):
		# pygame.mixer.pre_init(44100, -16, 1, 512)
		# pygame.init()
		# self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeigh), pygame.HWSURFACE)
		# pygame.display.set_caption('Pacman')

		pygame.font.init() # you have to call this at the start, if you want to use this module.
		pygame.mixer.music.load('music/pacman_siren.wav')

		self.effect_beginning = pygame.mixer.Sound('music/pacman_beginning.wav')
		# self.effect_siren = pygame.mixer.Sound('music/pacman_siren.wav')
		self.effect_chomp = pygame.mixer.Sound('music/pacman_chomp.wav')
		self.effect_eatpill = pygame.mixer.Sound('music/pacman_eatpill.wav')
		self.effect_death = pygame.mixer.Sound('music/pacman_death.wav')
		self.effect_eatghost = pygame.mixer.Sound('music/pacman_eatghost.wav')
		self.effect_waza = pygame.mixer.Sound('music/pacman_waza.wav')
		
		self.scorefont = pygame.font.SysFont('Comic Sans MS', 15)

		Adjacency()
		self.init_wall()
		self.init_dot()
		self.init_pellet()
		del_c = 0
		for i in range(0, len(self.dot)):
			for j in range(0, len(self.wall_v)):
				if self.game.isCollision_wall_v(self.wall_v[j].x, self.wall_v[j].y, self.dot[i-del_c].x, self.dot[i-del_c].y, 1):
					del self.dot[i-del_c]
					del_c += 1
					break
			for j in range(0, len(self.wall_h)):
				if self.game.isCollision_wall_h(self.wall_h[j].x, self.wall_h[j].y, self.dot[i-del_c].x, self.dot[i-del_c].y, 1):
					del self.dot[i-del_c]
					del_c += 1
					break
		
		# self.add_player([255,255,0], "A") #0
		# self.add_player([255,0,0], "B") #1
		# self.player[1].x = self.player[1].map_width-self.player[1].picwidth
		# self.player[1].y = self.player[1].map_height-self.player[1].picwidth

		self.add_ghost([255,0,0], 320-32, 320-32)
		self.add_ghost([127,0,0], 256-32, 320-32)
		self.ghost[1].pause_c = 64
		self._running = True
		self.start_ticks = pygame.time.get_ticks()
		self.game_time_sec = int((pygame.time.get_ticks() - self.start_ticks)/1000) # milliseconds to seconds
		self.game_time_sec10 = int(self.game_time_sec/10)
		self.game_time_sec = int(self.game_time_sec%10)
		self.game_time_min = int(self.game_time_sec10/6)
		self.game_time_sec10 = int(self.game_time_sec10%6)
		self.life_image = pygame.image.load("img/pacman.png")
		self.life_image = pygame.transform.scale(self.life_image,(25, 25) )

		self.on_loop()
		self.on_render()
		self.effect_beginning.play()
		time.sleep(4500.0 / 1000.0)
		pygame.mixer.music.play(-1, 0.0)
	def init_dot(self):
		global wall_v, wall_h, block
		for i in range(0, int(self.GameWidth/32)):
			for j in range(0, int(self.GameHeight/32)):
				if not([i/2,j/2] in block or [i, j] in [[6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [8, 7], [0, 0], [0, 16], [16, 0], [16, 16], [8, 12]]):
					self.dot.append(Dot((i+1)*32,(j+1)*32))

	def init_pellet(self):
		self.pellet.append(Pellet(0+32,0+32))
		self.pellet.append(Pellet(0+32,512+32))
		self.pellet.append(Pellet(512+32,0+32))
		self.pellet.append(Pellet(512+32,512+32))



	def init_wall(self):
		global wall_v, wall_h, block
		for i in range(0, len(wall_v)):
			self.wall_v.append(Wall(wall_v[i][0]*64, wall_v[i][1]*64+32))
		for i in range(0, len(wall_h)):
			self.wall_h.append(Wall(wall_h[i][0]*64+32, wall_h[i][1]*64))
		


	def add_player(self,color,team):
		self.player.append(Player()) 
		self.player[self.player_num].team = team
		self.player[self.player_num].color = color
		ChangeColor(self.player[self.player_num]._image_0,self.player[self.player_num].color)
		ChangeColor(self.player[self.player_num]._image_1,self.player[self.player_num].color)
		ChangeColor(self.player[self.player_num]._image_2,self.player[self.player_num].color)
		ChangeColor(self.player[self.player_num]._image_3,self.player[self.player_num].color)
		self.player_num += 1

	def add_ghost(self,color,x,y):
		self.ghost.append(Ghost()) 
		self.ghost[self.ghost_num].x = x
		self.ghost[self.ghost_num].y = y
		self.ghost[self.ghost_num].color = color
		# ChangeColor(self.ghost[self.ghost_num]._image,self.ghost[self.ghost_num].color)
		self.ghost_num += 1

	def show_msg_box(self, color, msg):
		pygame.draw.rect(self._display_surf, color, (self.GameWidth/2-100, self.GameHeight/2-50, 200, 100))
		self._msg_box_surf = self.scorefont.render(msg, False, [0,0,0])
		self._display_surf.blit(self._msg_box_surf,(self.GameWidth/2-70,self.GameHeight/2-15))
		
		pygame.display.flip()

	def on_event(self, event):
		if event.type == QUIT:
			self._running = False

	def on_loop(self):

		if len(self.dot) == 0 and len(self.pellet) == 0:
			pygame.mixer.music.stop()
			self.show_msg_box([125,125,0],"Completed!(ESC to End)")
			pygame.mixer.music.load('music/pacman_beginning.wav')
			pygame.mixer.music.play(-1, 0.0)
			while self._running:
				# time.sleep(300.0 / 1000.0)
				pygame.event.pump()
				keys = pygame.key.get_pressed()
				if (keys[pygame.K_ESCAPE]):
					self._running = False

		if self.Con.player[self.sock].life == 0:
			pygame.mixer.music.stop()
			self.show_msg_box([125,255,125],"GameOver!(ESC to End)")
			pygame.mixer.music.load('music/pacman_beginning.wav')
			pygame.mixer.music.play(-1, 0.0)
			while self._running:
				# time.sleep(300.0 / 1000.0)
				pygame.event.pump()
				keys = pygame.key.get_pressed()
				if (keys[pygame.K_ESCAPE]):
					self._running = False
		# for i in range(0,len(self.player)):
		self.Con.player[self.sock].update()	

		# self.player[1].update()
		g_c = 0
		for g in self.ghost:
			if g.move_c == 0:
				if g.power_mode:
					g.direction = ChooseDir_PowerMode([g.map_x(),g.map_y()],[self.Con.player[self.sock].map_x(),self.Con.player[self.sock].map_y()])
				else:
					if g_c ==0:
						g.direction = ChooseDir([g.map_x(),g.map_y()],[self.Con.player[self.sock].map_x(),self.Con.player[self.sock].map_y()])
					else:
						g.direction = ChooseDir2([g.map_x(),g.map_y()],[self.Con.player[self.sock].map_x(),self.Con.player[self.sock].map_y()])
					
			g_c += 1
			g.move_c = (g.move_c + 1)%16
			g.update()

		self.Con.player[self.sock].image_count = (self.Con.player[self.sock].image_count + 1) % 4

		for i in range(0, len(self.wall_v)):
			if self.game.isCollision_wall_v(self.wall_v[i].x, self.wall_v[i].y, self.Con.player[self.sock].show_x(), self.Con.player[self.sock].show_y(), 32):
				self.Con.player[self.sock].x = self.Con.player[self.sock].last_x
				self.Con.player[self.sock].y = self.Con.player[self.sock].last_y
				self.Con.player[self.sock].image_count = 0
				break

		for i in range(0, len(self.wall_h)):
			if self.game.isCollision_wall_h(self.wall_h[i].x, self.wall_h[i].y, self.Con.player[self.sock].show_x(), self.Con.player[self.sock].show_y(), 32):
				self.Con.player[self.sock].y = self.Con.player[self.sock].last_y
				self.Con.player[self.sock].y = self.Con.player[self.sock].last_y
				self.Con.player[self.sock].image_count = 0
				break

		
		self.Con.player[self.sock].last_x = self.Con.player[self.sock].x
		self.Con.player[self.sock].last_y = self.Con.player[self.sock].y

		for g in self.ghost:
			g.last_x = g.x
			g.last_y = g.y

		for g in self.ghost:
			if self.game.isCollision_ghost(g.x, g.y, self.Con.player[self.sock].show_x(), self.Con.player[self.sock].show_y(), 32):
				if g.power_mode:
					self.effect_eatghost.play()
					time.sleep(300.0 / 1000.0)
					self.point = self.point + 400
					g.on_init()
				else:
					self.effect_death.play()
					time.sleep(300.0 / 1000.0)
					for i in self.ghost:
						i.on_init()
					self.ghost[1].x = 256-32
					self.ghost[1].y = 320-32
					self.ghost[1].pause_c = 64
					self.Con.player[self.sock].life -= 1
					print("gameover")
					break
		
		for j in range(0, len(self.dot)):
			if self.game.isCollision_dot(self.dot[j].x, self.dot[j].y, self.Con.player[self.sock].show_x(), self.Con.player[self.sock].show_y(), 32):
				del self.dot[j]	
				self.effect_chomp.play()
				self.point = self.point + 10
				break
		
		for j in range(0, len(self.pellet)):
			if self.game.isCollision_dot(self.pellet[j].x, self.pellet[j].y, self.Con.player[self.sock].show_x(), self.Con.player[self.sock].show_y(), 32):
				del self.pellet[j]
				self.effect_eatpill.play()
				pygame.mixer.music.stop()
				pygame.mixer.music.load('music/pacman_waza.wav')
				pygame.mixer.music.play(-1, 0.0)
				self.point = self.point + 100
				for g in self.ghost:
					g.power_mode =True
					ChangeColor(g._image, [255,255,255])
				self.power_mode_start_time = pygame.time.get_ticks()
				break		
		power_mode_off_c = 0
		for g in self.ghost:
			if g.power_mode == True:
				if (pygame.time.get_ticks() - self.power_mode_start_time)/1000 >= 10:
					power_mode_off_c += 1
					g.__init__()
					if power_mode_off_c == len(self.ghost):
						pygame.mixer.music.stop()
						pygame.mixer.music.load('music/pacman_siren.wav')
						pygame.mixer.music.play(-1, 0.0)
			else:
				power_mode_off_c += 1
		
		
		self.game_time_sec = int((pygame.time.get_ticks() - self.start_ticks)/1000) # milliseconds to seconds
		self.game_time_sec10 = int(self.game_time_sec/10)
		self.game_time_sec = int(self.game_time_sec%10)
		self.game_time_min = int(self.game_time_sec10/6)
		self.game_time_sec10 = int(self.game_time_sec10%6)
		self._text_surf = self.scorefont.render("Time : "+str(self.game_time_min)+": "+str(self.game_time_sec10)\
		+str(self.game_time_sec)+"    Score : "+str(self.point), False, (255, 255, 255))
		
		pass

	def on_render(self):
		self._display_surf.fill((0,0,0))
		# self._display_surf.blit(self.bg_image,(0, 0))
		for i in range(0,len(self.wall_v)):
			self.wall_v[i].draw_v(self._display_surf)
		for i in range(0,len(self.wall_h)):
			self.wall_h[i].draw_h(self._display_surf)
		for i in range(0, len(self.dot)):
			self.dot[i].draw(self._display_surf)
		for i in range(0, len(self.pellet)):
			self.pellet[i].draw(self._display_surf)
		# for i in range(0,len(self.Con.player[self.sock])):
		self.Con.player[self.sock].draw(self._display_surf)
		for i in range(0,len(self.ghost)):
			self.ghost[i].draw(self._display_surf)

		self._display_surf.blit(self._text_surf,(0,self.GameHeight))
		
		for i in range(0,self.Con.player[self.sock].life):
			self._display_surf.blit(self.life_image,(self.GameWidth/2 + i*27.5, self.GameHeight))

		
		pygame.display.flip()
		
	def on_cleanup(self):
		pygame.quit()

	def on_execute(self):
		if self.on_init() == False:
			self._running = False

		pause = False

		while(self._running):
			pygame.event.pump()
			keys = pygame.key.get_pressed()

			if (keys[pygame.K_RIGHT]) or (keys[pygame.K_KP6]):
				self.Con.player[self.sock].moveRight()
			
			if (keys[pygame.K_LEFT]) or (keys[pygame.K_KP4]):
				self.Con.player[self.sock].moveLeft()

			if (keys[pygame.K_UP]) or (keys[pygame.K_KP8]):
				self.Con.player[self.sock].moveUp()
	
			if (keys[pygame.K_DOWN]) or (keys[pygame.K_KP2]):
				self.Con.player[self.sock].moveDown()

			if (keys[pygame.K_g]):
				self.ghost[0].moveRight()
			
			if (keys[pygame.K_d]):
				self.ghost[0].moveLeft()

			if (keys[pygame.K_r]):
				self.ghost[0].moveUp()
	
			if (keys[pygame.K_f]):
				self.ghost[0].moveDown()

			if (keys[pygame.K_ESCAPE]):
				self._running = False

			if (keys[pygame.K_p]):
				pause = True
				print("Pause")
				pygame.mixer.music.pause()
				self.show_msg_box([125,255,125],"Pause (p to Resume)")
				time.sleep(250.0 / 1000.0)


			while pause:
				
				pygame.event.pump()
				keys = pygame.key.get_pressed()
				if (keys[pygame.K_p]):
					pause = False
					print("Resume")
					pygame.mixer.music.unpause()
					time.sleep(250.0 / 1000.0)
				if (keys[pygame.K_ESCAPE]):
					pause = False
					self._running = False
					time.sleep(250.0 / 1000.0)

			self.on_loop()
			self.on_render()
			
			time.sleep(100.0 / 1000.0)
		self.on_cleanup()

if __name__ == "__main__" :
	theApp = App()
	theApp.on_execute()
