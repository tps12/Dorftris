from math import acos, asin, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from etopo import Earth
from planet import Planet

class RenderWorld(object):
    game = None
    dt = 0.01
    
    def __init__(self, zoom):
        self.zoom = zoom
        self.rotate = 0

        self.planet = Planet()
        
        self.definetiles()

        self.makescreen(display.get_surface().get_size())

    def definetiles(self):
        self.uifont = self.zoom.font
                
    def makebackground(self):
        self.screen.fill((0,0,0))
        
        template = Surface(2*(min(self.zoom.width, self.zoom.height),))
        template.fill((0,0,0,255))
        width,height = template.get_size()

        o = min(self.screen.get_width()/width,
                self.screen.get_height()/height)/2

        for y in range(2*o):
            lat = 90 - acos(y/(2.0*o)) * 90
            r = int(sqrt(o**2-(o-y)**2))
            for x in range(o-r, o+r):
                block = template.copy()

                lon = self.rotate + asin(x/float(o+r)) * 360/pi
                h = self.planet.sample(lat, lon)
                color = ((0,int(255 * (h/9000.0)),0) if h > 0
                         else (0,0,int(255 * (1 + h/11000.0))))

                block.fill(color)
                self.screen.blit(block, (x * width, y * height))
                                 
    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)
        
        self.makebackground()

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

        self.rotate -= 5
        if self.rotate <= -180:
            self.rotate += 360
        self.makebackground()

        display.flip()

        return None if done else self
