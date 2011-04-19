from math import sin, cos, pi

import pygame

def coolscale(v):
    m = 1020
    r = 255 - m * v if v < 0.25 else 0
    g = (255 if v < 0.75 else
         255 - m * (v - 0.75))
    b = (255 - m * v if v < 0.25 else
         m * (v - 0.25) if v < 0.5 else
         255)
    return r, g, b

class ClimateClassDisplay(object):
    dt = 0.01
    
    def __init__(self, summary, sealevel):
        self._summary = summary
        self._sealevel = sealevel
        self.dirty = True

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self.dirty = True

    CLIMATE = 0
    THRESHOLD = 1
    MOISTURE = 2

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.dirty = True

    def handle(self, e):
        return False

    colors = {
        u'A' : {
            u'f' : (0,0,255),
            u'm' : (0,63,255),
            u'w' : (0,127,255) },
        u'B' : {
            u'S' : (255,127,0),
            u'W' : (255,0,0) },
        u'C' : {
            u'f' : (0,255,0),
            u's' : (255,255,0),
            u'w' : (127,255,0) },
        u'D' : {
            u'f' : (0,255,255),
            u's' : (255,0,255),
            u'w' : (127,127,255) },
        u'E' : {
            u'F' : (127,127,127),
            u'T' : (191,191,191) }
        }
    
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
                        
                    h, t, p, thr, k = self._summary[y][xo]


                    if h > self._sealevel:
                        if self.mode == self.CLIMATE:
                            color = self.colors[k[0]][k[1]]
                        elif self.mode == self.MOISTURE:
                            color = coolscale(p)
                        elif self.mode == self.THRESHOLD:
                            color = coolscale(thr)
                    else:
                        if self.mode == self.CLIMATE:
                            color = (255,255,255)
                        else:
                            color = (0,0,0)

                    block.fill(color)
                   
                    self._screen.blit(block,
                                      ((x + (res[0] - len(self._summary[y]))/2)*block.get_width(),
                                       y*block.get_height()))

            self.dirty = False
                    
        surface.blit(self._screen, (0,0))
