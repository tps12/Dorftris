from math import acos, asin, atan2, cos, pi, sin, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from noise import pnoise2

class DetailedRegion(object):
    def __init__(self, zoom, source, zoomin):
        self.zoom = zoom

        self.source = source
        
        self.definetiles()

        self.selection = None

        self._zoom = zoomin

    def definetiles(self):
        self.uifont = self.zoom.font
                
    def makebackground(self, surface):
        surface.fill((0,0,0))
        
        template = Surface(2*(min(self.zoom.width, self.zoom.height),))
        template.fill((0,0,0,255))
        width,height = template.get_size()

        ylim = surface.get_height()/height
        xlim = surface.get_width()/width

        data = self.source.data()
        noise = [[pnoise2(self.source.selection[1][0]+x,
                          self.source.selection[0][0]+y,
                          6, 0.65) * 1000
                  for x in range(xlim)]
                 for y in range(ylim)]

        hmin = hmax = 0
        for y in range(ylim):
            for x in range(xlim):
                yd = int(len(data)*float(y)/ylim)
                xd = int(len(data[0])*float(x)/xlim)

                h = data[yd][xd]
                n = noise[y][x]
                if h < 0:
                    h += -n if n > 0 else n
                else:
                    h += n if n > 0 else -n
                if h < hmin:
                    hmin = h
                if h > hmax:
                    hmax = h

        self.rects = []
        for y in range(ylim):
            for x in range(xlim):
                block = template.copy()
                yd = int(len(data)*float(y)/ylim)
                xd = int(len(data[0])*float(x)/xlim)
                h = data[yd][xd]
                n = noise[y][x]
                if h < 0:
                    h += -n if n > 0 else n
                else:
                    h += n if n > 0 else -n
                if h < 0:
                    color = 0, 0, int(255 * (1 - h/hmin))
                else:
                    color = 0, int(255 * h/hmax), 0
                block.fill(color)
                rect = Rect(x*width, y*height, width, height)
                surface.blit(block, rect.topleft)
                self.rects.append((rect, (yd, xd)))

    def detail(self):
        return DetailedRegion(self.zoom, self, self._zoom)

    def data(self):
        return None

    def _select(self, coords):
        if not self.selection:
            zoom = True
            self.selection = [None, None]
        else:
            zoom = False
        
        if zoom:
            self._zoom()

    def handle(self, e):
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            for rect, coords in self.rects:
                if rect.collidepoint(e.pos):                    
                    self._select(coords)
                    return True
        return False
                                 
    def draw(self, surface):
        self.size = surface.get_size()
        self.makebackground(surface)
