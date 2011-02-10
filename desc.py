from pygame import Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from scroll import Scroll
from text import TextRenderer

class CreatureDescription(object):
    dt = 0.01
    
    def __init__(self, creature, font):
        self._creature = creature

        self._sprites = LayeredDirty()

        self.scale(font)

    def _addline(self, surface, text, color, dy):
        image = self._renderer.render(text, color)
        h = image.get_height() + dy
        if h > surface.get_height():
            bigger = Surface((surface.get_width(), h), flags=surface.get_flags())
            bigger.blit(surface, (0,0))
            surface = bigger
            
        surface.blit(image, (0,dy))
        return surface, dy + image.get_height()

    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])

        bg = Surface(size, flags=SRCALPHA)
        bg.fill((0,0,0))

        dy = 0
        bg, dy = self._addline(bg,
                           self._creature.physical(),
                           (255,255,255),
                           dy)
        appetites = self._creature.appetitereport()
        if appetites:
            bg, dy = self._addline(bg,
                               appetites,
                               (255,255,255),
                               dy)
        inventory = self._creature.inventoryreport()
        if inventory:
            bg, dy = self._addline(bg,
                               inventory,
                               (255,255,255),
                               dy)

        self._background = Surface(size, flags = bg.get_flags())
        
        self._scroll.draw(self._background, bg)

    def scrolled(self):
        self._background = None

    def scale(self, font):
        self._font = font
        
        self._sprites.empty()
        self._background = None
        self._scroll = Scroll(self._font, None, self.scrolled)

    def resize(self, size):
        self._makebackground(size)

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                return True

        return False

    def draw(self, surface):
        if self._scroll.poll():
            self._background = None
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
        
        self._sprites.clear(surface, self._background)
        self._sprites.draw(surface)
