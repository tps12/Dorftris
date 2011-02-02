from pygame import draw, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Creature, Stockpile, Wine
from details import CreatureDetails
from game import Earth, Empty
from text import TextRenderer

class SelectionInfo(object):
    def __init__(self, playfield, font, prefs):
        self._playfield = playfield
        self._prefs = prefs
        self._cursor = None
        self._entity = None
        self._tiles = []
        
        self._selectionrect = None
        self._details = None
        
        self.scale(font)

    def _entitydescription(self, entity):
        return (entity.namecard()
                if isinstance(entity, Creature)
                else entity.description())

    def _entitydetails(self, entity):
        return (CreatureDetails(entity,
                                self._playfield, self._font, self._prefs)
                if isinstance(entity, Creature)
                else self)

    def _describeentities(self, surface, entities, dy):
        for entity in entities:
            image = self._renderer.render(self._entitydescription(entity),
                                          (255,255,255))
            surface.blit(image, (0, dy))
            if entity is self._entity:
                draw.rect(surface, self._prefs.selectioncolor,
                          Rect((0,dy), image.get_size()), 1)
                self._details = lambda: self._entitydetails(self._entity)
            dy += image.get_height()
        return dy

    def _describetile(self, surface, location, dy):
        x, y, z = location
        tile = self._playfield.game.world.space[location]

        if isinstance(tile, Empty):
            below = self._playfield.game.world.space[(x,y,z-1)]
            if not isinstance(below, Earth):
                s = _(u'open space')
            else:
                s = below.description
                covering = tile.description
                if covering:
                    s = ' '.join([covering, s])
        elif tile.revealed:
            s = tile.description
        else:
            s = _(u'unknown')

        color = ((255,255,255)
                  if location == self._cursor else self._prefs.selectioncolor)
        image = self._renderer.render(s.capitalize(), color)
        surface.blit(image, (0,dy))
        if location == self._cursor and location in self._tiles:
            draw.rect(surface, self._prefs.selectioncolor,
                      image.get_rect().move(0,dy), 1)
        dy += image.get_height()

        dy = self._describeentities(surface, tile.creatures, dy)
        dy = self._describeentities(surface, tile.items, dy)

        return dy

    def _drawselectedtile(self, dy):
        if len(self._tiles) == 1 and self._tiles[0] != self._cursor:
            dy = self._describetile(self._background, self._tiles[0], dy)
        return dy

    def _drawselectedentity(self, dy):
        if (self._entity and self._entity.location != self._cursor and
            (not self._tiles or self._entity.location not in self._tiles)):
            image = self._renderer.render(
                self._entitydescription(self._entity),
                self._prefs.selectioncolor)
            self._background.blit(image, (0, dy))

            self._selectionrect = image.get_rect().move(0,dy)
            self._details = lambda: self._entitydetails(self._entity)

            dy += image.get_height()
        return dy

    def _addbutton(self, surface, text, click, dy):
        button = Button(self._font, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]

    def _definetilebuttons(self, dy):
        self._buttons = []
        if self._tiles:
            if self._allclearfloor(self._tiles):
                dy = self._addbutton(self._background,
                                     _(u'Dig down'),
                                     self._designate,
                                     dy)
                dy = self._addbutton(self._background,
                                     _(u'Make stockpile'),
                                     self._stockpile,
                                     dy)
            elif self._allsolidwalls(self._tiles):
                dy = self._addbutton(self._background,
                                     _(u'Dig out'),
                                     self._designate,
                                     dy)
        return dy

    def _allclearfloor(self, tiles):
        return all([isinstance(self._playfield.game.world.space[(x,y,z)], Empty) and
                    isinstance(self._playfield.game.world.space[(x,y,z-1)], Earth)
                    for (x,y,z) in tiles])

    def _allsolidwalls(self, tiles):
        return all([isinstance(self._playfield.game.world.space[tile], Earth)
                    for tile in tiles])

    def _clearselectedtiles(self):
        self._playfield.deselecttiles()

    def _stockpile(self):
        self._playfield.game.world.addstockpile(Stockpile(self._tiles,
                                                          [Wine.stocktype]))
        self._clearselectedtiles()

    def _designatetile(self, location):
        x, y, z = location
        tile = self._playfield.game.world.space[(x,y,z)]
        if isinstance(tile, Empty):
            floor = self._playfield.game.world.space[(x,y,z-1)]
            if isinstance(floor, Earth):
                self._playfield.game.world.designatefordigging((x,y,z-1))
        elif isinstance(tile, Earth):
            self._playfield.game.world.designatefordigging((x,y,z))

    def _designate(self):
        for location in self._tiles:
            self._designatetile(location)
        
        self._clearselectedtiles()
        
    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])

        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        self._selectionrect = self._detail = None

        dy = 0
        if self._cursor:
            dy = self._describetile(self._background, self._cursor, dy)

        dy = self._drawselectedtile(dy)
        dy = self._drawselectedentity(dy)
        dy = self._definetilebuttons(dy)
    
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_RETURN and self._details:
                return True, True, self._details()
        
        elif (e.type == MOUSEBUTTONDOWN and e.button == 1):
            if (self._selectionrect and
                self._selectionrect.collidepoint(e.pos)):
                return True, True, self._details()
            for button in self._buttons:
                if button.handle(e):
                    return True, False, self
        
        return False, False, self

    def draw(self, surface):
        cursor = self._playfield.cursor
        if self._cursor != cursor:
            self._cursor = cursor
            self._background = None

        entity = self._playfield.selectedentity
        if self._entity != entity:
            self._entity = entity
            self._background = None

        tiles = [t for t in self._playfield.selectedtiles]
        if (len(self._tiles) != len(tiles) or
            any([self._tiles[i] != tiles[i] for i in range(len(tiles))])):
            self._tiles = tiles
            self._background = None
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
