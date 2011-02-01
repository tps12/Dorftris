from pygame.locals import *

from details import CreatureDetails
from info import InfoView
from playfield import Playfield

class GameScreen(object):
    dt = 0.05
    
    def __init__(self, game, font, zoom):
        self._game = game
        self._playfield = Playfield(self._game, font, zoom)
        self._info = InfoView(self._playfield, font, zoom)
        self.scale(font)

    def scale(self, font):
        self._font = font
        self._playfield.scale(self._font)
        self._info.scale(self._font)
        
    def resize(self, size):
        self._fieldwidth = max(0, size[0] - self._info.width)
        self._playfield.resize((self._fieldwidth, size[1]))
        self._info.resize((size[0] - self._fieldwidth, size[1]))

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.unicode == 'c':
                return True, CreatureDetails(self._game.world.creatures[0],
                                             self._font)

        if self._playfield.handle(e):
            return True, self

        handled, child = self._info.handle(e)
        if handled:
            return True, child if child is not self._info else self
        
        return False, self

    def _playinfosurfaces(self, surface):
        size = surface.get_size()
        return (surface.subsurface(Rect((0,0),(self._fieldwidth,size[1]))),
                surface.subsurface(Rect((self._fieldwidth,0),
                                        (size[0]-self._fieldwidth, size[1]))))
                    
    def draw(self, surface):
        play, info = self._playinfosurfaces(surface)
        self._playfield.draw(play)
        self._info.draw(info)
