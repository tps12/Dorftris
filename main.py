from random import choice, randint

import pygame
from pygame import display, draw, event, Surface
from pygame.locals import *
from pygame.mixer import Sound
from pygame.sprite import *

from data import Creature
from glyphs import GlyphGraphics

TILE_WIDTH = 16
TILE_HEIGHT = 18

def tile_location(c):
    x, y = c
    return (TILE_WIDTH/2 + x * TILE_WIDTH,
            TILE_HEIGHT/2 + y * TILE_HEIGHT + (x&1) * TILE_HEIGHT/2)

def main():
    pygame.init()

    dimensions = 80, 50

    screen = pygame.display.set_mode(tile_location([d+1 for d in dimensions]),
                                     HWSURFACE)

    display.set_caption('Hex Grid')

    background = Surface(screen.get_size())
    
    background.fill((0,0,0))

    graphics = GlyphGraphics(max(TILE_WIDTH, TILE_HEIGHT))

    for x in range(dimensions[0]):
        for y in range(dimensions[1]):
            dirt = choice(graphics['ground']).copy()
            dirt.fill((0,randint(65,189),0), special_flags=BLEND_ADD)
            background.blit(dirt, tile_location((x,y)))

    screen.blit(background, (0,0))

    sprites = Group()

    kind = ('dwarf','goblin','tortoise','spider-small')

    creatures = []
    for i in range(20):
        creature = Creature()
        creature.location = (randint(0,dimensions[0]-1),
                             randint(0,dimensions[1]-1))
        creatures.append(creature)

    creature_sprites = {}

    for creature in creatures:
        sprite = Sprite()
        image = graphics[choice(kind)][0].copy()
        image.fill((randint(0,255),randint(0,255),randint(0,255)),
                   special_flags=BLEND_ADD)
        sprite.image = Surface(image.get_size())
        sprite.image.fill((0,0,0))
        sprite.image.blit(image, (0,0))
        x, y = tile_location(creature.location)
        sprite.rect = sprite.image.get_rect().move(x, y)
        sprites.add(sprite)

        creature_sprites[creature] = sprite

    step = Sound('38874__swuing__footstep_grass.wav')

    done = False

    while not done:
        for e in event.get():
            if e.type == QUIT:
                done = True
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    done = True

        stepped = False
        for creature in creatures:
            creature.step()

            if creature in creature_sprites:
                sprite = creature_sprites[creature]
                x, y = tile_location(creature.location)
                if sprite.rect.topleft != (x,y):
                    sprite.rect.topleft = (x,y)
                    stepped = True

        sprites.clear(screen, background)
        sprites.draw(screen)

        if stepped:
            step.play()

        display.flip()

if __name__ == '__main__':
    main()