from pygame import Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from text import TextRenderer

class InfoView(object):
    def __init__(self, playfield, font):
        self._playfield = playfield
        self._cursor = None
        
        self.scale(font)

    @property
    def width(self):
        return self._font.size('-' * 16)[0]

    def _describecreatures(self, surface, tile, dy):
        pass

    def _describeitems(self, surface, tile, dy):
        pass

    def _describetile(self, surface, location):
        x, y, z = location
        tile = self._playfield.game.world.space[location]
        if tile.is_passable():
            if self._playfield.game.world.space[(x,y,z-1)].is_passable():
                s = _('Open air')
            else:
                s = _('Ground')
        else:
            s = _('Solid')
        image = self._renderer.render(s, (255,255,255))
        surface.blit(image, (0,0))
        dy = image.get_height()

        self._describecreatures(surface, tile, dy)
        self._describeitems(surface, tile, dy)

    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])

        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        if self._cursor:
            self._describetile(self._background, self._cursor)
    
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        return False

    def draw(self, surface):
        cursor = self._playfield.cursor
        if self._cursor != cursor:
            self._cursor = cursor
            self._background = None
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
