from math import cos, pi, sin

from noise import snoise3

class Planet(object):
    def sample(self, latitude, longitude):
        lat, lon = [x * pi/180 for x in latitude, longitude]
        c = cos(lat)
        x, y, z = c * cos(lon), c * sin(lon), sin(lat)
        return 5000 * snoise3(x/1000, y/1000, z/1000, 1, 0)
