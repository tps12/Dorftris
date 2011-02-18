from math import acos, asin, atan2, cos, pi, sin, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from detailregion import DetailedRegion

class Region(object):
    description = _('Region')
    
    def __init__(self, zoom, source, zoomin):
        self.zoom = zoom

        self.planet = source.planet
        
        self.definetiles()

        self.selected = source.selection
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

        self.rects = []
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
                if self.selection:
                    if self.selection[0][0] <= lat <= self.selection[0][1]:
                        if self.selection[1][0] <= lon <= self.selection[1][1]:
                            block.fill((255,0,0,32),
                                       special_flags = BLEND_ADD)
                rect = Rect(int(x+dx)*width, y*height, width, height)
                surface.blit(block, rect.topleft)
                self.rects.append((rect, (lat, lon)))

    def detail(self):
        return DetailedRegion(self.zoom, self, self._zoom)

    def _select(self, coords):
        if not self.selection:
            zoom = True
            self.selection = [None, None]
        else:
            zoom = False
        
        yspan = (self.selected[0][1] - self.selected[0][0])/10.0
        yo = coords[0]
        self.selection[0] = yo - yspan/2, yo + yspan/2

        scale = cos(yo * pi/180)
        xspan = yspan * scale
        xo = coords[1]
        self.selection[1] = xo - xspan/2, xo + xspan/2

        if zoom:
            self._zoom()

    def data(self):
        xlim = ylim = 100
        data = [[None for x in range(xlim)] for y in range(ylim)]
        dlat = (self.selection[0][1] - self.selection[0][0])/ylim
        for y in range(ylim):
            lat = self.selection[0][0] + y * dlat
            dlon = dlat * cos(lat * pi/180)
            for x in range(xlim):
                lon = self.selection[1][0] + x * dlon
                data[y][x] = self.planet.sample(lat, lon)
        return data

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
