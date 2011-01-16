from random import choice, randint

import pygame
from pygame import display, draw, event, font, mouse, Rect, Surface
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
    x, y = c
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
        
        padded = (self.game.dimensions[0] + INFO_WIDTH,
                  self.game.dimensions[1] + STATUS_HEIGHT)

        self.screen = pygame.display.set_mode(tile_location([d+1
                                                             for d in padded]),
                                              HWSURFACE)

        display.set_caption(_('Hex Grid'))

        self.background = Surface(self.screen.get_size())
        
        self.background.fill((0,0,0))

        self.uifont = font.Font('FreeMono.ttf', max(TILE_WIDTH, TILE_HEIGHT))
        self.graphics = GlyphGraphics(self.uifont)

        self.pause_notice = self.uifont.render(_('*** PAUSED ***'), True,
                                               (255,255,255))
        self.pause_notice.fill((255,255,255), special_flags=BLEND_ADD)

        ground = Entity('ground')

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
        if False: # set true to show grid
            self.grid_image.blit(self.hex_image, (0, 0))
            self.grid_image.fill((16,16,16), special_flags=BLEND_ADD)

        for x in range(self.game.dimensions[0]):
            for y in range(self.game.dimensions[1]):
                dirt = choice(self.graphics[ground]).copy()
                dirt.fill((0,randint(65,189),0), special_flags=BLEND_ADD)

                location = tile_location((x,y))
                self.background.blit(dirt, location)
                self.background.blit(self.grid_image,
                                     (location[0]-TILE_HEIGHT/3,location[1]))

        self.screen.blit(self.background, (0,0))

        self.sprites = LayeredUpdates()

        self.mouse_sprite = Sprite()
        self.mouse_sprite.image = Surface(self.hex_image.get_size(),
                                          flags=SRCALPHA)
        self.mouse_sprite.image.blit(self.hex_image, (0,0))
        self.mouse_sprite.image.fill((255,255,0), special_flags=BLEND_ADD)
        self.mouse_sprite.rect = self.mouse_sprite.image.get_rect()

        self.entity_sprites = {}

        for creature in self.game.world.creatures:
            sprite = Sprite()
            image = self.graphics[creature][0].copy()
            image.fill(creature.color, special_flags=BLEND_ADD)
            sprite.image = Surface(image.get_size())
            sprite.image.fill((0,0,0))
            sprite.image.blit(image, (0,0))
            x, y = tile_location(creature.location)
            sprite.rect = sprite.image.get_rect().move(x, y)
            self.sprites.add(sprite)

            self.entity_sprites[creature] = sprite

        self.stepsound = Sound('38874__swuing__footstep_grass.wav')

    def step(self):
        for e in event.get():
            if e.type == QUIT:
                self.game.done = True
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.game.done = True
                elif e.key == K_SPACE:
                    self.game.paused = not self.game.paused

        stepped = False

        pos = mouse.get_pos()
        descs = []

        for creature in self.game.world.creatures:
            if creature not in self.game.world.creatures:
                self.sprites.remove(entity_sprites[creature])
                del self.entity_sprites[creature]

            if creature in self.entity_sprites:
                sprite = self.entity_sprites[creature]
                x, y = tile_location(creature.location)
                if sprite.rect.topleft != (x,y):
                    sprite.rect.topleft = (x,y)
                    stepped = True
                if Rect(x, y, TILE_WIDTH, TILE_HEIGHT).collidepoint(pos):
                    descs.append(creature.description())

        for item in self.game.world.items:
            if item.location is None:
                if item in self.entity_sprites:
                    self.sprites.remove(self.entity_sprites[item])
                    del self.entity_sprites[item]
            else:
                if item not in self.entity_sprites:
                    sprite = Sprite()

                    if isinstance(item, Corpse):
                        image = self.graphics[item.origins][0].copy()
                    else:
                        image = self.graphics[item][0].copy()
                        
                    image.fill(item.color, special_flags=BLEND_ADD)
                        
                    sprite.image = Surface(image.get_size())
                    sprite.image.fill((0,0,0))
                    sprite.image.blit(image, (0,0))
                    x, y = tile_location(item.location)
                    sprite.rect = sprite.image.get_rect().move(x, y)
                    self.sprites.add(sprite)

                    self.entity_sprites[item] = sprite
            
            if item in self.entity_sprites:
                x, y = tile_location(item.location)
                if Rect(x, y, TILE_WIDTH, TILE_HEIGHT).collidepoint(pos):
                    descs.append(item.description())

        tile = location_tile(pos)
        if (0 <= tile[0] < self.game.dimensions[0] and
            0 <= tile[1] < self.game.dimensions[1]):
            if self.mouse_sprite not in self.sprites:
                self.sprites.add(self.mouse_sprite, layer=1)
            self.mouse_sprite.rect.topleft = tile_location(tile)
            self.mouse_sprite.rect.move_ip(-TILE_HEIGHT/3, 0)

            mouse.set_visible(False)
        else:
            if self.mouse_sprite in self.sprites:
                self.sprites.remove(self.mouse_sprite)

            mouse.set_visible(True)

        self.sprites.clear(self.screen, self.background)
        self.sprites.draw(self.screen)

        info_loc = tile_location((self.game.dimensions[0]+1,0))
        self.screen.fill((0,0,0), Rect(info_loc, self.screen.get_size()))
        for d in descs:
            line = self.uifont.render(d, True, (255,255,255))
            self.screen.blit(line, info_loc)
            info_loc = (info_loc[0], info_loc[1] + line.get_height())

        msg_loc = tile_location((0,self.game.dimensions[1]+1))
        self.screen.fill((0,0,0), Rect(msg_loc, self.pause_notice.get_size()))        
        if self.game.paused:
            self.screen.blit(self.pause_notice, msg_loc)

        if stepped:
            self.stepsound.play()

        display.flip()
