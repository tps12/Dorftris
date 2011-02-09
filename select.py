from pygame import draw, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Creature, Stockpile, Wine
from details import CreatureDetails
from furnish import FurnishingSelect
from game import Earth, Empty
from text import TextRenderer

class SelectionInfo(object):
    def __init__(self, playfield, font, prefs):
        self._playfield = playfield
        self._prefs = prefs

        self._cursor = None
        
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

        image = self._renderer.render(s.capitalize(), (255,255,255))
        surface.blit(image, (0,dy))
        dy += image.get_height()

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
        handled = False
        
##        if e.type == KEYDOWN:
##            if e.key == K_RETURN and self._details:
##                return True, True, self._details()
##        
##        elif (e.type == MOUSEBUTTONDOWN and e.button == 1):
##            if (self._selectionrect and
##                self._selectionrect.collidepoint(e.pos)):
##                return True, True, self._details()
##            for button in self._buttons:
##                if button.handle(e):
##                    handled = True
##
##        if self._selectfurnishing is not None:
##            location = self._selectfurnishing
##            self._selectfurnishing = None
##            return True, True, FurnishingSelect(self._playfield.player,
##                                                location,
##                                                self._font,
##                                                self._prefs)
        
        return handled, False, self

    def draw(self, surface):
        cursor = self._playfield.cursor
        if self._cursor != cursor:
            self._cursor = cursor
            self._background = None
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
