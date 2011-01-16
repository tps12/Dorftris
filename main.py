import gettext
gettext.install('dorftris')

from random import choice, randint

import pygame
from pygame import display, draw, event, font, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import Sound
from pygame.sprite import *

from data import Barrel, Corpse, Dwarf, Entity, Goblin, Oak, SmallSpider, Thing, Tortoise, World
from glyphs import GlyphGraphics
from pathing import PathManager

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

def main():
    pygame.init()

    dimensions = 80, 50

    padded = dimensions[0] + INFO_WIDTH, dimensions[1] + STATUS_HEIGHT

    screen = pygame.display.set_mode(tile_location([d+1 for d in padded]),
                                     HWSURFACE)

    display.set_caption('Hex Grid')

    background = Surface(screen.get_size())
    
    background.fill((0,0,0))

    uifont = font.Font('FreeMono.ttf', max(TILE_WIDTH, TILE_HEIGHT))
    graphics = GlyphGraphics(uifont)

    pause_notice = uifont.render('*** PAUSED ***', True, (255,255,255))
    pause_notice.fill((255,255,255), special_flags=BLEND_ADD)

    ground = Entity('ground')

    hex_image = Surface((TILE_WIDTH+TILE_HEIGHT/3, TILE_HEIGHT+1),
                        flags=SRCALPHA)
    draw.lines(hex_image, (0, 0, 0), True,
                  [(TILE_HEIGHT/3,TILE_HEIGHT),
                   (0,TILE_HEIGHT/2),
                   (TILE_HEIGHT/3,0),
                   (TILE_WIDTH,0),
                   (TILE_WIDTH+TILE_HEIGHT/3,TILE_HEIGHT/2),
                   (TILE_WIDTH,TILE_HEIGHT)],
                  1)

    grid_image = Surface(hex_image.get_size(), flags=SRCALPHA)
    if False:
        grid_image.blit(hex_image, (0, 0))
        grid_image.fill((16,16,16), special_flags=BLEND_ADD)

    for x in range(dimensions[0]):
        for y in range(dimensions[1]):
            dirt = choice(graphics[ground]).copy()
            dirt.fill((0,randint(65,189),0), special_flags=BLEND_ADD)

            location = tile_location((x,y))
            background.blit(dirt, location)
            background.blit(grid_image, (location[0]-TILE_HEIGHT/3,location[1]))

    screen.blit(background, (0,0))

    sprites = LayeredUpdates()

    mouse_sprite = Sprite()
    mouse_sprite.image = Surface(hex_image.get_size(), flags=SRCALPHA)
    mouse_sprite.image.blit(hex_image, (0,0))
    mouse_sprite.image.fill((255,255,0), special_flags=BLEND_ADD)
    mouse_sprite.rect = mouse_sprite.image.get_rect()

    kind = (Dwarf,Goblin,Tortoise,SmallSpider)

    class Tile(object):
        def __init__(self, passable):
            self.passable = passable
            
        def is_passable(self):
            return self.passable

    class Space(object):
        def __init__(self, dim):
            self.dim = (dim[0], dim[1], 2)
            self.pathing = PathManager(self)

        def get_dimensions(self):
            return self.dim

        def __getitem__(self, loc):
            return Tile(loc[2] == 1)

    world = World(Space(dimensions), [], [])

    for i in range(20):
        creature = choice(kind)((randint(0,dimensions[0]-1),
                                 randint(0,dimensions[1]-1)))
        world.creatures.append(creature)

    for i in range(10):
        world.items.append(Barrel((randint(0,dimensions[0]-1),
                                   randint(0,dimensions[1]-1)), Oak))

    entity_sprites = {}

    for creature in world.creatures:
        sprite = Sprite()
        image = graphics[creature][0].copy()
        image.fill(creature.color, special_flags=BLEND_ADD)
        sprite.image = Surface(image.get_size())
        sprite.image.fill((0,0,0))
        sprite.image.blit(image, (0,0))
        x, y = tile_location(creature.location)
        sprite.rect = sprite.image.get_rect().move(x, y)
        sprites.add(sprite)

        entity_sprites[creature] = sprite

    step = Sound('38874__swuing__footstep_grass.wav')

    done = False
    paused = False

    while not done:
        for e in event.get():
            if e.type == QUIT:
                done = True
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    done = True
                elif e.key == K_SPACE:
                    paused = not paused
                elif e.key == K_d:
                    import pdb
                    pdb.set_trace()

        stepped = False

        pos = mouse.get_pos()
        descs = []

        for creature in world.creatures:
            if not paused:
                creature.step(world)

            if creature not in world.creatures:
                sprites.remove(entity_sprites[creature])
                del entity_sprites[creature]

            if creature in entity_sprites:
                sprite = entity_sprites[creature]
                x, y = tile_location(creature.location)
                if sprite.rect.topleft != (x,y):
                    sprite.rect.topleft = (x,y)
                    stepped = True
                if Rect(x, y, TILE_WIDTH, TILE_HEIGHT).collidepoint(pos):
                    descs.append(creature.description())

        for item in world.items:
            if item.location is None:
                if item in entity_sprites:
                    sprites.remove(entity_sprites[item])
                    del entity_sprites[item]
            else:
                if item not in entity_sprites:
                    sprite = Sprite()

                    if isinstance(item, Corpse):
                        image = graphics[item.origins][0].copy()
                    else:
                        image = graphics[item][0].copy()
                        
                    image.fill(item.color, special_flags=BLEND_ADD)
                        
                    sprite.image = Surface(image.get_size())
                    sprite.image.fill((0,0,0))
                    sprite.image.blit(image, (0,0))
                    x, y = tile_location(item.location)
                    sprite.rect = sprite.image.get_rect().move(x, y)
                    sprites.add(sprite)

                    entity_sprites[item] = sprite
            
            if item in entity_sprites:
                x, y = tile_location(item.location)
                if Rect(x, y, TILE_WIDTH, TILE_HEIGHT).collidepoint(pos):
                    descs.append(item.description())

        tile = location_tile(pos)
        if 0 <= tile[0] < dimensions[0] and 0 <= tile[1] < dimensions[1]:
            if mouse_sprite not in sprites:
                sprites.add(mouse_sprite, layer=1)
            mouse_sprite.rect.topleft = tile_location(tile)
            mouse_sprite.rect.move_ip(-TILE_HEIGHT/3, 0)

            mouse.set_visible(False)
        else:
            if mouse_sprite in sprites:
                sprites.remove(mouse_sprite)

            mouse.set_visible(True)

        sprites.clear(screen, background)
        sprites.draw(screen)

        info_loc = tile_location((dimensions[0]+1,0))
        screen.fill((0,0,0), Rect(info_loc, screen.get_size()))
        for d in descs:
            line = uifont.render(d, True, (255,255,255))
            screen.blit(line, info_loc)
            info_loc = (info_loc[0], info_loc[1] + line.get_height())

        msg_loc = tile_location((0,dimensions[1]+1))
        screen.fill((0,0,0), Rect(msg_loc, pause_notice.get_size()))        
        if paused:
            screen.blit(pause_notice, msg_loc)

        if stepped:
            step.play()

        display.flip()

if __name__ == '__main__':
    main()
