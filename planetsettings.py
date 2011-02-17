from math import acos, asin, atan2, pi, sqrt
from random import random

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from button import Button

class PlanetSettings(object):
    def __init__(self, zoom, planet):
        self.zoom = zoom
        self.rotate = 0

        self.planet = planet
        
        self.definetiles()

        self.selection = None
        self._buttons = []

    def definetiles(self):
        self.uifont = self.zoom.font
                
    def makebackground(self, surface):
        surface.fill((0,0,0))
        
        self._buttons = [
            Button(self.uifont, _(u'Randomize'), self._randomize)
            ]

        size = surface.get_size()
        y = 0
        for b in self._buttons:
            b.location = (0, y)
            b.draw(surface)
            y += b.size[1]

    def _randomize(self):
        self.planet.seeds = tuple([-5 + 5 * random()
                                   for i in range(len(self.planet.seeds))])
        
    def handle(self, e):
        for b in self._buttons:
            if b.handle(e):
                return True
        
        return False
                                 
    def draw(self, surface):
        self.makebackground(surface)
