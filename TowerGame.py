from pygame.locals import *
import pygame
import time
from random import randint

import os


def ChangeColor(image,color):
	w, h = image.get_size()
	b, g, r = color
	o_r, o_g, o_b, _ = image.get_at((16, 16))
	for x in range(w):
		for y in range(h):
			if image.get_at((x, y))[0] == o_r and image.get_at((x, y))[1] == o_g and image.get_at((x, y))[2] == o_b:
				a = image.get_at((x, y))[3]
				image.set_at((x, y), pygame.Color(r, g, b, a))
			else:
				image.set_at((x, y), pygame.Color(0, 0, 0, 0))
	image.set_colorkey( (0,0,0), RLEACCEL )
	   

class Game:
	picwidth = 32
	def isCollision(self,x1,y1,x2,y2,bsize):
		
		if x1 >= x2 and x1 <= x2+bsize:
			if y1 >= y2 and y1 <= y2+bsize:
				return True
		if x1+self.picwidth >= x2 and x1+self.picwidth <= x2+bsize:
			if y1 >= y2 and y1 <= y2+bsize:
				return True
		if x1 >= x2 and x1 <= x2+bsize:
			if y1+self.picwidth >= y2 and y1+self.picwidth <= y2+bsize:
				return True
		if x1+self.picwidth >= x2 and x1+self.picwidth <= x2+bsize:
			if y1+self.picwidth >= y2 and y1+self.picwidth <= y2+bsize:
				return True

		return False

class Tower:
	x = 0
	y = 0
	step = 64
	picwidth = 32

	def __init__(self,x,y):
		self.x = x * self.step + self.step/4
		self.y = y * self.step + self.step/4
		self.image = pygame.image.load('img/tower.png').convert()
		self.image = pygame.transform.scale(self.image,(self.picwidth,self.picwidth))
		self.image.set_colorkey( (0,0,0), RLEACCEL )
		self.done = False
		self.id = 0
	def draw(self, surface):
		surface.blit(self.image,(self.x , self.y))

class App:

	GameWidth = 512
	GameHeigh = 512
	textsurfHeight = 30
	windowHeigh = GameHeigh + textsurfHeight
	windowWidth =512
	tower = []
	teamA_point = 0
	teamB_point = 0

	def __init__(self,Con):
		self.Con = Con
		self._running = True
		self._display_surf = None
		self._image_surf = None
		self._text_surf = None
		self.game = Game()
		self.on_init()
		

	def on_init(self):
		pygame.init()
		self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeigh), pygame.HWSURFACE)
		pygame.display.set_caption('Tower War')

		pygame.font.init() # you have to call this at the start, if you want to use this module.
		self.scorefont = pygame.font.SysFont('Comic Sans MS', 30)

		self.bg_image = pygame.image.load('img/map.jpg').convert()
		self.bg_image = pygame.transform.scale(self.bg_image,(self.GameWidth,self.GameHeigh))
		# self._running = True
		# self.add_player([0,0,255], "A") #0
		# # self.add_player([255,0,0], "B") #1
		# self.player[1].x = self.player[1].map_width-self.player[1].picwidth
		# self.player[1].y = self.player[1].map_height-self.player[1].picwidth
		
		self._text_surf = self.scorefont.render("Score : Team_A : "+str(self.teamA_point)+"    Team_B : "+str(self.teamB_point), False, (255, 255, 255))
		self.Tower_init()

	def Tower_init(self):
		c = 0
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a'):
				print(self.Con.player[i].carDst[0], self.Con.player[i].carDst[1])
				self.tower.append(Tower(self.Con.player[i].carDst[0], self.Con.player[i].carDst[0]))
				self.tower[c].id = self.Con.player[i].id
				ChangeColor(self.tower[c].image,self.Con.player[i].Color)
				c = c + 1

	def on_event(self, event):
		if event.type == QUIT:
			self._running = False

	def on_loop(self):
		

		#does car catch tower	
		# for i in range(0,len(self.Con.player)):
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a'):
				self.Con.player[i].update()	
				for j in range(0,len(self.tower)):
					if self.game.isCollision(self.tower[j].x,self.tower[j].y,self.Con.player[i].x,self.Con.player[i].y,30):
						if self.toewr[i].id == self.Con.player[i].id:
							self.tower[i].done = True
							self.Con.player[i].done = True
							print("Done")

		pass

	def on_render(self):
		self._display_surf.fill((0,0,0))
		self._display_surf.blit(self.bg_image,(0, 0))
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a'):
				self.Con.player[i].draw(self._display_surf)
		for i in range(0,len(self.tower)):
			self.tower[i].draw(self._display_surf)
		self._display_surf.blit(self._text_surf,(0,self.GameHeigh))
		pygame.display.flip()
		
	def on_cleanup(self):
		pygame.quit()
		print("pygame.quit()")

	def on_execute(self):
		if self.on_init() == False:
			self._running = False

		while(self._running):
			pygame.event.pump()
			keys = pygame.key.get_pressed()

			if (keys[pygame.K_RIGHT]) or (keys[pygame.K_KP6]):
				self.Con.player[1].moveRight()
			
			if (keys[pygame.K_LEFT]) or (keys[pygame.K_KP4]):
				self.Con.player[1].moveLeft()

			if (keys[pygame.K_UP]) or (keys[pygame.K_KP8]):
				self.Con.player[1].moveUp()
	
			if (keys[pygame.K_DOWN]) or (keys[pygame.K_KP2]):
				self.Con.player[1].moveDown()

			if (keys[pygame.K_g]):
				self.Con.player[2].moveRight()
			
			if (keys[pygame.K_d]):
				self.Con.player[2].moveLeft()

			if (keys[pygame.K_r]):
				self.Con.player[2].moveUp()
	
			if (keys[pygame.K_f]):
				self.Con.player[2].moveDown()

			if (keys[pygame.K_ESCAPE]):
				print("esc")
				self._running = False

			self.on_loop()
			self.on_render()
			
			time.sleep(100.0 / 1000.0)
		self.on_cleanup()


# if __name__ == "__main__" :
# 	theApp = App()
# 	theApp.on_execute()
