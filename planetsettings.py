from math import acos, asin, atan2, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

class PlanetSettings(object):
    def __init__(self, zoom, planet):
        self.zoom = zoom
        self.rotate = 0

        self.planet = planet
        
        self.definetiles()

        self.selection = None

    def definetiles(self):
        self.uifont = self.zoom.font
                
    def makebackground(self, surface):
        surface.fill((0,0,0))
        surface.blit(self.uifont.render('planet settings...', True, (255,255,255)),
                     (0,0))
        
    def handle(self, e):
        return False
                                 
    def draw(self, surface):
        self.makebackground(surface)
