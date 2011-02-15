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

        xlim, ylim = surface.get_width()/width, surface.get_height()/height

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

    def handle(self, e):
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            for i in range(2):
                span = self.selected[i][1] - self.selected[i][0]
                self.selection[i] = 2*span/5, 3*span/5
                self._zoom(self.selection)
            return True
        return False
                                 
    def draw(self, surface):
        self.makebackground(surface)
