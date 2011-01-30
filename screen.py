from pygame import event, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

class GameScreen(object):
    def __init__(self, game, font):
        self.game = game

        self.sprites = LayeredDirty()

        self.zoom(font)

    def zoom(self, font):
        self.font = font
        self.sprites.empty()

    def resize(self, size):
        self.background = Surface(size, flags=SRCALPHA)
        self.background.fill((0,0,0))

    def draw(self, surface):
        self.sprites.clear(surface, self.background)
        self.sprites.draw(surface)
