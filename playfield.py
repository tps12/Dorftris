from random import choice

from pygame import draw, event, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import *
from pygame.sprite import *

from data import Barrel, Beverage, Corpse, Stockpile
from details import CreatureDetails
from game import *
from glyphs import Air, GlyphGraphics
from listener import PlayfieldListener
from space import *

class StockpileSprite(DirtySprite):
    def __init__(self, visible, position, graphics, component, *args, **kwargs):
        DirtySprite.__init__(self, *args, **kwargs)
        self.component = component
        
        self._position = position
        self._visible = visible

        self.image = graphics[self.component][0].copy()
        self.image.fill(self.component.color, special_flags=BLEND_ADD)
        self.rect = self.image.get_rect().move(
            self._position(self.component.location))
        self.layer = 0
        
    def update(self):
        if self._visible(self.component.location):
            pos = self._position(self.component.location)
            if self.rect.topleft != pos:
                self.rect.topleft = pos
                self.dirty = True
        else:
            self.kill()

class EntitySprite(DirtySprite):
    def __init__(self, visible, position, graphics, entity, *args, **kwargs):
        DirtySprite.__init__(self, *args, **kwargs)
        self.entity = entity

        self._graphics = graphics
        self._position = position
        self._visible = visible

        self._setimage()
        self.rect = self.image.get_rect().move(
            self._position(self.entity.location))
        self.layer = 1

    def _setimage(self):
        self.image = (choice(self._graphics[self.entity])
                      if self.entity.volatile
                      else self._graphics[self.entity][0]).copy()
        self.image.fill(self.entity.color, special_flags=BLEND_ADD)
        
    def update(self):
        if self._visible(self.entity.location):
            if self.entity.volatile:
                self._setimage()
                self.dirty = True
            
            pos = self._position(self.entity.location)
            if self.rect.topleft != pos:
                self.rect.topleft = pos
                self.dirty = True
        else:
            self.kill()

class EntitySelectionSprite(DirtySprite):
    def __init__(self, removed, entity, sprite, prefs, *args, **kwargs):
        DirtySprite.__init__(self, *args, **kwargs)
        self._removed = removed
        self.selection = entity
        self._selection = sprite

        self.image = Surface(self._selection.image.get_size(), flags=SRCALPHA)
        draw.rect(self.image, prefs.selectioncolor, self.image.get_rect(), 1)
        self.rect = self._selection.rect
        
        self.layer = 2

    def update(self):
        if len(self._selection.groups()):
            self.rect.topleft = self._selection.rect.topleft
        else:
            self.kill()

    def kill(self):
        Sprite.kill(self)
        self._removed()

class RegionOutlineSprite(DirtySprite):
    def __init__(self, visible, position, lines, zoom, color, region, *args, **kwargs):
        DirtySprite.__init__(self, *args, **kwargs)
        self._visible = visible
        self._position = position
        self._lines = lines
        self._zoom = zoom
        self._color = color
        self._region = region
        self._ps = []

    def update(self):
        ps = [self._position(loc)
              for loc in self._region]
                    
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
        for p in self._ps:
            for edge in [sorted([[v[j][i] + p[i] - pos[i]
                                  for i in range(2)]
                                 for j in range(2)])
                         for v in self._lines()]:
                if edge in lines:
                    lines.remove(edge)
                else:
                    lines.append(edge)
        for line in lines:
            draw.line(self.image, self._color, line[0], line[1])
        self.rect = self.image.get_rect().move((pos[0]-self._zoom.height/3,
                                                pos[1]))
        self.dirty = 1
        
class TileSelectionSprite(RegionOutlineSprite):
    def __init__(self, visible, position, lines, zoom, selection, *args, **kwargs):
        RegionOutlineSprite.__init__(self, visible, position, lines,
                                     zoom, zoom.selectioncolor,
                                     selection, *args, **kwargs)
        self.selection = selection

        self.layer = 2

