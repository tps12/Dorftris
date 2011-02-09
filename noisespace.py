from random import randint

from noise import snoise2

from space import *

class NoiseSpace(Space):
    def __init__(self, dim):
        Space.__init__(self, dim)
        self._d = randint(-2048,2048), randint(-2048,2048)

    def groundlevel(self, x, y):
        return 64 + int(16 * snoise2(
            (x+self._d[0])/128.0,
            (y+self._d[1]+(x&1)*0.5)/128.0,
            12,
            0.5))
