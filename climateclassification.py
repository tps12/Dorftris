from math import sin, cos, pi

import pygame

class ClimateClassDisplay(object):
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
                    cs = self._summary[y][xo]

                    h = cs[0][0]

                    tf = lambda c: c * 200.0 - 50.0
                    pf = lambda c: c * 10000.0
                    ts = [tf(c[0]) for (h,c) in cs]
                    ps = [pf(c[1]) for (h,c) in cs]

                    if h > 0:

                        if sum(ps) <= sum(ts)/len(cs) * 20:
                            color = (255,0,0)
                        elif min(ts) >= 18:
                            color = (0,0,255)
                        elif max(ts) > 10:
                            if -3 <= min(ts) < 18:
                                color = (0,255,0)
                            else:
                                color = (255,0,255)
                        else:
                            color = (128,128,128)
                    else:
                        color = (255,255,255)

                    block.fill(color)
                   
                    self._screen.blit(block,
                                      ((x + (res[0] - len(self._summary[y]))/2)*block.get_width(),
                                       y*block.get_height()))

            self.dirty = False
                    
        surface.blit(self._screen, (0,0))
