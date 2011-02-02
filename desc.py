from pygame import Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from text import TextRenderer

class CreatureDescription(object):
    dt = 0.01
    
    def __init__(self, creature, font):
        self._creature = creature

        self._sprites = LayeredDirty()

        self.scale(font)

    def _addline(self, surface, text, color, dy):
        image = self._renderer.render(text, color)
        surface.blit(image, (0,dy))
        return dy + image.get_height()

    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])

        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        dy = 0
        dy = self._addline(self._background,
                           self._creature.physical(),
                           (255,255,255),
                           dy)
        appetites = self._creature.appetitereport()
        if appetites:
            dy = self._addline(self._background,
                               appetites,
                               (255,255,255),
                               dy)

    def scale(self, font):
        self._font = font
        
        self._sprites.empty()
        self._background = None

    def resize(self, size):
        self._makebackground(size)

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                return True, None

        return False, self

    def draw(self, surface):
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
        
        self._sprites.clear(surface, self._background)
        self._sprites.draw(surface)