class ScreenSprites(LayeredDirty):
    def __init__(self, visible, position, lines, prefs, *args, **kwargs):
        LayeredDirty.__init__(self, *args, **kwargs)
        self._visible = visible
        self._position = position
        self._lines = lines
        self._prefs = prefs
        self.entities = {}
        self._selectionsprite = None
        self.set_clip(None)

    def setselection(self, selection):
        if self._selectionsprite and self._selectionsprite.selection == selection:
            return

        if self._selectionsprite:
            self._selectionsprite.kill()

        if selection:
            if isinstance(selection, Stockpile):
                selection = [c.location for c in selection.components]
                if any([self._visible(location) for location in selection]):
                    sprite = TileSelectionSprite(self._visible,
                                                 self._position,
                                                 self._lines,
                                                 self._prefs,
                                                 selection)
                else:
                    return
            elif isinstance(selection, Entity):
                if selection in self.entities:
                    sprite = EntitySelectionSprite(lambda: None,
                                                   selection,
                                                   self.entities[selection],
                                                   self._prefs)
                else:
                    return
            else:
                if isinstance(selection, tuple):
                    selection = [selection]
                if any([self._visible(location) for location in selection]):
                    sprite = TileSelectionSprite(self._visible,
                                                 self._position,
                                                 self._lines,
                                                 self._prefs,
                                                 selection)
                else:
                    return
                
            self._selectionsprite = sprite
            self.add(self._selectionsprite)

    def addspritefor(self, entity, graphics):
        sprite = EntitySprite(self._visible, self._position, graphics, entity)
        self.add(sprite)
        self.entities[entity] = sprite

    def remove_internal(self, sprite):
        LayeredDirty.remove_internal(self, sprite)
        if isinstance(sprite, EntitySprite):
            del self.entities[sprite.entity]
        if sprite is self._selectionsprite:
            self._selectionsprite = None

    def hasspritefor(self, entity):
        return entity in self.entities

