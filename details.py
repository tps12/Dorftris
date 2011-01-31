from pygame import Rect, Surface
from pygame.locals import *
from pygame.sprite import *

class CreatureDetails(object):
    dt = 0.01
    
    def __init__(self, creature, font):
        self._creature = creature

        self._sprites = LayeredDirty()

        self.scale(font)

    def scale(self, font):
        self._font = font
        
        self._sprites.empty()

    def resize(self, size):
        self.background = Surface(size, flags=SRCALPHA)
        self.background.fill((0,0,0))
        self.background.blit(self._font.render('test', True, (255,255,255)),
                             (0,0))

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                return True, None

        return False, self

    def draw(self, surface):
        self._sprites.clear(surface, self.background)
        self._sprites.draw(surface)
