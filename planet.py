from math import cos, pi, sin

from noise import snoise2

class Planet(object):
    def sample(self, latitude, longitude):
        return 10000 * snoise2(latitude/100.0, longitude/100.0, 12, 0.65)