class Playfield(object):
    def __init__(self, game, player, font, zoom):
        self.game = game
        self.game.world.addsoundlistener(PlayfieldListener(self))

        self.player = player

        self.zoom = zoom

        self.sprites = ScreenSprites(self.visible,
                                     self.tilecoordinates,
                                     self.hexlines,
                                     self.zoom)

        self.selection = None

        self.scale(font)

        self._dragging = False
        self.cursor = None

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
        return x, (py - self.zoom.height +
                   (x&1)*self.zoom.height/2) / self.zoom.height

    def _absolutetile(self, coordinates):
        relative = self._screentile(coordinates)
        absolute = [relative[i] + self.offset[i]
                    for i in range(2)] + [self.level]
        return tuple(absolute) if all(
            [0 <= absolute[i] < self.game.dimensions[i]
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
        rect = self._tilerect(location)
        if surface.get_rect().contains(rect):
            image = surface.subsurface(rect)
            gfxdraw.filled_polygon(image, self._hex(), color)

    def _colortint(self, surface, color, location, alpha = None):
        rect = self._tilerect(location)
        image = Surface(rect.size, flags=SRCALPHA)
        gfxdraw.filled_polygon(image, self._hex(), (0, 0, 0, alpha or 128))
        image.fill(color, special_flags=BLEND_ADD)
        surface.blit(image, rect.topleft)

    def _drawdesignation(self, surface, location):
        self._colortint(surface, (85, 85, 0), location)

    def _drawground(self, surface, space, ground, location):
        self._colortile(surface, ground,
                        ground.color, space.varient, location)

        if space.color:
            self._colortint(surface, space.color, location)
        
        if ground.designation:
            self._drawdesignation(surface, location)

    def _drawliquid(self, surface, tile, location):
        self._colorfill(surface, tile.liquid.color, location)

    def _drawwall(self, surface, wall, location):
        self._colorfill(surface, wall.color, location)
        
        if wall.designation:
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
        if isinstance(tile, TreeTrunk):
            self._drawtrunk(surface, tile, location)
        else:
            self._colortile(surface, tile, tile.color, tile.varient, location)

    def _drawfarground(self, surface, space, ground, location):
        self._colortile(surface, Air, space.color or ground.color, 0, location)

    def _drawair(self, surface, location):
        self._colorfill(surface, (0, 85, 85), location)

    def _drawopen(self, surface, tile, location):
        x, y, z = location
        while z and isinstance(tile, Empty):
            z -= 1
            tile = self.game.world.space[(x,y,z)]
        else:
            self._drawtilefield(surface, tile, (x,y,z))
            alpha = min(255, 192 + 8 * (location[2]-z))
            self._colortint(surface, (0,0,0), location, alpha)
            return

        self._drawair(surface, location)
            
    def _drawfloor(self, surface, tile, location):
        x, y, z = location
        locationbelow = x, y, z - 1
        below = self.game.world.space[locationbelow]
        self._drawground(surface, tile, below, location)

    def _processlocation(self, surface, location, process):
        x, y, z = location
        tile = self.game.world.space[location]

        if tile is None:
            return

        process(surface, tile, location)

    def _drawtilefield(self, surface, tile, location):
        if tile.liquid:
            self._drawliquid(surface, tile, location)
        elif isinstance(tile, Empty):
            self._drawopen(surface, tile, location)
        elif isinstance(tile, Floor):
            self._drawfloor(surface, tile, location)
        elif not isinstance(tile, Earth):
            self._drawtile(surface, tile, location)
        else:
            if tile.revealed:
                self._drawwall(surface, tile, location)
            elif tile.designation:
                self._drawdesignation(surface, location)

    def _drawtilebackground(self, surface, tile, location):
        self._drawtilefield(surface, tile, location)
        
        self._addtilesprites(tile, location)
            
    def _addtilesprites(self, tile, location):
        if tile.creatures:
            entity = tile.creatures[-1]
            if not self.sprites.hasspritefor(entity):
                self.sprites.addspritefor(entity, self.graphics)
        if tile.items:
            entity = tile.items[-1]
            if not self.sprites.hasspritefor(entity):
                self.sprites.addspritefor(entity, self.graphics)
        if isinstance(tile, Floor):
            if tile.furnishing and not self.sprites.hasspritefor(tile.furnishing):
                self.sprites.addspritefor(tile.furnishing, self.graphics)
            if tile.stockpiles and self.player in tile.stockpiles:
                for component in tile.stockpiles[self.player].components:
                    if not self.sprites.hasspritefor(component):
                        self.sprites.addspritefor(component, self.graphics)
        
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

    def _zscroll(self, dz):
        level = max(0, min(self.game.dimensions[2], self.level + dz))
        if self.level != level:
            self.level = level
            self.background = None
            self.sprites.empty()

    def _nextentity(self, tile, entity):
        found = entity is None
        if hasattr(tile, 'furnishing') and tile.furnishing:
            if found:
                return tile.furnishing
            elif entity == tile.furnishing:
                found = True
        elif (hasattr(tile, 'stockpiles') and tile.stockpiles and
              self.player in tile.stockpiles):
            if found:
                return tile.stockpiles[self.player]
            elif entity == tile.stockpiles[self.player]:
                found = True
        for creature in tile.creatures:
            if found:
                return creature
            elif creature == entity:
                found = True
        for item in tile.items:
            if found:
                return item
            elif item == entity:
                found = True
        if found:
            return None

        raise ValueError

    def _select(self, location):
        if self.selection is None:
            self.selection = location
        elif self.selection == location:
            try:
                self.selection = self._nextentity(
                    self.game.world.space[location], None)
            except ValueError:
                self.selection = None
        elif isinstance(self.selection, Stockpile):
            if location in [c.location for c in self.selection.components]:
                self.selection = self._nextentity(
                    self.game.world.space[location], self.selection)
        elif isinstance(self.selection, Entity):
            if self.selection.location == location:
                self.selection = self._nextentity(
                    self.game.world.space[location], self.selection)
            else:
                self.selection = location
        else:
            self.selection = location

    def _expandselection(self, location):
        if self.selection is None or isinstance(self.selection, Entity):
            return

        if isinstance(self.selection, tuple):
            locations = [self.selection]
        else:
            locations = self.selection

        if location not in locations and any([a + (self.level,) in locations
                                              for a in
                                              self.game.world.space.pathing.
                                              adjacent_xy(location[0:2])]):
            self.selection = locations + [location]

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

            elif e.key == K_TAB:
                self._select(self._absolutetile(mouse.get_pos()))
                return True

        elif (e.type == MOUSEBUTTONDOWN and
              self.background and
              self.background.get_rect().collidepoint(e.pos) and
              e.button == 1):
            self._select(self._absolutetile(mouse.get_pos()))
            return True
        
        elif (e.type == MOUSEBUTTONUP and
              self.background and
              self.background.get_rect().collidepoint(e.pos) and
              e.button == 1):
            self._dragging = False
            return True

        elif (e.type == MOUSEMOTION and
              self.background and
              self.background.get_rect().collidepoint(e.pos) and
              1 in e.buttons):
            self._expandselection(self._absolutetile(mouse.get_pos()))
            self._dragging = True
            
        return False

    def draw(self, surface):
        self.cursor = self._absolutetile(mouse.get_pos())
        
        self.sprites.setselection(self.selection)

        self.sprites.update()

        if self.background and not self.game.world.space.changed:
            self._scanbackground(None, lambda s,t,l: self._addtilesprites(t,l))
        else:
            self._makebackground(surface.get_size())
            surface.blit(self.background, (0,0))
            self.sprites.repaint_rect(self.background.get_rect())
            self.game.world.space.changed = False

        self.sprites.clear(surface, self.background)
        self.sprites.draw(surface)
