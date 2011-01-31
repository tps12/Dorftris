from pygame import Rect, Surface
from pygame.locals import *
from pygame.sprite import *

class InfoView(object):
    def __init__(self, selection, font):
        self._selection = selection
        
        self.scale(font)

    @property
    def width(self):
        return self._font.size('-' * 16)[0]
    
    def scale(self, font):
        self._font = font

    def resize(self, size):
        pass

    def handle(self, e):
        return False

    def draw(self, surface):
        pass
