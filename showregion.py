from math import acos, asin, atan2, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

class Region(object):
    def __init__(self, zoom, planet, selection):
        self.zoom = zoom

        self.planet = planet
        
        self.definetiles()

        self.selected = selection

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

        for x in range(xlim):
            lon = self.selected[1][0] + x * dx
            for y in range(ylim):
                block = template.copy()
                lat = self.selected[0][0] + y * dy

                h = self.planet.sample(lat, lon)
                color = ((0,int(255 * (h/9000.0)),0) if h > 0
                         else (0,0,int(255 * (1 + h/11000.0))))

                block.fill(color)
                surface.blit(block, (x * width, y * height))

    def handle(self, e):
        return False
                                 
    def draw(self, surface):
        self.makebackground(surface)
