from pygame import display, draw, event, font, key, Rect
from pygame.locals import *

from etopo import Earth
from planet import Planet

class RenderWorld(object):
    game = None
    dt = 0.01
    
    def __init__(self, zoom):
        self.zoom = zoom

        self.planet = Planet()
        
        self.definetiles()

        self.makescreen(display.get_surface().get_size())

    def definetiles(self):
        self.uifont = self.zoom.font
                
    def makebackground(self):
        for lat in range(-90, 90, 2):
            for lon in range(0, 360, 2):
                h = self.planet.sample(lat, lon)
                color = ((0,int(255 * (h/10000.0)),0) if h > 0
                         else (0,0,int(255 * (1 + h/10000.0))))
                draw.circle(self.screen,
                            color,
                            (2*lon,
                             2*(lat+90)),
                            2)

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

        display.flip()

        return None if done else self
