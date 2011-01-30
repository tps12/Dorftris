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

    def _hex(self):
        return [(self.zoom.height/3,self.zoom.height),
                (0,self.zoom.height/2),
                (self.zoom.height/3,0),
                (self.zoom.width,0),
                (self.zoom.width+self.zoom.height/3,self.zoom.height/2),
                (self.zoom.width,self.zoom.height)]

    def _colortile(self, surface, entity, color, varient, location):
        image = self.graphics[entity][varient].copy()
        image.fill(color, special_flags=BLEND_ADD)
        surface.blit(image, self._tilecoordinates(location))

    def _tilerect(self, location):
        x, y = self._tilecoordinates(location)
        return Rect(x - self.zoom.height/3, y,
                    self.zoom.width + self.zoom.height/3, self.zoom.height+1)

    def _colorfill(self, surface, color, location):
        image = surface.subsurface(self._tilerect(location))
        gfxdraw.filled_polygon(image, self._hex(), color)

    def _colortint(self, surface, color, location):
        rect = self._tilerect(location)
        image = Surface(rect.size, flags=SRCALPHA)
        gfxdraw.filled_polygon(image, self._hex(), (0, 0, 0, 85))
        image.fill(color, special_flags=BLEND_ADD)
        surface.blit(image, rect.topleft)

    def _drawdesignation(self, surface, location):
        self._colortint(surface, (85, 85, 0), location)

    def _drawground(self, surface, ground, location):
        self._colortile(surface, Entity('ground'),
                        ground.color, ground.varient, location)
        
        if ground.designated:
            self._drawdesignation(surface, location)

    def _drawwall(self, surface, wall, location):
        self._colorfill(surface, wall.color, location)
        
        if wall.designated:
            self._drawdesignation(surface, location)

    def _drawtrunk(self, surface, trunk, location):
        image = self.graphics[trunk][0].copy()
        image.fill(trunk.color, special_flags=BLEND_ADD)
        image.fill((48,48,48), special_flags=BLEND_ADD)

        exterior = self.graphics[trunk][1].copy()
        exterior.fill(trunk.color, special_flags=BLEND_ADD)
        image.blit(exterior, (0,0))

        rings = self.graphics[trunk][2].copy()
        rings.fill(trunk.color, special_flags=BLEND_ADD)
        image.blit(rings, (0,0))
        
        surface.blit(image, self._tilecoordinates(location))

    def _drawtile(self, surface, tile, location):
        if tile.kind == 'tree-trunk':
            self._drawtrunk(surface, tile, location)
        else:
            self._colortile(surface, tile, tile.color, tile.varient, location)

    def _drawfarground(self, surface, ground, location):
        self._colortile(surface, Entity('air'), ground.color, 0, location)

    def _drawair(self, surface, location):
        self._colorfill(surface, (0, 85, 85), location)

    def _drawlocation(self, surface, location):
        x, y, z = location
        tile = self.game.world.space[location]

        if tile is None:
            return

        if tile.is_passable():
            locationbelow = x, y, z - 1
            below = self.game.world.space[locationbelow]
            if below.is_passable():
                locationfarbelow = x, y, z - 2
                farbelow = self.game.world.space[locationfarbelow]
                if farbelow.is_passable():
                    self._drawair(surface, locationfarbelow)
                else:
                    self._drawfarground(surface, farbelow,
                                        locationfarbelow)
            elif below.kind:
                self._drawfarground(surface, below, locationbelow)
            else:
                self._drawground(surface, below, locationbelow)

        elif tile.kind is not None:
            self._drawtile(surface, tile, location)
        else:
            if tile.revealed:
                self._drawwall(surface, tile, location)
            elif tile.designated:
                self._drawdesignation(surface, location)

    def _getbackground(self, size):
        background = Surface(size, flags=SRCALPHA)
        background.fill((0,0,0))

        xs, ys = [range(self.offset[i], self.offset[i] + self.dimensions[i])
                  for i in range(2)]
        for x in xs:
            for y in ys:
                self._drawlocation(background, (x, y, self.level))

        return background

    def resize(self, size):
        tilecount = self._screentile(size)
        self.dimensions = tilecount

        if not self.offset:
            self.offset = tuple([r/2 if r > 0 else 0 for r in
                                 [self.game.dimensions[i] - self.dimensions[i]
                                  for i in range(2)]])

        self.background = self._getbackground(size)

    def _mouse(self, pos = None):
        if pos is None:
            pos = mouse.get_pos()
        else:
            mouse.set_pos(pos)
        tile = self._screentile(pos)
        if not (0 <= tile[0] < self.dimensions[0] and
                0 <= tile[1] < self.dimensions[1]):
            tile = None
        return pos, tile

    @staticmethod
    def _clamp(value, limits):
        if value < limits[0]:
            return limits[0], value - limits[0]
        elif value > limits[1]:
            return limits[1], value - limits[1]
        else:
            return value, 0

    def _scroll(self, axis, amount):
        size = self.zoom.width if axis == 0 else self.zoom.height

        pos, tile = self._mouse()

        while (tile is not None and
               ((amount < 0 and
                 tile[axis] + self.offset[axis] >
                 self.game.dimensions[axis] - self.dimensions[axis]/2) or
                (amount > 0 and
                 tile[axis] + self.offset[axis] <
                 self.dimensions[axis]/2))):
            pos, tile = self._mouse(tuple([pos[i] + (size * amount/abs(amount)
                                                     if i == axis else 0)
                                           for i in range(2)]))
            amount -= amount/abs(amount)

        dest, remainder = self._clamp(
            self.offset[axis] + amount,
            (0, self.game.dimensions[axis] - self.dimensions[axis]))
        
        self.offset = tuple([dest if i == axis else self.offset[i]
                             for i in range(2)])

        while tile is not None and ((remainder < 0 and 0 < tile[axis]) or
               (remainder > 0 and tile[axis] < self.dimensions[axis]-1)):
            pos, tile = self._mouse(tuple([pos[i] +
                                           (size * remainder/abs(remainder)
                                            if i == axis else 0)
                                           for i in range(2)]))
            remainder -= remainder/abs(remainder)

    def handle(self, e):
        if e.type == KEYDOWN:
            pressed = key.get_pressed()
            shifted = pressed[K_LSHIFT] or pressed[K_RSHIFT]
            scroll = 10 if shifted else 1
            
            if e.key == K_ESCAPE:
                self.game.done = True
                
            elif e.key == K_SPACE:
                self.game.paused = not self.game.paused
                
            elif e.key == K_UP:
                self._scroll(1, -scroll)                                        
                self.background = None
                
            elif e.key == K_DOWN:
                self._scroll(1, scroll)
                self.background = None
                
            elif e.key == K_LEFT:
                self._scroll(0, -scroll)
                self.background = None
                
            elif e.key == K_RIGHT:
                self._scroll(0, scroll)
                self.background = None
                    
            elif e.unicode == '>':
                self.level = max(self.level-1, 0)
                self.background = None
                
            elif e.unicode == '<':
                self.level = min(self.level+1, self.game.dimensions[2])
                self.background = None
                    
    def draw(self, surface):
        if not self.background:
            self.resize(surface.get_size())
            surface.blit(self.background, (0,0))

        self.sprites.clear(surface, self.background)
        self.sprites.draw(surface)
