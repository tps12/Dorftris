from math import acos, asin, atan2, cos, pi, sin, sqrt

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

        ylim = surface.get_height()/height
        dlat = float(self.selected[0][1] - self.selected[0][0])/ylim
        xmax = 0
        for y in range(ylim):
            lat = self.selected[0][0] + y * dlat
            scale = cos(lat * pi/180)

            w = int(surface.get_width() * scale/width)
            if w > xmax:
                xmax = w

        hmin = hmax = 0
        for y in range(ylim):
            lat = self.selected[0][0] + y * dlat
            scale = cos(lat * pi/180)

            xlim = int(surface.get_width() * scale/width)
            for x in range(xlim):
                dx = float(xmax - xlim)/2
                
                lon = self.selected[1][0] + (x + dx) * scale * dlat
                
                h = self.planet.sample(lat, lon)
                if h < hmin:
                    hmin = h
                if h > hmax:
                    hmax = h

        for y in range(ylim):
            lat = self.selected[0][0] + y * dlat
            scale = cos(lat * pi/180)

            xlim = int(surface.get_width() * scale/width)
            for x in range(xlim):
                dx = float(xmax - xlim)/2
                
                lon = self.selected[1][0] + (x + dx) * scale * dlat
                
                block = template.copy()
                h = self.planet.sample(lat, lon)
                if h < 0:
                    color = 0, 0, int(255 * (1 - h/hmin))
                else:
                    color = 0, int(255 * h/hmax), 0
                block.fill(color)
                surface.blit(block, (int((x+dx)*width), y*height))

    def detail(self):
        return Region(self.zoom, self, self._zoom)

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
