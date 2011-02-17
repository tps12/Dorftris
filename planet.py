from math import cos, pi, sin

from noise import pnoise3

class Planet(object):
    def __init__(self):
        self.seeds = 18, -3, 3, -3, 2, 0
        
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
