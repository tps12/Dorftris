from pygame import draw, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from data import Creature, CulturedCreature
from desc import CreatureDescription
from text import TextRenderer

class CreatureDetails(object):
    def __init__(self, creature, font, prefs):
        self._creature = creature
        self._prefs = prefs
        
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
                           self._creature.namecard(),
                           self._prefs.selectioncolor,
                           dy)
        dy = self._addline(self._background,
                           self._creature.noun,
                           (255,255,255),
                           dy)

        self._buttons = []
    
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_RETURN and self._details:
                return True, self._details()
            elif e.key == K_ESCAPE:
                return True, None
        
        elif (e.type == MOUSEBUTTONDOWN and
            e.button == 1):
            return True, self._details()
        
        return False, self

    def draw(self, surface):
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
