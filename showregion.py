from math import acos, asin, atan2, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from noiseregion import NoiseRegion

class Region(object):
    def __init__(self, zoom, source, zoomin):
        self.zoom = zoom

        self.planet = source.planet
        
        self.definetiles()

        self.selected = source.selection
        self.selection = [span for span in self.selected]

        self._zoom = zoomin

    def definetiles(self):
        self.uifont = self.zoom.font
                
    def makebackground(self, surface):
        surface.fill((0,0,0))
        
        template = Surface(2*(min(self.zoom.width, self.zoom.height),))
        template.fill((0,0,0,255))
        width,height = template.get_size()

        xlim, ylim = self.size[0]/width, self.size[1]/height

        dy, dx = [float(self.selected[i][1] - self.selected[i][0])/
                  (ylim,xlim)[i]
                  for i in range(2)]

        region = NoiseRegion(self.planet, *self.selected)

        limits = [float('inf'),-float('inf')]

        hs = [[None for y in range(ylim)] for x in range(xlim)]

        for x in range(xlim):
            lon = self.selected[1][0] + x * dx
            for y in range(ylim):
                lat = self.selected[0][0] + y * dy

                h = region.sample(x * dx, y * dy)

                if h < limits[0]:
                    limits[0] = h
                if h > limits[1]:
                    limits[1] = h

                hs[x][y] = h

        for x in range(xlim):
            for y in range(ylim):        
                block = template.copy()
                h = hs[x][y]
                color = ((0,int(255 * (h/limits[1])),0) if h > 0
                         else (0,0,int(255 * (1 - h/limits[0]))))

                block.fill(color)
                surface.blit(block, (x * width, y * height))

    def _select(self, pos):
        for i in range(2):
            span = (self.selected[i][1] - self.selected[i][0])/5
            d = pos[i]/float(self.size[i])
            limits = [d - span/2, d + span/2]
            if limits[0] < self.selected[i][0]:
                limits[1] += self.selected[i][0] - limits[0]
                limits[0] = self.selected[i][0]
            elif limits[1] > self.selected[i][1]:
                limits[0] -= limits[1] - self.selected[i][1]
                limits[1] = self.selected[i][1]
                
            self.selection[i] = limits
        self._zoom()

    def handle(self, e):
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            self._select(e.pos)
            return True
        return False
                                 
    def draw(self, surface):
        self.size = surface.get_size()
        self.makebackground(surface)
