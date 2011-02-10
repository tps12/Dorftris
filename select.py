from pygame import draw, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Creature, Item, Stockpile
from details import CreatureDetails
from furnish import FurnishingSelect
from game import Earth, Empty
from item import ItemDetails
from region import RegionDetails
from text import TextRenderer

class SelectionInfo(object):
    def __init__(self, playfield, font, prefs,
                 pushchild, popchild,
                 pushscreen, popscreen):
        self._playfield = playfield
        self._prefs = prefs
        self._pushchild = pushchild
        self._popchild = popchild
        self._pushscreen = pushscreen
        self._popscreen = popscreen

        self._cursor = None
        
        self.scale(font)

    def _entitydescription(self, entity):
        return (entity.namecard()
                if isinstance(entity, Creature)
                else entity.description())

    def _describeentities(self, surface, entities, dy):
        for entity in entities:
            image = self._renderer.render(self._entitydescription(entity),
                                          (255,255,255))
            surface.blit(image, (0, dy))
            dy += image.get_height()
        return dy

    def _description(self, location):
        x, y, z = location
        tile = self._playfield.game.world.space[location]

        if isinstance(tile, Empty):
            below = self._playfield.game.world.space[(x,y,z-1)]
            if not isinstance(below, Earth):
                s = _(u'open space')
            elif tile.furnishing:
                s = tile.furnishing.description()
            elif tile.stockpiles and self._playfield.player in tile.stockpiles:
                s = tile.stockpiles[self._playfield.player].description()
            else:
                s = below.description
                covering = tile.description
                if covering:
                    s = ' '.join([covering, s])
        elif tile.revealed:
            s = tile.description
        else:
            s = _(u'unknown')

        return s

    def _describetile(self, surface, location, dy):
        s = self._description(location)

        image = self._renderer.render(s.capitalize(), (255,255,255))
        surface.blit(image, (0,dy))
        dy += image.get_height()

        tile = self._playfield.game.world.space[location]
        dy = self._describeentities(surface, tile.creatures, dy)
        dy = self._describeentities(surface, tile.items, dy)

        return dy
        
    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])
        
        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        dy = self._describetile(self._background, self._cursor, 0)
    
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        return False

    def draw(self, surface):
        if self._playfield.selection:
            if isinstance(self._playfield.selection, Creature):
                self._pushchild(CreatureDetails(self._playfield.selection,
                                                self._playfield,
                                                self._font,
                                                self._prefs,
                                                self._popchild,
                                                self._pushscreen,
                                                self._popscreen))
            elif isinstance(self._playfield.selection, Item):
                self._pushchild(ItemDetails(self._playfield.selection,
                                            self._playfield,
                                            self._font,
                                            self._prefs,
                                            self._popchild,
                                            self._pushscreen,
                                            self._popscreen))
            elif isinstance(self._playfield.selection, Stockpile):
                pass
            else:
                region = self._playfield.selection
                region = [region] if isinstance(region, tuple) else region
                self._pushchild(RegionDetails(region,
                                              self._playfield,
                                              self._font,
                                              self._prefs,
                                              self._description,
                                              self._pushchild,
                                              self._popchild,
                                              self._pushscreen,
                                              self._popscreen))
            self._background = None
            return

        cursor = self._playfield.cursor
        if self._cursor != cursor:
            self._cursor = cursor
            self._background = None
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
