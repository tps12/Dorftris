from random import choice, randint

import pygame
from pygame import display, event, font, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import Sound
from pygame.sprite import *

from data import Corpse, Entity
from glyphs import GlyphGraphics

INFO_WIDTH = 20
STATUS_HEIGHT = 2

class Renderer(object):
    def __init__(self, game):
        self.game = game
        
        pygame.init()

        key.set_repeat(50, 50)

        self.tile_width = 16
        self.tile_height = 18

        self.definetiles()
        
        self.level = 64

        self.makescreen((1400, 800))

        display.set_caption(_('Hex Grid'))

        self.stepsound = Sound('38874__swuing__footstep_grass.wav')

    def tile_location(self, c):
        x, y, z = c
        return (self.tile_width/2 + x * self.tile_width,
                self.tile_height/2 + y * self.tile_height +
                ((x+self.offset[0])&1) * self.tile_height/2)

    def location_tile(self, c):
        px, py = c
        x = (px - self.tile_width/2)/self.tile_width
        return x, (py - self.tile_height/2 - (x&1) * self.tile_height/2)/self.tile_height

    def hexpoints(self):
        return [(self.tile_height/3,self.tile_height),
                (0,self.tile_height/2),
                (self.tile_height/3,0),
                (self.tile_width,0),
                (self.tile_width+self.tile_height/3,self.tile_height/2),
                (self.tile_width,self.tile_height)]

    def definetiles(self):
        self.uifont = font.Font('FreeMono.ttf', max(self.tile_width, self.tile_height))
        self.graphics = GlyphGraphics(self.uifont)

        self.pause_notice = self.uifont.render(_('*** PAUSED ***'), True,
                                               (255,255,255))
        self.pause_notice.fill((255,255,255), special_flags=BLEND_ADD)

        self.air = Entity('air')
        self.ground = Entity('ground')

        self.hex_image = Surface((self.tile_width+self.tile_height/3, self.tile_height+1),
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

        self.sprites = LayeredUpdates()

        self.mouse_sprite = Sprite()
        self.mouse_sprite.image = Surface(self.hex_image.get_size(),
                                          flags=SRCALPHA)
        self.mouse_sprite.image.blit(self.hex_image, (0,0))
        self.mouse_sprite.image.fill((255,255,0), special_flags=BLEND_ADD)
        self.mouse_sprite.rect = self.mouse_sprite.image.get_rect()

        self.entity_sprites = {}
    
    def makebackground(self):
        self.background = Surface(self.screen.get_size())
        
        self.background.fill((0,0,0))

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
                                                         (location[0]-self.tile_height/3,
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
                                                     (location[0]-self.tile_height/3,
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

                elif (self.offset[0] + x, self.offset[1] + y,
                      self.level) in self.game.world.designations:
                    self.background.blit(self.designation,
                                         (location[0]-self.tile_height/3,
                                          location[1]))


                self.background.blit(self.grid_image,
                                     (location[0]-self.tile_height/3,location[1]))

        self.screen.blit(self.background, (0,0))

    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)

        tile = self.location_tile(size)
        self.dimensions = tile[0]-INFO_WIDTH, tile[1]-STATUS_HEIGHT

        try:
            self.offset
        except AttributeError:            
            remainder = [self.game.dimensions[i] - self.dimensions[i]
                         for i in range(2)]
            self.offset = tuple([r/2 if r > 0 else 0 for r in remainder])

        self.makebackground()

    def visible(self, location):
        return all([self.offset[i] <= location[i] < self.offset[i] + self.dimensions[i]
                    for i in range(2)]) and location[2] == self.level

    def update(self, entities, pos, descs):
        moved = False
        
        for entity in entities:
            if entity.location is None or not self.visible(entity.location):
                if entity in self.entity_sprites:
                    self.sprites.remove(self.entity_sprites[entity])
                    del self.entity_sprites[entity]
            elif entity not in self.entity_sprites:
                sprite = Sprite()

                if isinstance(entity, Corpse):
                    image = self.graphics[entity.origins][0].copy()
                else:
                    image = self.graphics[entity][0].copy()
                    
                image.fill(entity.color, special_flags=BLEND_ADD)
                
                sprite.image = Surface(image.get_size())
                sprite.image.fill((0,0,0))
                sprite.image.blit(image, (0,0))
                x, y = self.tile_location([entity.location[i] - self.offset[i]
                                           for i in range(2)] +
                                          [entity.location[2]])
                sprite.rect = sprite.image.get_rect().move(x, y)
                self.sprites.add(sprite)

                self.entity_sprites[entity] = sprite

            if entity in self.entity_sprites:
                sprite = self.entity_sprites[entity]
                x, y = self.tile_location([entity.location[i] - self.offset[i]
                                           for i in range(2)] +
                                          [entity.location[2]])
                
                if sprite.rect.topleft != (x,y):
                    sprite.rect.topleft = (x,y)
                    moved = True

                if Rect(x, y, self.tile_width, self.tile_height).collidepoint(pos):
                    descs.append(entity.description())

        return moved

    def mousepos(self, pos = None):
        if pos is None:
            pos = mouse.get_pos()
        else:
            mouse.set_pos(pos)
        tile = self.location_tile(pos)
        if not (0 <= tile[0] < self.dimensions[0] and
                0 <= tile[1] < self.dimensions[1]):
            tile = None
        return pos, tile

    def clamp(self, value, limits):
        if value < limits[0]:
            return limits[0], value - limits[0]
        elif value > limits[1]:
            return limits[1], value - limits[1]
        else:
            return value, 0

    def scroll(self, dx, dy):
        dest, remainder = self.clamp(
            self.offset[1] + dy,
            (0, self.game.dimensions[1] - self.dimensions[1]))

        self.offset = (self.offset[0], dest)

        pos, tile = self.mousepos()

        while ((remainder < 0 and 0 < tile[1]) or
               (remainder > 0 and tile[1] < self.dimensions[1]-1)):
            pos, tile = self.mousepos((pos[0],
                                       pos[1] +
                                       self.tile_height * remainder/abs(remainder)))
            remainder -= remainder/abs(remainder)

        return pos, tile

    def step(self):
        pos, tile = self.mousepos()

        for e in event.get():
            if e.type == QUIT:
                self.game.done = True
            elif e.type == KEYDOWN:
                pressed = key.get_pressed()
                shifted = pressed[K_LSHIFT] or pressed[K_RSHIFT]
                scroll = 10 if shifted else 1
                
                if e.key == K_ESCAPE:
                    self.game.done = True
                elif e.key == K_SPACE:
                    self.game.paused = not self.game.paused
                elif e.key == K_UP:
                    pos, tile = self.scroll(0, -scroll)
                                        
                    self.makebackground()
                elif e.key == K_DOWN:
                    dest = self.offset[1] + scroll

                    if dest < self.game.dimensions[1] - self.dimensions[1]:
                        self.offset = (self.offset[0], dest)
                    else:
                        self.offset = (self.offset[0],
                                       self.game.dimensions[1] - self.dimensions[1])
                        while scroll > 0 and tile[1] < self.dimensions[1]-1:
                            pos, tile = self.mousepos((pos[0],
                                                       pos[1] + self.tile_height))
                            scroll -= 1

                    self.makebackground()
                elif e.key == K_LEFT:
                    self.offset = (max(self.offset[0]-scroll, 0), self.offset[1])
                    self.makebackground()
                elif e.key == K_RIGHT:
                    self.offset = (min(self.offset[0]+scroll,
                                       self.game.dimensions[0] - self.dimensions[0]),
                                   self.offset[1])
                    self.makebackground()
                elif e.unicode == '>':
                    self.level = max(self.level-1, 0)
                    self.makebackground()
                elif e.unicode == '<':
                    self.level = min(self.level+1, self.game.dimensions[2])
                    self.makebackground()
                elif e.unicode == 'd':
                    import pdb
                    pdb.set_trace()
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    if tile is not None:
                        x, y, z = (self.offset[0] + tile[0],
                                   self.offset[1] + tile[1],
                                   self.level)
                        target = self.game.world.space[(x,y,z)]
                        if target.is_passable() and z > 0:
                            z -= 1
                            target = self.game.world.space[(x,y,z)]
                        if not target.is_passable():
                            self.game.world.designations.append((x,y,z))
                            self.makebackground()
                    
                elif e.button == 4:
                    self.tile_width += 2
                    self.tile_height += 2
                    self.definetiles()

                    if tile is not None:
                        newtile = self.location_tile(pos)
                        if (0 <= newtile[0] < self.dimensions[0] and
                            0 <= newtile[1] < self.dimensions[1]):
                            self.offset = tuple(
                                [self.offset[i] - (newtile[i] - tile[i])
                                 for i in range(2)])
                    
                    self.makescreen(self.screen.get_size())
                    
                elif e.button == 5:
                    self.tile_width = max(self.tile_width - 2, 2)
                    self.tile_height = max(self.tile_height - 2, 4)
                    self.definetiles()

                    if tile is not None:
                        newtile = self.location_tile(pos)
                        if (0 <= newtile[0] < self.dimensions[0] and
                            0 <= newtile[1] < self.dimensions[1]):
                            self.offset = tuple(
                                [self.offset[i] - (newtile[i] - tile[i])
                                 for i in range(2)])

                    self.makescreen(self.screen.get_size())
                    
            elif e.type == VIDEORESIZE:
                self.makescreen(e.size)

        if self.game.world.space.changed:
            self.makebackground()
            self.game.world.space.changed = False

        descs = []

        moved = self.update(self.game.world.creatures, pos, descs)

        moved = self.update(self.game.world.items, pos, descs)

        for entity in self.entity_sprites.keys():
            if (entity not in self.game.world.creatures and
                entity not in self.game.world.items):
                self.sprites.remove(self.entity_sprites[entity])
                del self.entity_sprites[entity]

        if tile is not None:
            if self.mouse_sprite not in self.sprites:
                self.sprites.add(self.mouse_sprite, layer=1)
            self.mouse_sprite.rect.topleft = self.tile_location(
                tile + (self.level,))
            self.mouse_sprite.rect.move_ip(-self.tile_height/3, 0)

            mouse.set_visible(False)
        else:
            if self.mouse_sprite in self.sprites:
                self.sprites.remove(self.mouse_sprite)

            mouse.set_visible(True)

        self.sprites.clear(self.screen, self.background)
        self.sprites.draw(self.screen)

        info_loc = self.tile_location((self.dimensions[0]+1,0,self.level))
        self.screen.fill((0,0,0), Rect(info_loc, self.screen.get_size()))
        for d in descs:
            line = self.uifont.render(d, True, (255,255,255))
            self.screen.blit(line, info_loc)
            info_loc = (info_loc[0], info_loc[1] + line.get_height())

        msg_loc = self.tile_location((0,self.dimensions[1]+1,self.level))
        self.screen.fill((0,0,0), Rect(msg_loc, self.pause_notice.get_size()))        
        if self.game.paused:
            self.screen.blit(self.pause_notice, msg_loc)

        if moved:
            self.stepsound.play()

        display.flip()
