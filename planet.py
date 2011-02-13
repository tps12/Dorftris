from math import cos, pi, sin

from noise import pnoise3

class Planet(object):
    def sample(self, latitude, longitude):
        lat, lon = [v*pi/180 for v in latitude, longitude]
        c = cos(lat)
        x, y, z = c * cos(lon), c * sin(lon), sin(lat)

        octaves = 10
        persist = 0.7

        return 9000 * pnoise3(x, y, z, octaves, persist)
