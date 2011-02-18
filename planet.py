from math import cos, pi, sin
from random import random

from noise import pnoise3

class Planet(object):
    name = _(u'Random Planet')
    
    def __init__(self):
        self.randomize()

    def actions(self):
        return [(_(u'Randomize'), self.randomize)]

    def randomize(self):
        self.seeds = [-5 + 5 * random() for i in range(6)]
        
    def sample(self, latitude, longitude):
        lat, lon = [v*pi/180 for v in latitude, longitude]
        c = cos(lat)
        x, y, z = c * cos(lon), c * sin(lon), sin(lat)

        octaves = 12
        persist = 0.7

        b = 1 if pnoise3(x+self.seeds[0],
                         y+self.seeds[1],
                         z+self.seeds[2], 4, persist) > -0.125 else -1
        value = pnoise3(x+self.seeds[3],
                        y+self.seeds[4],
                        z+self.seeds[5], octaves, persist)
        if value > 0.25:
            value *= 1.25 * b
        elif value > 0:
            value *= b
        else:
            value *= 3

        scale = 7000
        return scale * value
