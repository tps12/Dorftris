from pygame import draw, event, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Furnishings

class FurnishingSelect(object):
    def __init__(self, player, location, font, prefs):
        self._player = player
        self._location = location
        self._prefs = prefs
        
        self.scale(font)

    def _addbutton(self, surface, text, click, dy):
        button = Button(self._font, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]

    def _choose(self, item):
        return lambda: self._furnish(item)

    def _furnish(self, item):
        self._player.furnish(self._location, item)
                
    def _makebackground(self, size):
        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        dy = 0

        self._buttons = []
        for pile in self._player.getstockpiles(Furnishings):
            for item in pile.contents:
                dy = self._addbutton(self._background,
                                     item.description(),
                                     self._choose(item),
                                     dy)
        for item in self._player.unstockpileditems(Furnishings):
            dy = self._addbutton(self._background,
                                 item.description(),
                                 self._choose(item),
                                 dy)
   
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                return True, False, None
        
        elif (e.type == MOUSEBUTTONDOWN and
            e.button == 1):
            for button in self._buttons:
                if button.handle(e):
                    return True, False, None
                
        return False, False, self

    def draw(self, surface):
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
