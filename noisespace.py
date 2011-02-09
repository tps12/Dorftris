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

    def __getitem__(self, loc):
        if not all([0 <= loc[i] < self.dim[i] for i in range(3)]):
            return None
        
        g = self.groundlevel(loc[0], loc[1])
        
        if loc not in self.cache:            
            if loc[2] == g:
                self.cache[loc] = Empty(randint(0,3), Grass)
            elif loc[2] > g:
                self.cache[loc] = Empty(randint(0,3))
            elif loc[2] >= g - 3:
                self.cache[loc] = Earth(Clay, randint(0,3))
            else:
                self.cache[loc] = Earth(Stone, randint(0,3))

        tile = self.cache[loc]
        if loc[2] >= g:
            tile.revealed = True
        return tile
