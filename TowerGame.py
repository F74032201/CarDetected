from pygame.locals import *
import pygame
import time
from random import randint
from tkinter import messagebox
from tkinter import *
from tkinter.scrolledtext import *
import os
from mapp import *

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
	picwidth = 32

	def __init__(self,x,y,block_size):
		self.block_size = block_size
		self.x = x * self.block_size + self.block_size/4
		self.y = y * self.block_size + self.block_size/4
		self.image = pygame.image.load('img/tower.png').convert()
		self.image = pygame.transform.scale(self.image,(self.picwidth,self.picwidth))
		self.image.set_colorkey( (0,0,0), RLEACCEL )
		self.done = False
		self.id = 0
		self.Color = None
	def draw(self, surface):
		surface.blit(self.image,(self.x , self.y))

class Wall:
	x = 0
	y = 0
	def __init__(self,x,y):
		self.x = x
		self.y = y
	def draw_v(self, surface):
		# pygame.draw.circle(surface, [0, 0, 255], (self.x, self.y), 5, 0)
		pygame.draw.rect(surface, [255, 0, 0], (self.x-2.5, self.y-32, 5, 64))
	def draw_h(self, surface):
		# pygame.draw.circle(surface, [0, 0, 255], (self.x, self.y), 5, 0)
		pygame.draw.rect(surface, [255, 0, 0], (self.x-32, self.y-2.5, 64, 5))


