from math import acos, asin, atan2, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from etopo import Earth
from planet import Planet
from showplanet import Globe
from planetsettings import PlanetSettings

class RenderWorld(object):
    game = None
    dt = 0.01
    
    def __init__(self, zoom):
        self.zoom = zoom
        self.rotate = 0

        self._zoomrate = 0
        self._zooming = None

        self.left = PlanetSettings(self.zoom, Planet())
        self.right = Globe(self.zoom, self.left.planet, self._zoom)
        
        self.definetiles()

        self.makescreen(display.get_surface().get_size())

    def _zoom(self):
        self._zooming = 0

    def definetiles(self):
        self.uifont = self.zoom.font
        self.left.definetiles()
        self.right.definetiles()
                                                 
    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)

        self.leftsize = min(size[0]/2,size[1])
        d = self.leftsize

        if self._zooming is not None:
            if self._zoomrate < 100:
                self._zoomrate += 5
            self._zooming += self._zoomrate
            
            self.leftsize -= self._zooming
            if self.leftsize <= 0:
                self.leftsize = d
                self.left = self.right
                self.right = self.left.detail()
                self._zoomrate = 0
                self._zooming = None
        
        self.leftsurf = self.screen.subsurface(Rect((0,0),2*(d,)))
        self.rightsurf = self.screen.subsurface(Rect((self.leftsize,0), 2*(d,)))

    def step(self):
        done = False
        
        for e in event.get():
            if self.left.handle(e):
                continue

            if 'pos' in e.dict:
                e.dict['pos'] = e.pos[0] - self.leftsize, e.pos[1]
            if self.right.handle(e):
                continue
            
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

        if self._zooming is not None:
            self.makescreen(self.screen.get_size())

        self.left.draw(self.leftsurf)
        self.right.draw(self.rightsurf)

        display.flip()

        return None if done else self
