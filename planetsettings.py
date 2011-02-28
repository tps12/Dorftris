from math import acos, asin, atan2, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from button import Button

class PlanetSettings(object):
    scale = None
    
    def __init__(self, zoom, planet):
        self.zoom = zoom
        self.rotate = 0

        self.planet = planet
        
        self.definetiles()

        self.selection = None
        self._buttons = []

    @property
    def description(self):
        return _(u'{planet} Settings').format(planet=self.planet.name)

    def definetiles(self):
        self.uifont = self.zoom.font
                
    def makebackground(self, surface):
        surface.fill((0,0,0))

        hotkeys = []
        del self._buttons[:]
        for label, action in self.planet.actions():
            self._buttons = [
                Button(self.zoom, hotkeys, label, action)
                ]

        size = surface.get_size()
        y = 0
        for b in self._buttons:
            b.location = (0, y)
            b.draw(surface)
            y += b.size[1]
        
    def handle(self, e):
        for b in self._buttons:
            if b.handle(e):
                return True
        
        return False
                                 
    def draw(self, surface):
        self.makebackground(surface)
