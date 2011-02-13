from math import cos, pi, sin

from noise import snoise3

class Planet(object):
    def sample(self, latitude, longitude):
        lat, lon = [v*pi/180 for v in latitude, longitude]
        c = cos(lat)
        x, y, z = c * cos(lon), c * sin(lon), sin(lat)

        amp = 1.0
        persist = 0.75
        m = 0.0
        octaves = 24
        for i in range(octaves):
            m += amp
            amp *= persist

        return 2000 * snoise3(x, y, z, octaves, persist) / m
