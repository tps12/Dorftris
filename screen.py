from pygame import mouse
from pygame.locals import *

from details import CreatureDetails
from info import InfoView
from playfield import Playfield

class GameScreen(object):
    dt = 0.05
    
    def __init__(self, game, player, font, zoom, push, pop):
        self._game = game
        self._playfield = Playfield(self._game, player, font, zoom)
        self._info = InfoView(self._playfield, font, zoom, push, pop)
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
        if e.type == MOUSEMOTION:
            mouse.set_visible(True)
        
        if self._playfield.handle(e):
            return True

        if 'pos' in e.dict:
            e.dict['pos'] = (e.pos[0] - self._fieldwidth, e.pos[1])
        return self._info.handle(e)

    def _playinfosurfaces(self, surface):
        size = surface.get_size()
        return (surface.subsurface(Rect((0,0),(self._fieldwidth,size[1]))),
                surface.subsurface(Rect((self._fieldwidth,0),
                                        (size[0]-self._fieldwidth, size[1]))))
                    
    def draw(self, surface):
        play, info = self._playinfosurfaces(surface)
        self._playfield.draw(play)
        self._info.draw(info)
