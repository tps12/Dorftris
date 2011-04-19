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

                    tf = lambda c: c * 75.0 - 25.0
                    pf = lambda c: c * 1800.0/len(cs)
                    ts = [tf(c[0]) for (h,c) in cs]
                    ps = [pf(c[2]) for (h,c) in cs]

                    if h > 0:
                        thr = sum(ts)/len(cs) * 20
                        byt = sorted(range(len(ts)), key=lambda i: ts[i])
                        tot = sum(ps)
                        inh = sum([ps[i] for i in byt[-len(byt)/2:]])
                        if inh >= 0.7 * tot:
                            thr += 280
                        elif inh >= 0.3 * tot:
                            thr += 140

                        if self.mode == self.CLIMATE:
                            if tot <= thr:
                                # B
                                if tot <= thr/2:
                                    # W
                                    color = (255,0,0)
                                else:
                                    # S
                                    color = (255,127,0)
                            elif min(ts) >= 18:
                                # A
                                if all([p >= 60*len(ps) for p in ps]):
                                    # f
                                    color = (0,0,255)
                                elif any([(100 - tot/25)*len(ps) <= p < 60*len(ps)
                                          for p in ps]):
                                    # m
                                    color = (0,63,255)
                                else:
                                    # w
                                    color = (0,127,255)
                            elif max(ts) > 10:
                                if min(ts) >= -3:
                                    # C
                                    if (min([ps[i] for i in byt[-len(byt)/2:]]) <
                                        max([ps[i] for i in byt[:len(byt)/2]])/10.0):
                                        # w
                                        color = (127,255,0)
                                    elif (min([ps[i] for i in byt[:len(byt)/2]]) <
                                          min(30*len(ps),
                                              max([ps[i] for i in byt[-len(byt)/2:]])/3.0)):
                                        # s
                                        color = (255,255,0)
                                    else:
                                        # f
                                        color = (0,255,0)
                                else:
                                    # D
                                    if (min([ps[i] for i in byt[-len(byt)/2:]]) <
                                        max([ps[i] for i in byt[:len(byt)/2]])/10.0):
                                        # w
                                        color = (127,127,255)
                                    elif (min([ps[i] for i in byt[:len(byt)/2]]) <
                                          min(30*len(ps),
                                              max([ps[i] for i in byt[-len(byt)/2:]])/3.0)):
                                        # s
                                        color = (255,0,255)
                                    else:
                                        # f
                                        color = (0,255,255)
                            else:
                                # E
                                if max(ts) >= 0:
                                    # T
                                    color = (191,191,191)
                                else:
                                    # F
                                    color = (127,127,127)
                        elif self.mode == self.MOISTURE:
                            color = coolscale(tot/(1800.0/len(ps))/len(ps))
                        elif self.mode == self.THRESHOLD:
                            color = coolscale(max(0, thr)/1280.0)
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
