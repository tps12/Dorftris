from pygame import draw, event, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import *
from pygame.sprite import *

from data import Barrel, Beverage, Corpse, Entity, Stockpile
from details import CreatureDetails
from glyphs import GlyphGraphics

class EntitySprite(DirtySprite):
    def __init__(self, visible, position, graphics, entity, *args, **kwargs):
        DirtySprite.__init__(self, *args, **kwargs)
        self.entity = entity
        
        self._position = position
        self._visible = visible

        self.image = graphics[self.entity][0].copy()
        self.image.fill(self.entity.color, special_flags=BLEND_ADD)
        self.rect = self.image.get_rect().move(
            self._position(self.entity.location))
        self.layer = 0
        
    def update(self):
        if self._visible(self.entity.location):
            pos = self._position(self.entity.location)
            if self.rect.topleft != pos:
                self.rect.topleft = pos
                self.dirty = True
        else:
            self.kill()

class SelectionSprite(DirtySprite):
    def __init__(self, visible, position, lines, zoom, selection, *args, **kwargs):
        DirtySprite.__init__(self, *args, **kwargs)
        self._visible = visible
        self._position = position
        self._lines = lines
        self._zoom = zoom
        self.selection = selection
        self._ps = []

        self.layer = 1

    def update(self):
        ps = [self._position(loc)
              for loc in self.selection
              if self._visible(loc)]
        
        if not ps:
            self.kill()
            return
            
        if len(self._ps) == len(ps) and all([self._ps[i] == ps[i]
                                             for i in range(len(ps))]):
            return

        self._ps = ps
        pos = [min([p[i] for p in self._ps]) for i in range(2)]
        adj = self._zoom.width+self._zoom.height/3, self._zoom.height + 1
        size = [max([p[i] for p in self._ps]) - pos[i] + adj[i]
                for i in range(2)]
        self.image = Surface(size, flags=SRCALPHA)
        lines = []
        internal = []
        for p in self._ps:
            for edge in [sorted([[v[j][i] + p[i] - pos[i]
                                  for i in range(2)]
                                 for j in range(2)])
                         for v in self._lines()]:
                if edge in lines:
                    internal.append(edge)
                else:
                    lines.append(edge)
        for line in lines:
            if line not in internal:
                draw.line(self.image, (255,0,0), line[0], line[1])
        self.rect = self.image.get_rect().move((pos[0]-self._zoom.height/3,
                                                pos[1]))
        self.dirty = 1

class ScreenSprites(LayeredDirty):
    def __init__(self, visible, position, *args, **kwargs):
        LayeredDirty.__init__(self, *args, **kwargs)
        self._visible = visible
        self._position = position
        self._entities = {}

    def addspritefor(self, entity, graphics):
        sprite = EntitySprite(self._visible, self._position, graphics, entity)
        self.add(sprite)
        self._entities[entity] = sprite

    def remove_internal(self, sprite):
        LayeredDirty.remove_internal(self, sprite)
        if isinstance(sprite, EntitySprite):
            del self._entities[sprite.entity]

    def hasspritefor(self, entity):
        return entity in self._entities

