from pygame import event, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import *
from pygame.sprite import *

from data import Barrel, Beverage, Corpse, Entity, Stockpile
from glyphs import GlyphGraphics

class GameScreen(object):
    def __init__(self, game, font, zoom):
        self.game = game

        self.zoom = zoom

        self.sprites = LayeredDirty()

        self.scale(font)

        self.offset = None

        self.selection = []
        
        self.level = 64

    def scale(self, font):
        self.font = font
        self.graphics = GlyphGraphics(self.font)
        
        self.sprites.empty()

    def _tilecoordinates(self, location):
        x, y, z = location
        x, y = [(x,y)[i] - self.offset[i] for i in range(2)]
        return (self.zoom.width/2 + x * self.zoom.width,
                self.zoom.height/2 + y * self.zoom.height +
                ((x+self.offset[0])&1) * self.zoom.height/2)

    def _screentile(self, coordinates):
        px, py = coordinates
        x = (px - self.zoom.width/2)/self.zoom.width
        return x, (py - self.zoom.height/2 - (x&1) *
                   self.zoom.height/2) / self.zoom.height

    def _colortile(self, surface, entity, color, varient, location):
        image = self.graphics[entity][varient].copy()
        image.fill(color, special_flags=BLEND_ADD)
        surface.blit(image, self._tilecoordinates(location))

    def _drawdesignation(self, surface, tile, location):
        pass

    def _drawground(self, surface, ground, location):
        self._colortile(surface, Entity('ground'),
                        ground.color, ground.varient, location)
        
        if ground.designated:
            self._drawdesignation(surface, ground, location)

    def _drawwall(self, surface, wall, location):
        if wall.designated:
            self._drawdesignation(surface, wall, location)

    def _drawtrunk(self, surface, trunk, location):
        pass

    def _drawtile(self, surface, tile, location):
        pass

    def _drawfarground(self, surface, ground, location):
        self._colortile(surface, Entity('air'), ground.color, 0, location)

    def _drawair(self, surface, location):
        pass

    def _getbackground(self, size):
        background = Surface(size, flags=SRCALPHA)
        background.fill((0,0,0))

        xs, ys = [range(self.offset[i], self.offset[i] + self.dimensions[i])
                  for i in range(2)]
        for x in xs:
            for y in ys:
                location = x, y, self.level
                tile = self.game.world.space[location]

                if tile is None:
                    continue

                if tile.is_passable():
                    locationbelow = x, y, self.level - 1
                    below = self.game.world.space[locationbelow]
                    if below.is_passable():
                        locationfarbelow = x, y, self.level - 2
                        farbelow = self.game.world.space[locationfarbelow]
                        if farbelow.is_passable():
                            self._drawair(background, locationfarbelow)
                        else:
                            self._drawfarground(background, farbelow,
                                                locationfarbelow)
                    elif below.kind:
                        self._drawfarground(background, below, locationbelow)
                    else:
                        self._drawground(background, below, locationbelow)

                elif tile.kind is not None:
                    self._drawtile(background, tile, location)
                else:
                    if tile.revealed:
                        self._drawwall(background, tile, location)
                    elif tile.designated:
                        self._drawdesignation(background, tile, location)

        return background

    def resize(self, size):
        tilecount = self._screentile(size)
        self.dimensions = tilecount

        if not self.offset:
            self.offset = tuple([r/2 if r > 0 else 0 for r in
                                 [self.game.dimensions[i] - self.dimensions[i]
                                  for i in range(2)]])
        
        self.background = self._getbackground(size)

    def handle(self, e):
        pass

    def draw(self, surface):
        if not self.background:
            self.resize(surface.get_size())

        self.sprites.clear(surface, self.background)
        self.sprites.draw(surface)
