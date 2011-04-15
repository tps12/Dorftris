from math import sin, cos, pi

import pygame

def colorscale(v):
    m = 1275
    r = (255 - m * v if v < 0.2 else
         0 if v < 0.6 else
         m * (v - 0.6) if v < 0.8 else
         255)
    g = (0 if v < 0.2 else
         m * (v - 0.2) if v < 0.4 else
         255 if v < 0.8 else
         255 - m * (v - 0.8))
    b = (255 if v < 0.4 else
         255 - m * (v - 0.4) if v < 0.6 else
         0)
    return r, g, b

def warmscale(v):
    m = 510
    r = 255
    g = v * m if v < 0.5 else 255
    b = 0 if v < 0.5 else m * (v - 0.5)
    return r, g, b

def coolscale(v):
    m = 1020
    r = 255 - m * v if v < 0.25 else 0
    g = (255 if v < 0.75 else
         255 - m * (v - 0.75))
    b = (255 - m * v if v < 0.25 else
         m * (v - 0.25) if v < 0.5 else
         255)
    return r, g, b

class ClimateSummaryDisplay(object):
    dt = 0.01
    
    def __init__(self, summary):
        self._summary = summary
        self.dirty = True

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self.dirty = True

    def handle(self, e):
        return False
    
    def draw(self, surface):
        if self.dirty or self._screen.get_size() != surface.get_size():
            self._screen = pygame.Surface(surface.get_size(), 0, 32)
        
            self._screen.fill((0,0,0))

            self.dirty = False
                    
        surface.blit(self._screen, (0,0))
