from math import sin, cos, pi

import pygame
from pygame.locals import *

def colorscale(v):
    m = 1275
    r = (255 - m * v if v < 0.2 else
         0 if v < 0.6 else
         m * (v - 0.6) if v < 0.8 else
         255)
    g = (0 if v < 0.2 else
         m * (v - 0.2) if v < 0.4 else
         255 if v < 0.8 else
         255 - m * (v - 0.8))
    b = (255 if v < 0.4 else
         255 - m * (v - 0.4) if v < 0.6 else
         0)
    return r, g, b

def warmscale(v):
    m = 510
    r = 255
    g = v * m if v < 0.5 else 255
    b = 0 if v < 0.5 else m * (v - 0.5)
    return r, g, b

def coolscale(v):
    m = 1020
    r = 255 - m * v if v < 0.25 else 0
    g = (255 if v < 0.75 else
         255 - m * (v - 0.75))
    b = (255 - m * v if v < 0.25 else
         m * (v - 0.25) if v < 0.5 else
         255)
    return r, g, b

class ClimateDisplay(object):
    dt = 0.01
    
    def __init__(self, sim):
        self._sim = sim
        
        self.selected = None
        self.adjacent = []
        self.sources = {}

        self._screen = None

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self.dirty = True

    @property
    def airflow(self):
        return self._airflow

    @airflow.setter
    def airflow(self, value):
        self._airflow = value
        self.dirty = True

    TERRAIN = 0
    INSOLATION = 1
    TEMPERATURE = 2
    SEABREEZE = 3
    PRECIPITATION = 4
    CONVECTION = 5

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.dirty = True

    def resolvesources(self, p, t, f):
        value = []
        for (s,w) in self._sim.sources(p):
            fw = f*w
            if fw > t:
                value.extend([(s, 0)] + self.resolvesources(s, t, fw/2))
            else:
                value.append((s,fw))
        return value
    
    def handle(self, e):
        if e.type == MOUSEBUTTONUP:
            mx, my = e.pos

            res = max([len(r) for r in self._sim.tiles]), len(self._sim.tiles)

            y = my / (self.size[1]/res[1])
            x = mx / (self.size[0]/res[0]) - (res[0] - len(self._sim.tiles[y]))/2

            r = self.rotate
            o = r * len(self._sim.tiles[y])/360

            xo = x + o
            if xo > len(self._sim.tiles[y])-1:
                xo -= len(self._sim.tiles[y])
            elif xo < 0:
                xo += len(self._sim.tiles[y])
            
            if 0 <= y < len(self._sim.tiles) and 0 <= xo < len(self._sim.tiles[y]):
                if self.selected == (xo,y):
                    self.selected = None
                    self.adjacent = []
                    self.sources = {}
                else:
                    self.selected = (xo,y)
                    self.adjacent = self._sim.adj[self.selected]
                    self.sources = dict(((s,w) for (s,w) in
                                         self.resolvesources(self.selected, 0.1, 1.0)))
       
                self._screen = None

                return True

        return False
    
    def draw(self, surface):
        self._sim.update()
            
        if self._sim.dirty or self._screen.get_size() != surface.get_size():
            self._screen = pygame.Surface(surface.get_size(), 0, 32)
            
            self.size = self._screen.get_size()
        
            self._screen.fill((0,0,0))

            res = max([len(r) for r in self._sim.tiles]), len(self._sim.tiles)
            template = pygame.Surface((self.size[0]/res[0],
                                       self.size[1]/res[1]), 0, 32)

            for y in range(res[1]):
                for x in range(len(self._sim.tiles[y])):
                    block = template.copy()

                    r = self.rotate
                    o = r * len(self._sim.tiles[y])/360

                    xo = x + o
                    if xo > len(self._sim.tiles[y])-1:
                        xo -= len(self._sim.tiles[y])
                    elif xo < 0:
                        xo += len(self._sim.tiles[y])
                    h = self._sim.tiles[y][xo][2]

                    climate = self._sim.climate[(xo,y)]

                    if self.selected == (xo, y):
                        color = (255,0,255)
                    elif (xo, y) in self.sources:
                        color = (255,255 * self.sources[(xo,y)]/0.1,0)
                    elif self.mode == self.INSOLATION:
                        ins = self._sim.insolation(y)                    
                        color = warmscale(ins)
                    elif h > 0:
                        if self.mode == self.PRECIPITATION:
                            color = coolscale(climate[4])
                        elif self.mode == self.SEABREEZE:
                            color = coolscale(climate[2])
                        elif self.mode == self.TEMPERATURE:
                            color = colorscale(climate[1])
                        elif self.mode == self.CONVECTION:
                            color = coolscale(climate[3])
                        else:
                            color = (0,int(255 * (h/9000.0)),0)
                    else:
                        if self.mode == self.PRECIPITATION:
                            color = (0,0,0)
                        elif self.mode == self.TEMPERATURE:
                            color = [(c+255)/2 for c in colorscale(climate[1])]
                        elif self.mode == self.SEABREEZE:
                            color = (0,0,0)
                        elif self.mode == self.CONVECTION:
                            color = (128,128,128)
                        else:
                            color = (0,0,int(255 * (1 + h/11000.0)))

                    block.fill(color)

                    if self.airflow:
                        s = sin(pi/2 * (y - res[1]/2)/res[1]/2) * 90
                        s *= sin(pi/2 * (x - len(self._sim.tiles[y])/2)/(len(self._sim.tiles[y])/2))

                        w, h = [c-1 for c in block.get_size()]

                        angle = climate[0] + s
                        if angle >= 337.5 or angle < 22.5:
                            p = w/2, h-1
                            es = (0, 0), (w-1, 0)
                        elif 22.5 <= angle < 67.5:
                            p = w-1, h-1
                            es = (0, h-1), (w-1, 0)
                        elif 67.5 <= angle < 112.5:
                            p = w-1, h/2
                            es = (0, 0), (0, h-1)
                        elif 112.5 <= angle < 157.5:
                            p = w-1, 0
                            es = (w-1, h-1), (0, 0)
                        elif 157.5 <= angle < 202.5:
                            p = w/2, 0
                            es = (0, h-1), (w-1, h-1)
                        elif 202.5 <= angle < 247.5:
                            p = 0, 0
                            es = (0, h-1), (w-1, 0)
                        elif 247.5 <= angle < 292.5:
                            p = 0, h/2
                            es = (w-1, 0), (w-1, h-1)
                        else:
                            p = 0, h-1
                            es = (0, 0), (w-1, h-1)

                        pygame.draw.lines(block, (255,255,255), False,
                                          [es[0], p, es[1]])
                   
                    self._screen.blit(block,
                                      ((x + (res[0] - len(self._sim.tiles[y]))/2)*block.get_width(),
                                       y*block.get_height()))

            self.dirty = False
                    
        surface.blit(self._screen, (0,0))