class App:	
	tower = {}
	wall_v = []
	wall_h = []
	def __init__(self,Con):
		self.Con = Con
		self._running = True
		self._all_done = False
		self._display_surf = None
		self._image_surf = None
		self._text_surf = None
		self.block_size = Con.block_size
		self.GameHeigh = Con.border_H * Con.block_size
		self.GameWidth = Con.border_W * Con.block_size
		self.textsurfHeight = 30
		self.windowHeigh = self.GameHeigh + self.textsurfHeight
		self.windowWidth = self.GameWidth
		self.game = Game()
		self.on_init()
		

	def on_init(self):
		pygame.init()
		self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeigh), pygame.HWSURFACE)
		pygame.display.set_caption('Tower War (esc to quit)')

		pygame.font.init() # you have to call this at the start, if you want to use this module.
		self.scorefont = pygame.font.SysFont('Comic Sans MS', 30)

		self.bg_image = pygame.image.load('img/map.jpg').convert()
		self.bg_image = pygame.transform.scale(self.bg_image,(self.GameWidth,self.GameHeigh))
		self.start_ticks = pygame.time.get_ticks()
		self.game_time_sec = int((pygame.time.get_ticks() - self.start_ticks)/1000) # milliseconds to seconds
		self.game_time_sec10 = int(self.game_time_sec/10)
		self.game_time_sec = int(self.game_time_sec%10)
		self.game_time_min = int(self.game_time_sec10/6)
		self.game_time_sec10 = int(self.game_time_sec10%6)
		self._text_surf = self.scorefont.render("Time : "+str(self.game_time_min)+": "+str(self.game_time_sec10)\
		+str(self.game_time_sec), False, (0, 0, 0))
		# self._running = True
		# self.add_player([0,0,255], "A") #0
		# # self.add_player([255,0,0], "B") #1
		# self.player[1].x = self.player[1].map_width-self.player[1].picwidth
		# self.player[1].y = self.player[1].map_height-self.player[1].picwidth
		
		# self._text_surf = self.scorefont.render("Score : Team_A : "+str(self.teamA_point)+"    Team_B : "+str(self.teamB_point), False, (255, 255, 255))
		self.Tower_init()
		self.init_wall()

	def init_wall(self):
		global wall_v, wall_h, block
		for i in range(0, len(wall_v)):
			self.wall_v.append(Wall(wall_v[i][0]*64, wall_v[i][1]*64+32))
		for i in range(0, len(wall_h)):
			self.wall_h.append(Wall(wall_h[i][0]*64+32, wall_h[i][1]*64))

	def Tower_init(self):
		for i in list(self.Con.player):	
			if type(self.Con.player[i]) != type('a'):
				#print(self.Con.player[i].carDst[0], self.Con.player[i].carDst[1])
				self.tower[i] = Tower(self.Con.player[i].carDst[0], self.Con.player[i].carDst[1],self.block_size)
				self.tower[i].id = self.Con.player[i].id
				self.tower[i].Color = self.Con.player[i].Color
				ChangeColor(self.tower[i].image,self.Con.player[i].Color)

	def on_event(self, event):
		if event.type == QUIT:
			self._running = False

	def on_loop(self):
		

		#does car catch tower	
		# for i in range(0,len(self.Con.player)):
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a') and (i in self.tower):
				if self.Con.player[i].image == None:
					self.Con.player[i].game_init()
					self.Con.player[i].direction = -1
				self.Con.player[i].update()	
				for j in list(self.tower):
					if self.game.isCollision(self.tower[j].x,self.tower[j].y,self.Con.player[i].x,self.Con.player[i].y,30):
						# Arrived at the correct destination.
						if self.tower[j].id == self.Con.player[i].id and (not self.tower[j].done):
							self.tower[j].done = True
							self.Con.player[i].done = True
							#send done message to car
							self.Con.ser_send_data(i,"Done")
							#record every player finished time
							self.Con.player[i].game_time_min = self.game_time_min
							self.Con.player[i].game_time_sec10 = self.game_time_sec10
							self.Con.player[i].game_time_sec = self.game_time_sec
							print("%s has Done at %d分 %d%d秒" %(self.Con.player[i].name,\
								self.Con.player[i].game_time_min,\
								self.Con.player[i].game_time_sec10,\
								self.Con.player[i].game_time_sec))
							# Print result onto textbox.
							self.Con.chatbox.insert(INSERT, "%s has Done at %d分 %d%d秒\n" %(self.Con.player[i].name,\
								self.Con.player[i].game_time_min,\
								self.Con.player[i].game_time_sec10,\
								self.Con.player[i].game_time_sec))
							self.Con.chatbox.see(END) 

							#check whether all the cars have done
							self._all_done = True
							for idx in list(self.Con.player):
								if type(self.Con.player[idx]) != type('a') and (idx in self.tower):
									if not self.Con.player[idx].done:
										self._all_done = False
							if self._all_done:
								self._running = False

						# Arrived at the wrong destination. 
						else:
							if not self.Con.player[i].dst_sent:
								self.Con.ser_send_data(i,"False:"+self.Con.player[i].name)
								self.Con.player[i].dst_sent = True

		self.game_time_sec = int((pygame.time.get_ticks() - self.start_ticks)/1000) # milliseconds to seconds
		self.game_time_sec10 = int(self.game_time_sec/10)
		self.game_time_sec = int(self.game_time_sec%10)
		self.game_time_min = int(self.game_time_sec10/6)
		self.game_time_sec10 = int(self.game_time_sec10%6)
		self._text_surf = self.scorefont.render("Time : "+str(self.game_time_min)+": "+str(self.game_time_sec10)\
		+str(self.game_time_sec), False, (0,0,0))
		pass

	def on_render(self):
		self._display_surf.fill((255,255,255))
		# self._display_surf.blit(self.bg_image,(0, 0))
		for i in range(0,len(self.wall_v)):
			self.wall_v[i].draw_v(self._display_surf)
		for i in range(0,len(self.wall_h)):
			self.wall_h[i].draw_h(self._display_surf)
		# for i in list(self.tower):
		# 	self.tower[i].draw(self._display_surf)
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a') and (i in self.tower):
				if self.Con.player[i].Color != self.tower[i].Color:
					self.tower[i].Color = self.Con.player[i].Color
					ChangeColor(self.tower[i].image,self.Con.player[i].Color)
				self.Con.player[i].draw(self._display_surf)
				self.tower[i].draw(self._display_surf)
		self._display_surf.blit(self._text_surf,(0,self.GameHeigh))
		pygame.display.flip()
		
	def on_cleanup(self):
		pygame.quit()
		print("pygame.quit()")
		if self._all_done:
			#print all player finished time to the screen
			print_mes = ""
			for i in list(self.Con.player):
				if type(self.Con.player[i]) != type('a') and (i in self.tower):
					print_mes = print_mes + ("%s 行走時間： %d分 %d%d秒\n" \
						%(self.Con.player[i].name,\
						self.Con.player[i].game_time_min,\
						self.Con.player[i].game_time_sec10,\
						self.Con.player[i].game_time_sec))
					#initialize everyone 
					
			print_mes = print_mes + ("共花時間: %d分 %d%d秒" \
				%(self.game_time_min,self.game_time_sec10,self.game_time_sec))
			messagebox.showinfo("All done!",print_mes)

		self.tower.clear()
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a') and (i in self.tower):
				self.Con.player[i].done = False
				# del self.tower[i]
		

	def on_execute(self):
		# if self.on_init() == False:
		# self._running = False

		while(self._running):
			pygame.event.pump()
			keys = pygame.key.get_pressed()

			
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
