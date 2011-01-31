from pygame.locals import *

from details import CreatureDetails
from playfield import Playfield

class GameScreen(object):
    dt = 0.05
    
    def __init__(self, game, font, zoom):
        self._game = game
        self._playfield = Playfield(self._game, font, zoom, [])
        self.scale(font)

    def scale(self, font):
        self._font = font
        self._playfield.scale(self._font)
        
    def resize(self, size):
        self._playfield.resize(size)

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.unicode == 'c':
                return True, CreatureDetails(self._game.world.creatures[0],
                                             self._font)

        if self._playfield.handle(e):
            return True, self
        
        return False, self
                    
    def draw(self, surface):
        self._playfield.draw(surface)
