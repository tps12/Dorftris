from math import acos, asin, atan2, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

class Globe(object):
    def __init__(self, zoom, planet, selection):
        self.zoom = zoom
        self.rotate = 0

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

        o = min(surface.get_width()/width,
                surface.get_height()/height)/2

        for y in range(2*o):
            lat = 90 - acos(y/(2.0*o)) * 90
            r = int(sqrt(o**2-(o-y)**2))
            for x in range(o-r, o+r):
                block = template.copy()

                v = [float(x-r)/o, float(y-o)/o]

                if x >= o:
                    lon = self.rotate - acos(float((x-(o-r)-r))/r) * 180/pi
                else:
                    lon = self.rotate + 180 + acos(float(r-(x-(o-r)))/r) * 180/pi

                if lon > 180:
                    lon -= 360

                h = self.planet.sample(lat, lon)
                color = ((0,int(255 * (h/9000.0)),0) if h > 0
                         else (0,0,int(255 * (1 + h/11000.0))))

                block.fill(color)
                if self.selected[0][0] <= lat <= self.selected[0][1]:
                    if self.selected[1][0] <= lon <= self.selected[1][1]:
                        block.fill((64,0,0))
                surface.blit(block, (x * width, y * height))
                                 
    def draw(self, surface):
        self.rotate += 5
        if self.rotate >= 180:
            self.rotate -= 360

        self.makebackground(surface)
