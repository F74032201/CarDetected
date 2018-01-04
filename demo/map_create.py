import pygame, sys, os
from numpy import arange
import pyscreenshot as ImageGrab


class Simulator:

    W = 200
    x,y = W,0
    zoom = 1
    ts = s = 24
    speed = 1400
    tiles = {}
    selected = 'tiles'
    level = 0

    def __init__(self,window_size):
        self.w,self.h = window_size
        self.font = pygame.font.Font(None,40)
        self.loadTiles(36)
        self.mapNames = os.listdir('data/car_map')
        self.mapNames = sorted(sorted(self.mapNames),key=lambda i:len(i))
        self.maps = tuple('data/car_map/'+i for i in self.mapNames)
        self.mapNames = tuple(i[:i.index('.')] for i in self.mapNames)
        self.mapLen = len(self.maps)
        self.loadMap(self.maps[self.level])
        self.wall_v = []
        self.wall_h = []

    def reloadImages(self):
        s = int(self.s)+1; size = s,s
        for id in self.imageCopiesColored: self.images[id] = pygame.transform.scale(self.imageCopiesColored[id],size)

    def loadTiles(self,size):
        self.sideBar = pygame.Surface((self.W,self.h)); self.rects = {}; self.getID = {}; self.getName = {}
        self.images = {}; self.imageCopies = {}; self.imageCopiesColored = {}
        data = open('data/tiles/order.txt').read().split('\n'); row = 0; self.loop = []
        for i in range(len(data)):
            y,x = divmod(row,5); y*=size; x*=size
            id = i+1; self.rects[id] = pygame.Rect(x,y,size,size); self.getID[data[i]] = id; self.getName[id] = data[i]
            self.imageCopies[id] = pygame.image.load('data/tiles/%s.gif'%data[i]).convert_alpha()
            self.sideBar.blit(pygame.transform.scale(self.imageCopies[id],(size,size)),self.rects[id])
            row+=1; self.loop+=[id]

        id='tiles'; y,x = divmod(row,5); y*=size; x*=size; self.rects['tiles'] = pygame.Rect(x,y,size,size); self.loop+=[id]

    def saveMap(self,file):
        data = ''
        data+='fruittype '+str(self.fruitType).replace(' ','')+'\n'
        data+='bgcolor '+str(self.bgcolor).replace(' ','')+'\n'
        data+='fillcolor '+str(self.fillcolor).replace(' ','')+'\n'
        data+='edgelightcolor '+str(self.edgeLightColor).replace(' ','')+'\n'
        data+='edgeshadowcolor '+str(self.edgeShadowColor).replace(' ','')+'\n'
        data+='pelletcolor '+str(self.pelletColor).replace(' ','')+'\n\n'
        data += str(self.tiles)[1:-1].replace('.0,',',').replace('.0)',')').replace(' ','').replace(',(','\n(').replace(':',' ')
        open(file,'w').write(data)
        data_v = 'wall_v\n';data_h = 'wall_h\n';
        wall_v_dic = {}; wall_h_dic = {};
        self.wall_v = []
        self.wall_h = []

        for idx in list(self.tiles):
            wall_h_dic[(int(idx[0]/4),int(idx[1]/4))] = 0
            wall_v_dic[(int(idx[0]/4),int(idx[1]/4))] = 0
        
        for idx in list(self.tiles):
            #verticall
            if self.tiles[idx] == 12 or self.tiles[idx] == 13 or self.tiles[idx] == 16:
                wall_v_dic[(int(idx[0]/4),int(idx[1]/4))]+=1
            #horrozontal
            elif self.tiles[idx] == 14 or self.tiles[idx] == 15 or self.tiles[idx] == 17:
                wall_h_dic[(int(idx[0]/4),int(idx[1]/4))]+=1
            elif self.tiles[idx] <= 26 and self.tiles[idx] >= 18:
                wall_v_dic[(int(idx[0]/4),int(idx[1]/4))]+=1
                wall_h_dic[(int(idx[0]/4),int(idx[1]/4))]+=1
        for idx in list(wall_v_dic):
            if wall_v_dic[idx] == 4: self.wall_v.append([idx[0],idx[1]])
        for idx in list(wall_h_dic):
            if wall_h_dic[idx] == 4: self.wall_h.append([idx[0],idx[1]])
        print(self.wall_v)
        open('mapp.py','w').write('wall_v='+str(self.wall_v)+'\n'+'wall_h='+str(self.wall_h))

    def loadMap(self,file):
        data = open(file).read().split('\n'); self.tiles = {}
        for line in data:
            if not line: continue
            name,value = line.split(' '); value = eval(value)
            if name=='fruittype': self.fruitType = value
            elif name=='bgcolor': self.bgcolor = value
            elif name=='fillcolor': self.fillcolor = value
            elif name=='edgelightcolor': self.edgeLightColor = value
            elif name=='edgeshadowcolor': self.edgeShadowColor = value
            elif name=='pelletcolor': self.pelletColor = value
            else: self.tiles[eval(name)] = value

        for id in self.imageCopies:
            image = self.imageCopiesColored[id] = self.imageCopies[id].copy()
            for y in range(16):
                for x in range(16):
                    color = image.get_at((x,y))[:3]
                    if color==(255,206,255): image.set_at((x,y),self.edgeLightColor)
                    elif color==(132,0,132): image.set_at((x,y),self.fillcolor)
                    elif color==(255,0,255): image.set_at((x,y),self.edgeShadowColor)
                    elif color==(128,0,128): image.set_at((x,y),self.pelletColor)

        self.reloadImages()

        self.mapName = self.font.render(self.mapNames[self.level],2,(0,255,0))
        self.mapNameRect = self.mapName.get_rect(topleft=(self.W+10,10))

    def zoomTo(self,p,speed): self.zoom+=speed; self.x-=p[0]*speed; self.y-=p[1]*speed; self.s = self.ts*self.zoom; self.reloadImages()
    def get_pos(self,p): return (p[0]-self.x)/self.zoom, (p[1]-self.y)/self.zoom

    def events(self,event,key,mouse):
        if event.type == pygame.MOUSEMOTION and mouse[1]: self.x+=event.rel[0]; self.y+=event.rel[1]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 and self.zoom<3: self.zoomTo(self.mpos,0.15)
            elif event.button == 5 and self.zoom>0.3: self.zoomTo(self.mpos,-0.15)
            elif event.button == 1:
                for id in self.loop:
                    if self.rects[id].collidepoint(event.pos): self.selected = id

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE: self.tiles = {}
            elif event.key == pygame.K_s:
                if key[pygame.K_LCTRL]: self.saveMap('map.txt')

            elif event.key == pygame.K_LEFT: self.level = (self.level-1)%self.mapLen; self.loadMap(self.maps[self.level])
            elif event.key == pygame.K_RIGHT: self.level = (self.level+1)%self.mapLen; self.loadMap(self.maps[self.level])

    def isWall(self,pos): return pos in self.tiles and self.getName[self.tiles[pos]].startswith('wall')

    def getAdj(self,pos):
        adj = tuple((pos[0]+x,pos[1]+y) for x,y in ((0,-1),(0,1),(-1,0),(1,0)))
        return tuple(pos if self.isWall(pos) else None for pos in adj)

    def setWall(self,pos):
        adj = self.getAdj(pos)
        name = 'wall-'+''.join('udlr'[i] for i in (0,1,2,3) if adj[i])
        self.tiles[pos] = self.getID[name]; return adj

    def addWall(self,pos):
        adj = self.setWall(pos)
        for pos in adj:
            if pos: self.setWall(pos)

    def delWall(self,pos):
        del self.tiles[pos]; adj = self.getAdj(pos)
        for pos in adj:
            if pos: self.setWall(pos)

    def update(self,dt,key,mouse,mpos):
        mx,my = self.mpos = self.get_pos(mpos)
        if not key[pygame.K_LCTRL]:
            if key[pygame.K_w]: self.y+=dt*self.speed*self.zoom
            if key[pygame.K_s]: self.y-=dt*self.speed*self.zoom
            if key[pygame.K_a]: self.x+=dt*self.speed*self.zoom
            if key[pygame.K_d]: self.x-=dt*self.speed*self.zoom

        if mpos[0]>self.W and mouse[0]^mouse[2]:
            pos = mx//self.ts,my//self.ts
            if mouse[0]:
                if self.selected=='tiles': self.addWall(pos)
                elif self.selected: self.tiles[pos] = self.selected
            elif pos in self.tiles:
                if self.selected=='tiles': self.delWall(pos)
                else: del self.tiles[pos]

    def drawGrid(self,screen):
        for x in arange(self.x%self.s,self.w,self.s): pygame.draw.line(screen,(32,44,53),(x,0),(x,self.h))
        for y in arange(self.y%self.s,self.h,self.s): pygame.draw.line(screen,(32,44,53),(0,y),(self.w,y))
        pygame.draw.line(screen,(255,255,26),(self.x,0),(self.x,self.h))
        pygame.draw.line(screen,(255,255,26),(0,self.y),(self.w,self.y))

    def draw(self,screen,mpos):
        self.drawGrid(screen)
        for pos,id in self.tiles.items(): screen.blit(self.images[id],(self.x+pos[0]*self.s,self.y+pos[1]*self.s))

        screen.blit(self.sideBar,(0,0))
        for id in self.loop:
            if self.rects[id].collidepoint(mpos): pygame.draw.rect(screen,(0,255,0),self.rects[id],1)

        screen.blit(self.mapName,self.mapNameRect)


def main():
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode((1000,800))
    fpsclock = pygame.time.Clock(); fps = 60; caption = 'Map Editor'
    program = Simulator(screen.get_size())

    while True:
        dt = fpsclock.tick(fps)/1000
        pygame.display.set_caption('%s - FPS %.2f'%(caption,fpsclock.get_fps()))
        key = pygame.key.get_pressed(); mouse = pygame.mouse.get_pressed(); mpos = pygame.mouse.get_pos()

        screen.fill((0,0,0))
        program.draw(screen,mpos)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            program.events(event,key,mouse)

        program.update(dt,key,mouse,mpos)


if __name__ == '__main__':
    main()

