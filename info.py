from pygame import Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from text import TextRenderer

class InfoView(object):
    def __init__(self, selection, font):
        self._selection = selection
        
        self.scale(font)

    @property
    def width(self):
        return self._font.size('-' * 16)[0]

    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])

        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))
        self._background.blit(self._renderer.render('testing',
                                                    (255,255,255)),
                             (0,0))
    
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        self._makebackground(size)

    def handle(self, e):
        return False

    def draw(self, surface):
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