class Playfield(object):
    def __init__(self, game, font, zoom):
        self.game = game

        self.zoom = zoom

        self.sprites = ScreenSprites(self.visible, self.tilecoordinates)

        self.scale(font)

        self.cursor = None
        self.selection = []

        self._selectionsprite = SelectionSprite(self.visible,
                                                self.tilecoordinates,
                                                self.hexlines,
                                                self.zoom,
                                                self.selection)

        self.offset = None
        
        self.level = 64

    def scale(self, font):
        self.font = font
        self.graphics = GlyphGraphics(max(self.zoom.width, self.zoom.height))
        
        self.sprites.empty()
        
        self.background = None

    def visible(self, location):
        return location and all([
            self.offset[i] <= location[i] < self.offset[i] + self.dimensions[i]
            for i in range(2)]) and location[2] == self.level

    def tilecoordinates(self, location):
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

    def _absolutetile(self, coordinates):
        relative = self._screentile(coordinates)
        absolute = [relative[i] + self.offset[i]
                    for i in range(2)] + [self.level]
        return absolute if all([0 <= absolute[i] < self.game.dimensions[i]
                                for i in range(2)]) else None

    def _hex(self):
        return [(self.zoom.height/3,self.zoom.height),
                (0,self.zoom.height/2),
                (self.zoom.height/3,0),
                (self.zoom.width,0),
                (self.zoom.width+self.zoom.height/3,self.zoom.height/2),
                (self.zoom.width,self.zoom.height)]

    def hexlines(self):
        vs = self._hex()
        return [(vs[i-1], vs[i]) for i in range(len(vs))]

    def _colortile(self, surface, entity, color, varient, location):
        image = self.graphics[entity][varient].copy()
        image.fill(color, special_flags=BLEND_ADD)
        surface.blit(image, self.tilecoordinates(location))

    def _tilerect(self, location):
        x, y = self.tilecoordinates(location)
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
        
        surface.blit(image, self.tilecoordinates(location))

    def _drawtile(self, surface, tile, location):
        if tile.kind == 'tree-trunk':
            self._drawtrunk(surface, tile, location)
        else:
            self._colortile(surface, tile, tile.color, tile.varient, location)

    def _drawfarground(self, surface, ground, location):
        self._colortile(surface, Entity('air'), ground.color, 0, location)

    def _drawair(self, surface, location):
        self._colorfill(surface, (0, 85, 85), location)

    def _drawopen(self, surface, tile, location):
        x, y, z = location
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

    def _processlocation(self, surface, location, process):
        x, y, z = location
        tile = self.game.world.space[location]

        if tile is None:
            return

        process(surface, tile, location)

    def _drawtilebackground(self, surface, tile, location):
        if tile.is_passable():
            self._drawopen(surface, tile, location)
        elif tile.kind is not None:
            self._drawtile(surface, tile, location)
        else:
            if tile.revealed:
                self._drawwall(surface, tile, location)
            elif tile.designated:
                self._drawdesignation(surface, location)

        self._addtilesprites(tile)

    def _addtilesprites(self, tile):
        if tile.creatures:
            entity = tile.creatures[-1]
            if not self.sprites.hasspritefor(entity):
                self.sprites.addspritefor(entity, self.graphics)
        if tile.items:
            entity = tile.items[-1]
            if not self.sprites.hasspritefor(entity):
                self.sprites.addspritefor(entity, self.graphics)
        
    def _scanbackground(self, background, tileprocess):
        xs, ys = [range(self.offset[i], self.offset[i] + self.dimensions[i])
                  for i in range(2)]
        for x in xs:
            for y in ys:
                self._processlocation(background,
                                      (x, y, self.level),
                                      tileprocess)

    def resize(self, size):
        tilecount = self._screentile(size)
        self.dimensions = tilecount

        if not self.offset:
            self.offset = tuple([r/2 if r > 0 else 0 for r in
                                 [self.game.dimensions[i] - self.dimensions[i]
                                  for i in range(2)]])

        self._makebackground(size)

    def _makebackground(self, size):
        self.background = Surface(size, flags=SRCALPHA)
        self.background.fill((0,0,0))
        self._scanbackground(self.background, self._drawtilebackground)

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

        self.background = None

    def _select(self, tile):
        if tile:
            if tile in self._selectionsprite.selection:
                self._selectionsprite.selection.remove(tile)
            else:
                self._selectionsprite.selection.append(tile)

    def _zscroll(self, dz):
        level = max(0, min(self.game.dimensions[2], self.level + dz))
        if self.level != level:
            self.level = level
            self.background = None
            self.sprites.empty()

    def handle(self, e):
        if e.type == KEYDOWN:
            pressed = key.get_pressed()
            shifted = pressed[K_LSHIFT] or pressed[K_RSHIFT]
            scroll = 10 if shifted else 1
            
            if e.key == K_UP:
                self._scroll(1, -scroll)                                        
                return True
                
            elif e.key == K_DOWN:
                self._scroll(1, scroll)
                return True
                
            elif e.key == K_LEFT:
                self._scroll(0, -scroll)
                return True
                
            elif e.key == K_RIGHT:
                self._scroll(0, scroll)
                return True
                    
            elif e.unicode == '>':
                self._zscroll(-1)
                return True
                
            elif e.unicode == '<':
                self._zscroll(1)
                return True

        elif e.type == MOUSEBUTTONUP and e.button == 1:
            self._select(self._absolutetile(mouse.get_pos()))
            return True
            
        return False
                    
    def draw(self, surface):
        if (self._selectionsprite.selection and
            self._selectionsprite not in self.sprites):
            self.sprites.add(self._selectionsprite)

        self.sprites.update()

        if self.background:
            self._scanbackground(None, lambda s,t,l: self._addtilesprites(t))
        else:
            self._makebackground(surface.get_size())
            surface.blit(self.background, (0,0))

        self.sprites.clear(surface, self.background)
        self.sprites.draw(surface)
