from pygame.locals import *
import pygame
import time
from random import randint
from tkinter import messagebox
import os
import random

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
	def __init__(self,xy,block_size,pic):
		self.block_size = block_size
		self.x,self.y = xy
		self.x = self.x * self.block_size + self.block_size/4
		self.y = self.y * self.block_size + self.block_size/4
		self.image = pygame.image.load(pic).convert()
		self.image = pygame.transform.scale(self.image,(self.picwidth,self.picwidth))
		self.image.set_colorkey( (0,0,0), RLEACCEL )
		self.done = False
		self.id = 0

	def draw(self, surface):
		surface.blit(self.image,(self.x , self.y ))

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


class App:	
	tower = {}

	def __init__(self,Con):
		self.Con = Con
		self._running = True
		self._GG = None
		self._display_surf = None
		self._image_surf = None
		self._text_surf = None
		self.block_size = Con.block_size
		self.GameHeigh = Con.border_H * Con.block_size
		self.GameWidth = Con.border_W * Con.block_size
		self.textsurfHeight = 30
		self.windowHeigh = self.GameHeigh + self.textsurfHeight
		self.windowWidth = self.GameWidth
		self.open_base_time = -1
		self.count_down_final = False # use to record the base to open
		self.Base = {'A':(7,7),'B':(1,1)} # Set Base for A,B. 
		self.turret = {'A':[(6,1),(7,1),(7,2),(7,3),(6,4),(5,5),(4,6),(3,7)]\
					  ,'B':[(5,1),(4,2),(3,3),(2,4),(1,5),(1,6),(1,7),(2,7)]\
					  ,'C':[(2,5),(2,6),(3,4),(3,5),(3,6),(4,3),(4,4),(4,5)\
					  		,(4,6),(5,2),(5,3),(5,4),(6,2),(6,3)]} # Set turret position
		self.tower['A_Base'] = None
		self.tower['B_Base'] = None
		self.game = Game()
		self.on_init()
		

	def on_init(self):
		pygame.init()
		self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeigh), pygame.HWSURFACE)
		pygame.display.set_caption('Tower War (esc to quit)')

		pygame.font.init() # you have to call this at the start, if you want to use this module.
		self.scorefont = pygame.font.SysFont('Comic Sans MS', 30)

		self.bg_image = pygame.image.load('img/finalmap.png').convert()
		self.bg_image = pygame.transform.scale(self.bg_image,(self.GameWidth,self.GameHeigh))
		self.start_ticks = pygame.time.get_ticks()
		self.count_down = 180 # count down for 3 mins
		self.passed_sec = int((pygame.time.get_ticks() - self.start_ticks)/1000) # milliseconds to seconds
		self.game_time_sec = self.count_down - self.passed_sec # left sec
		self.game_time_sec10 = int(self.game_time_sec/10)
		self.game_time_sec = int(self.game_time_sec%10)
		self.game_time_min = int(self.game_time_sec10/6)
		self.game_time_sec10 = int(self.game_time_sec10%6)
		self._text_surf = self.scorefont.render("Remaining Time : "+str(self.game_time_min)+": "+str(self.game_time_sec10)\
		+str(self.game_time_sec), False, (255, 255, 255))
		
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a'):
				self.Con.player[i].blood = 180
				self.Con.player[i].score = 0
				self.Con.player[i].still_alive = True
		self.Con.towers_pos = [(-1,-1),(-1,-1),(-1,-1)]
		self.Con.base_situation = {'A':'C', 'B':'C'}

		# self._running = True
		# self.add_player([0,0,255], "A") #0
		# # self.add_player([255,0,0], "B") #1
		# self.player[1].x = self.player[1].map_width-self.player[1].picwidth
		# self.player[1].y = self.player[1].map_height-self.player[1].picwidth
		
		# self._text_surf = self.scorefont.render("Score : Team_A : "+str(self.teamA_point)+"    Team_B : "+str(self.teamB_point), False, (255, 255, 255))
		self.Tower_init()

		for i in list(self.Con.player):		
			if type(self.Con.player[i]) != type('a'):
				self.Con.player[i].stay_pos = self.Con.player[i].big_pos()
				self.Con.player[i].stay_time = self.passed_sec
		# self.init_wall()

	def Tower_init(self):
		self.tower['A'] = Tower(self.turret['A'][random.randint(0,5)],self.block_size,'img/tower.png')
		self.tower['B'] = Tower(self.turret['B'][random.randint(0,5)],self.block_size,'img/tower.png')
		self.tower['C'] = Tower(self.turret['C'][random.randint(0,6)],self.block_size,'img/tower.png')
		

	def on_event(self, event):
		if event.type == QUIT:
			self._running = False

	def on_loop(self):
		self.passed_sec = int((pygame.time.get_ticks() - self.start_ticks)/1000) # milliseconds to seconds
		self.game_time_sec = self.count_down - self.passed_sec # left sec
		self.game_time_sec10 = int(self.game_time_sec/10)
		self.game_time_sec = int(self.game_time_sec%10)
		self.game_time_min = int(self.game_time_sec10/6)
		self.game_time_sec10 = int(self.game_time_sec10%6)
		self._text_surf = self.scorefont.render("Remaining Time : "+str(self.game_time_min)+": "+str(self.game_time_sec10)\
		+str(self.game_time_sec), False, (255, 255, 255))
		# Setting sending text into connection object.
		if self.tower['A']:
			self.Con.towers_pos = [(int(self.tower['A'].x + self.block_size/4), int(self.tower['A'].y + self.block_size/4))\
				, (int(self.tower['B'].x + self.block_size/4), int(self.tower['B'].y + self.block_size/4))\
				, (int(self.tower['C'].x + self.block_size/4), int(self.tower['C'].y + self.block_size/4))]
		self.Con.base_situation['A'] = 'O' if not self.tower['B_Base'] else 'C'
		self.Con.base_situation['B'] = 'O' if not self.tower['A_Base'] else 'C'

		self.blood_control()	# Change blood in any situation.
		self.isGG()		# Check whether the game is over.
		self.is_open_base()	# Check whether the bases shoud be opened or not, if so then open it, or close it.
		

	def isGG(self):
		if self.count_down - self.passed_sec <= 0: # Time's up
			self._running = False
			if self.sum_of_teams('A') > self.sum_of_teams('B'):
				self._GG = 'A Won!'
			elif self.sum_of_teams('A') < self.sum_of_teams('B'):
				self._GG = 'B Won!'
			# If scores are the same
			elif self.blood_of_teams('A') > self.blood_of_teams('B'):
				self._GG = 'A Won!'
			elif self.blood_of_teams('A') < self.blood_of_teams('B'):
				self._GG = 'B Won!'
			else: # tied game
				self._GG = 'Tied game!'
			return 
		else:		# Still have time!
			# Check if everyone gains scores, or who won the game.
			for i in list(self.Con.player):
				if type(self.Con.player[i]) != type('a') and \
					self.Con.player[i].still_alive:
					if self.Con.player[i].image == None:
						self.Con.player[i].game_init()
						self.Con.player[i].direction = -1
					self.Con.player[i].update()	
					for j in list(self.tower):
						if self.tower[j]:
							if self.game.isCollision(self.tower[j].x,self.tower[j].y,self.Con.player[i].x,self.Con.player[i].y,32):
								# if self.tower[j].id == self.Con.player[i].id and (not self.tower[j].done):
								# if collision then get score and reset the turret
								if j == 'A_Base': # Got the base and team A won the game
									self._GG = 'A'
									self._running = False
									return
								elif j == 'B_Base': # Got the base and team B won the game
									self._GG = 'B'
									self._running = False
									return
								elif j == 'C': # step into neutral zone
									self.Con.player[i].score += 3
									self.tower[j] = Tower(self.turret['C'][random.randint(0,6)],self.block_size,'img/tower.png')
								elif j == 'A' and self.Con.player[i].team == 'A': # A step into A zone.
									self.Con.player[i].score += 5
									self.tower[j] = Tower(self.turret['A'][random.randint(0,5)],self.block_size,'img/tower.png')
								elif j == 'A' and self.Con.player[i].team == 'B': # B step int A zone.
									self.Con.player[i].score += 1
									self.Con.player[i].blood += 3
									self.tower[j] = Tower(self.turret['A'][random.randint(0,5)],self.block_size,'img/tower.png')
								elif j == 'B' and self.Con.player[i].team == 'B': # B step into B zone.
									self.Con.player[i].score += 5
									self.tower[j] = Tower(self.turret['B'][random.randint(0,5)],self.block_size,'img/tower.png')
								elif j == 'B' and self.Con.player[i].team == 'A': # A step int B zone.
									self.Con.player[i].score += 1
									self.Con.player[i].blood += 3
									self.tower[j] = Tower(self.turret['B'][random.randint(0,5)],self.block_size,'img/tower.png')
		# If game is not over, check who is out of blood.
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a') and \
				self.Con.player[i].blood <= 0 and self.Con.player[i].still_alive:
				self.Con.player[i].blood = 0
				self.Con.ser_send_data(i, "UDie")
				self.Con.player[i].still_alive = False		
				self.Con.player[i].BSVar.set('blood:'+str(self.Con.player[i].blood) \
						+ '/score:'+str(self.Con.player[i].score))		
		return


	def blood_control(self):
		for i in list(self.Con.player):		
			if type(self.Con.player[i]) != type('a') and self.Con.player[i].still_alive:
				# minus 1 blood every sec.
				if self.Con.player[i].blood_count != self.count_down - self.passed_sec:
					self.Con.player[i].blood_count = self.count_down - self.passed_sec
					self.Con.player[i].blood -= 1
				# Stay at a place last for 3 sec, then minus blood 10cc.
				if self.Con.player[i].big_pos()\
					!= self.Con.player[i].stay_pos:
					self.Con.player[i].stay_time = self.passed_sec
					self.Con.player[i].stay_pos = self.Con.player[i].big_pos()
				elif self.passed_sec - self.Con.player[i].stay_time > 3:
					self.Con.player[i].blood -= 10
					self.Con.player[i].stay_time = self.passed_sec
		# if nobody alive game over.
		self._running = False
		for i in list(self.Con.player):		
			if type(self.Con.player[i]) != type('a') and self.Con.player[i].still_alive:
				self._running = True
				return 
		self.count_down = 0
		return

	def is_open_base(self):
		A_B = self.sum_of_teams('A') - self.sum_of_teams('B')
		# check the base condition and change it
		if self.count_down - self.passed_sec <= 10 and not self.count_down_final:
			self.count_down_final = True
			print('30')
			self.open_base('A')
			self.open_base('B')
		elif not self.count_down_final and self.open_base_time < 0:
			if A_B >= 5:
				self.open_base('A')
			elif (-1)*A_B >= 5:
				self.open_base('B')
		elif self.passed_sec - self.open_base_time > 10 and not self.count_down_final:	# 10s
			self.close_base('A')
			self.close_base('B')

	def open_base(self,team):
		# if open last for 10 sec.
		self.open_base_time = self.passed_sec
		# Open the base that the team can occupy.
		if team == 'A' and not self.tower['A_Base']:
			self.tower['A_Base'] = Tower((7,7),self.block_size,'img/base.png')
		elif team == 'B'and not self.tower['B_Base']:
			self.tower['B_Base'] = Tower((1,1),self.block_size,'img/base.png')
		# Clear all the tower.
		self.tower['A'] = None
		self.tower['B'] = None 
		self.tower['C'] = None

	def close_base(self,team):
		self.open_base_time = -1
		if team == 'A':
			self.tower['A_Base'] = None
		elif team == 'B':
			self.tower['B_Base'] = None
		# Reset all the towers.
		self.tower['A'] = Tower(self.turret['A'][random.randint(0,5)],self.block_size,'img/tower.png')
		self.tower['B'] = Tower(self.turret['B'][random.randint(0,5)],self.block_size,'img/tower.png')
		self.tower['C'] = Tower(self.turret['C'][random.randint(0,6)],self.block_size,'img/tower.png')

	def sum_of_teams(self,team):
		Sum = 0 # temp sum to calculate total score
		for idx in list(self.Con.player) :
			if type(self.Con.player[idx]) != type('a') and self.Con.player[idx].team == team:
				Sum += self.Con.player[idx].score
		return Sum

	def blood_of_teams(self,team):
		Sum = 0 # temp sum to calculate total score
		for idx in list(self.Con.player) :
			if type(self.Con.player[idx]) != type('a') and self.Con.player[idx].team == team:
				Sum += self.Con.player[idx].blood
		return Sum

	def on_render(self):
		self._display_surf.fill((0,0,0))
		self._display_surf.blit(self.bg_image,(0, 0))
		for i in list(self.tower):
			if self.tower[i]:
				self.tower[i].draw(self._display_surf)
		for i in list(self.Con.player):
			if type(self.Con.player[i]) != type('a') and \
				self.Con.player[i].still_alive:
				self.Con.player[i].draw(self._display_surf)
		self._display_surf.blit(self._text_surf,(0,self.GameHeigh))
		pygame.display.flip()

	def on_cleanup(self):
		pygame.quit()
		print("pygame.quit()")
		if self._GG:
			#print all player finished time to the screen
			print_mes = "\tTeam A:\n"
			#print team A
			for i in list(self.Con.player):
				if type(self.Con.player[i]) != type('a') and self.Con.player[i].team == 'A':
					print_mes = print_mes + ("%s blood: %d / score： %d\n" \
						%(self.Con.player[i].name,self.Con.player[i].blood,self.Con.player[i].score))
			print_mes = print_mes + "\n\n\tTeam B:\n"
			#print team B
			for i in list(self.Con.player):
				if type(self.Con.player[i]) != type('a') and self.Con.player[i].team == 'B':
					print_mes = print_mes + ("%s blood: %d / score： %d\n" \
						%(self.Con.player[i].name,self.Con.player[i].blood,self.Con.player[i].score))
					# self.Con.player[i].done = False
			print_mes = print_mes + ("\n剩餘時間: %d分 %d%d秒" \
				%(self.game_time_min,self.game_time_sec10,self.game_time_sec))
			messagebox.showinfo(self._GG,print_mes)
		

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

