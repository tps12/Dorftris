from pygame import draw, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from data import Creature
from details import CreatureDetails
from text import TextRenderer

class InfoView(object):
    def __init__(self, playfield, font):
        self._playfield = playfield
        self._cursor = None
        self._entity = None
        self._tiles = []
        
        self._selectionrect = None
        self._details = None
        
        self.scale(font)

    @property
    def width(self):
        return self._font.size('-' * 32)[0]

    def _entitydescription(self, entity):
        return (entity.namecard()
                if isinstance(entity, Creature)
                else entity.description())

    def _entitydetails(self, entity):
        return (CreatureDetails(entity, self._font)
                if isinstance(entity, Creature)
                else self)

    def _describeentities(self, surface, entities, dy):
        for entity in entities:
            image = self._renderer.render(self._entitydescription(entity),
                                          (255,255,255))
            surface.blit(image, (0, dy))
            if entity is self._entity:
                draw.rect(surface, (255,0,0), Rect((0,dy), image.get_size()), 1)
                self._details = lambda: self._entitydetails(self._entity)
            dy += image.get_height()
        return dy

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
        if location in self._tiles:
            draw.rect(surface, (255,0,0), image.get_rect(), 1)
        dy = image.get_height()

        dy = self._describeentities(surface, tile.creatures, dy)
        dy = self._describeentities(surface, tile.items, dy)

        return dy

    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])

        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        self._selectionrect = self._detail = None

        if self._cursor:
            dy = self._describetile(self._background, self._cursor)
        else:
            dy = 0

        if self._entity and self._entity.location != self._cursor:
            image = self._renderer.render(
                self._entitydescription(self._entity), (255,0,0))
            self._background.blit(image, (0, dy))

            self._selectionrect = image.get_rect().move(0,dy)
            self._details = lambda: self._entitydetails(self._entity)
    
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_RETURN and self._details:
                return True, self._details()
        
        elif (e.type == MOUSEBUTTONDOWN and
            self._selectionrect and
            self._selectionrect.move(
                self._playfield.background.get_width(), 0).collidepoint(e.pos) and
            e.button == 1):
            return True, self._details()
        
        return False, self

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
