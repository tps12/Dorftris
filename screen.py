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
        
        self.selection = []
        
        self.level = 64

        self.stepsound = Sound('38874__swuing__footstep_grass.wav')

    def hexpoints(self):
        return [(self.zoom.height/3,self.zoom.height),
                (0,self.zoom.height/2),
                (self.zoom.height/3,0),
                (self.zoom.width,0),
                (self.zoom.width+self.zoom.height/3,self.zoom.height/2),
                (self.zoom.width,self.zoom.height)]

    def scale(self, font):
        self.font = font
            
        self.graphics = GlyphGraphics(self.font)

        self.air = Entity('air')
        self.button = Entity('button')
        self.ground = Entity('ground')

        self.hex_image = Surface((self.zoom.width+self.zoom.height/3,
                                  self.zoom.height+1),
                            flags=SRCALPHA)
        gfxdraw.polygon(self.hex_image, self.hexpoints(), (0, 0, 0))

        self.hex_fill = Surface(self.hex_image.get_size(), flags=SRCALPHA)
        gfxdraw.filled_polygon(self.hex_fill, self.hexpoints(), (0,0, 0, 255))

        self.sky = self.hex_fill.copy()
        self.sky.fill((0, 85, 85), special_flags=BLEND_ADD)

        self.designation = self.hex_fill.copy()
        self.designation.fill((0, 0, 0, 85), special_flags=BLEND_RGBA_MULT)
        self.designation.fill((85, 85, 0), special_flags=BLEND_ADD)

        self.grid_image = Surface(self.hex_image.get_size(), flags=SRCALPHA)
        if False: # set true to show grid
            self.grid_image.blit(self.hex_image, (0, 0))
            self.grid_image.fill((16,16,16), special_flags=BLEND_ADD)

        self.sprites.empty()

        self.mouse_sprite = DirtySprite()
        self.mouse_sprite.image = Surface(self.hex_image.get_size(),
                                          flags=SRCALPHA)
        self.mouse_sprite.image.blit(self.hex_image, (0,0))
        self.mouse_sprite.image.fill((255,255,0), special_flags=BLEND_ADD)
        self.mouse_sprite.rect = self.mouse_sprite.image.get_rect()

        self.selection_sprite = None

        self.entity_sprites = {}

    def makebackground(self):
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                location = self.tile_location((x,y,self.level))
                tile = self.game.world.space[(self.offset[0] + x,
                                              self.offset[1] + y,
                                              self.level)]
                if tile is None:
                    continue
                if tile.is_passable():
                    if self.level > 0:
                        foundation = self.game.world.space[(self.offset[0] + x,
                                                            self.offset[1] + y,
                                                            self.level - 1)]
                        if not foundation.is_passable():
                            if foundation.kind is None:
                                dirt = self.graphics[self.ground][foundation.varient].copy()
                                dirt.fill(foundation.color, special_flags=BLEND_ADD)

                                self.background.blit(dirt, location)
                                if (self.offset[0] + x, self.offset[1] + y,
                                    self.level -1) in self.game.world.designations:
                                    self.background.blit(self.designation,
                                                         (location[0]-self.zoom.height/3,
                                                          location[1]))
                            else:
                                air = self.graphics[self.air][0].copy()
                                air.fill(foundation.color, special_flags=BLEND_ADD)

                                self.background.blit(air, location)
                        else:
                            drawn = False
                            if self.level > 1:
                                below = self.game.world.space[(self.offset[0]+x,
                                                               self.offset[1]+y,
                                                               self.level-2)]
                                if not below.is_passable() and below.kind is None:
                                    air = self.graphics[self.air][0].copy()
                                    air.fill(below.color, special_flags=BLEND_ADD)
                                    self.background.blit(air, location)
                                    drawn = True

                            if not drawn:
                                self.background.blit(self.sky,
                                                     (location[0]-self.zoom.height/3,
                                                      location[1]))
                                
                elif tile.kind is not None:
                    if tile.kind == 'tree-trunk':
                        image = self.graphics[tile][0].copy()
                        image.fill(tile.color, special_flags=BLEND_ADD)
                        image.fill((48,48,48), special_flags=BLEND_ADD)
                        exterior = self.graphics[tile][1].copy()
                        exterior.fill(tile.color, special_flags=BLEND_ADD)
                        image.blit(exterior, (0,0))
                        rings = self.graphics[tile][2].copy()
                        rings.fill(tile.color, special_flags=BLEND_ADD)
                        image.blit(rings, (0,0))
                        self.background.blit(image, location)
                    else:
                        image = self.graphics[tile][tile.varient].copy()
                        image.fill(tile.color, special_flags=BLEND_ADD)
                        self.background.blit(image, location)

                else:
                    if tile.revealed:
                        image = self.hex_fill.copy()
                        image.fill(tile.color, special_flags=BLEND_ADD)
                        self.background.blit(image,
                                             (location[0]-self.zoom.height/3,
                                              location[1]))

                    if (self.offset[0] + x, self.offset[1] + y,
                          self.level) in self.game.world.designations:
                        self.background.blit(self.designation,
                                             (location[0]-self.zoom.height/3,
                                              location[1]))


                self.background.blit(self.grid_image,
                                     (location[0]-self.zoom.height/3,location[1]))

    def location_tile(self, c):
        px, py = c
        x = (px - self.zoom.width/2)/self.zoom.width
        return x, (py - self.zoom.height/2 - (x&1) * self.zoom.height/2)/self.zoom.height

    def tile_location(self, c):
        x, y, z = c
        return (self.zoom.width/2 + x * self.zoom.width,
                self.zoom.height/2 + y * self.zoom.height +
                ((x+self.offset[0])&1) * self.zoom.height/2)

    def resize(self, size):
        self.background = Surface(size, flags=SRCALPHA)
        self.background.fill((0,0,0))

        self.dimensions = self.location_tile(size)

        try:
            self.offset
        except AttributeError:            
            remainder = [self.game.dimensions[i] - self.dimensions[i]
                         for i in range(2)]
            self.offset = tuple([r/2 if r > 0 else 0 for r in remainder])
        
        self.makebackground()

    def draw(self, surface):
        self.sprites.clear(surface, self.background)
        self.sprites.draw(surface)
