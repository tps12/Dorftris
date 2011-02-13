from math import acos, asin, atan2, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from etopo import Earth
from planet import Planet
from showplanet import Globe
from showregion import Region

class RenderWorld(object):
    game = None
    dt = 0.01
    
    def __init__(self, zoom):
        self.zoom = zoom
        self.rotate = 0

        self.globe = Globe(self.zoom, Planet())
        self.region = Region(self.zoom, self.globe.planet)
        
        self.definetiles()

        self.makescreen(display.get_surface().get_size())

    def definetiles(self):
        self.uifont = self.zoom.font
        self.globe.definetiles()
                                                 
    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)

        gd = min(size[0]/2,size[1])
        self.globesurf = self.screen.subsurface(Rect(0,0,gd,gd))
        self.regsurf = self.screen.subsurface(Rect(gd,0,gd,gd))

    def step(self):
        done = False
        
        for e in event.get():
            
            if e.type == QUIT:
                done = True
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    done = True                   
            elif e.type == MOUSEBUTTONUP:
                if e.button == 4:
                    self.zoom.width += 2
                    self.zoom.height += 2
                    self.makescreen(self.screen.get_size())
                    self.definetiles()
                    
                elif e.button == 5:
                    self.zoom.width = max(self.zoom.width - 2, 2)
                    self.zoom.height = max(self.zoom.height - 2, 4)
                    self.makescreen(self.screen.get_size())
                    self.definetiles()
                    
            elif e.type == VIDEORESIZE:
                self.makescreen(e.size)
                self.definetiles()

        self.globe.draw(self.globesurf)
        self.region.draw(self.regsurf)

        display.flip()

        return None if done else self
