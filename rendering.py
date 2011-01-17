from random import choice, randint

import pygame
from pygame import display, draw, event, font, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import Sound
from pygame.sprite import *

from data import Corpse, Entity
from glyphs import GlyphGraphics

TILE_WIDTH = 16
TILE_HEIGHT = 18

INFO_WIDTH = 20
STATUS_HEIGHT = 2

def tile_location(c):
    x, y, z = c
    return (TILE_WIDTH/2 + x * TILE_WIDTH,
            TILE_HEIGHT/2 + y * TILE_HEIGHT + (x&1) * TILE_HEIGHT/2)

def location_tile(c):
    px, py = c
    x = (px - TILE_WIDTH/2)/TILE_WIDTH
    return x, (py - TILE_HEIGHT/2 - (x&1) * TILE_HEIGHT/2)/TILE_HEIGHT

class Renderer(object):
    def __init__(self, game):
        self.game = game
        
        pygame.init()

        self.uifont = font.Font('FreeMono.ttf', max(TILE_WIDTH, TILE_HEIGHT))
        self.graphics = GlyphGraphics(self.uifont)

        self.pause_notice = self.uifont.render(_('*** PAUSED ***'), True,
                                               (255,255,255))
        self.pause_notice.fill((255,255,255), special_flags=BLEND_ADD)

        self.air = Entity('air')
        self.ground = Entity('ground')

        self.hex_image = Surface((TILE_WIDTH+TILE_HEIGHT/3, TILE_HEIGHT+1),
                            flags=SRCALPHA)
        draw.lines(self.hex_image, (0, 0, 0), True,
                      [(TILE_HEIGHT/3,TILE_HEIGHT),
                       (0,TILE_HEIGHT/2),
                       (TILE_HEIGHT/3,0),
                       (TILE_WIDTH,0),
                       (TILE_WIDTH+TILE_HEIGHT/3,TILE_HEIGHT/2),
                       (TILE_WIDTH,TILE_HEIGHT)],
                      1)

        self.grid_image = Surface(self.hex_image.get_size(), flags=SRCALPHA)
        if True: # set true to show grid
            self.grid_image.blit(self.hex_image, (0, 0))
            self.grid_image.fill((16,16,16), special_flags=BLEND_ADD)

        self.level = 1

        self.makescreen((1400, 800))

        display.set_caption(_('Hex Grid'))

        self.sprites = LayeredUpdates()

        self.mouse_sprite = Sprite()
        self.mouse_sprite.image = Surface(self.hex_image.get_size(),
                                          flags=SRCALPHA)
        self.mouse_sprite.image.blit(self.hex_image, (0,0))
        self.mouse_sprite.image.fill((255,255,0), special_flags=BLEND_ADD)
        self.mouse_sprite.rect = self.mouse_sprite.image.get_rect()

        self.entity_sprites = {}

        self.stepsound = Sound('38874__swuing__footstep_grass.wav')

    def makebackground(self):
        self.background = Surface(self.screen.get_size())
        
        self.background.fill((0,0,0))

        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                location = tile_location((x,y,self.level))
                tile = self.game.world.space[(self.offset[0] + x,
                                              self.offset[1] + y,
                                              self.level)]
                if tile.is_passable():
                    if self.level > 0:
                        foundation = self.game.world.space[(self.offset[0] + x,
                                                            self.offset[1] + y,
                                                            self.level - 1)]
                        if not foundation.is_passable():
                            dirt = self.graphics[self.ground][foundation.varient].copy()
                            dirt.fill((0,foundation.shade,0), special_flags=BLEND_ADD)

                            self.background.blit(dirt, location)
                        elif self.level > 1:
                            below = self.game.world.space[(self.offset[0] + x,
                                                           self.offset[1] + y,
                                                           self.level - 2)]
                            if not below.is_passable():
                                air = self.graphics[self.air][0].copy()
                                air.fill((0,below.shade,0), special_flags=BLEND_ADD)

                                self.background.blit(air, location)
                    
                self.background.blit(self.grid_image,
                                     (location[0]-TILE_HEIGHT/3,location[1]))

        self.screen.blit(self.background, (0,0))

    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)

        tile = location_tile(size)
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
                x, y = tile_location([entity.location[i] - self.offset[i]
                                      for i in range(2)] + [entity.location[2]])
                sprite.rect = sprite.image.get_rect().move(x, y)
                self.sprites.add(sprite)

                self.entity_sprites[entity] = sprite

            if entity in self.entity_sprites:
                sprite = self.entity_sprites[entity]
                x, y = tile_location([entity.location[i] - self.offset[i]
                                      for i in range(2)] + [entity.location[2]])
                
                if sprite.rect.topleft != (x,y):
                    sprite.rect.topleft = (x,y)
                    moved = True

                if Rect(x, y, TILE_WIDTH, TILE_HEIGHT).collidepoint(pos):
                    descs.append(entity.description())

        return moved

    def step(self):
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
                    self.offset = (self.offset[0], max(self.offset[1]-scroll, 0))
                    self.makebackground()
                elif e.key == K_DOWN:
                    self.offset = (self.offset[0],
                                   min(self.offset[1]+scroll,
                                       self.game.dimensions[1] - self.dimensions[1]))
                    self.makebackground()
                elif e.key == K_LEFT:
                    self.offset = (max(self.offset[0]-2*(scroll+1)/2, 0), self.offset[1])
                    self.makebackground()
                elif e.key == K_RIGHT:
                    self.offset = (min(self.offset[0]+2*(scroll+1)/2,
                                       self.game.dimensions[0] - self.dimensions[0]),
                                   self.offset[1])
                    self.makebackground()
                elif e.unicode == '>':
                    self.level = max(self.level-1, 0)
                    self.makebackground()
                elif e.unicode == '<':
                    self.level = min(self.level+1, self.game.dimensions[2])
                    self.makebackground()
            elif e.type == VIDEORESIZE:
                self.makescreen(e.size)

        pos = mouse.get_pos()
        descs = []

        moved = self.update(self.game.world.creatures, pos, descs)

        moved = self.update(self.game.world.items, pos, descs)

        for entity in self.entity_sprites.keys():
            if (entity not in self.game.world.creatures and
                entity not in self.game.world.items):
                self.sprites.remove(self.entity_sprites[entity])
                del self.entity_sprites[entity]

        tile = location_tile(pos)
        if (0 <= tile[0] < self.dimensions[0] and
            0 <= tile[1] < self.dimensions[1]):
            if self.mouse_sprite not in self.sprites:
                self.sprites.add(self.mouse_sprite, layer=1)
            self.mouse_sprite.rect.topleft = tile_location(tile + (self.level,))
            self.mouse_sprite.rect.move_ip(-TILE_HEIGHT/3, 0)

            mouse.set_visible(False)
        else:
            if self.mouse_sprite in self.sprites:
                self.sprites.remove(self.mouse_sprite)

            mouse.set_visible(True)

        self.sprites.clear(self.screen, self.background)
        self.sprites.draw(self.screen)

        info_loc = tile_location((self.dimensions[0]+1,0,self.level))
        self.screen.fill((0,0,0), Rect(info_loc, self.screen.get_size()))
        for d in descs:
            line = self.uifont.render(d, True, (255,255,255))
            self.screen.blit(line, info_loc)
            info_loc = (info_loc[0], info_loc[1] + line.get_height())

        msg_loc = tile_location((0,self.dimensions[1]+1,self.level))
        self.screen.fill((0,0,0), Rect(msg_loc, self.pause_notice.get_size()))        
        if self.game.paused:
            self.screen.blit(self.pause_notice, msg_loc)

        if moved:
            self.stepsound.play()

        display.flip()
