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

    TERRAIN = 0
    TEMPERATURE = 1
    HUMIDITY = 2
    CLIMATE = 3

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.dirty = True

    def handle(self, e):
        return False
    
    def draw(self, surface):
        if self.dirty or self._screen.get_size() != surface.get_size():
            self._screen = pygame.Surface(surface.get_size(), 0, 32)
        
            self._screen.fill((0,0,0))
            res = max([len(r) for r in self._summary]), len(self._summary)
            
            template = pygame.Surface((self._screen.get_width()/res[0],
                                       self._screen.get_height()/res[1]), 0, 32)

            for y in range(res[1]):
                for x in range(len(self._summary[y])):
                    block = template.copy()

                    r = self.rotate
                    o = r * len(self._summary[y])/360

                    xo = x + o
                    if xo > len(self._summary[y])-1:
                        xo -= len(self._summary[y])
                    elif xo < 0:
                        xo += len(self._summary[y])
                    h, climate = self._summary[y][xo]

                    if h > 0:
                        if self.mode == self.CLIMATE:
                            color = (int(255 * (1 - climate[1])),
                                     255,
                                     int(255 * (1 - climate[0])))
                        elif self.mode == self.TEMPERATURE:
                            color = colorscale(climate[0])
                        elif self.mode == self.HUMIDITY:
                            color = coolscale(climate[1])
                        else:
                            color = (0,int(255 * (h/9000.0)),0)
                    else:
                        if self.mode == self.TEMPERATURE:
                            color = [(c+255)/2 for c in colorscale(climate[0])]
                        else:
                            color = (0,0,int(255 * (1 + h/11000.0)))

                    block.fill(color)
                   
                    self._screen.blit(block,
                                      ((x + (res[0] - len(self._summary[y]))/2)*block.get_width(),
                                       y*block.get_height()))

            self.dirty = False
                    
        surface.blit(self._screen, (0,0))
