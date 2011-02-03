import gettext
import gettext
gettext.install('dorftris')

from random import choice, randint
from time import sleep, time

import pygame
from pygame.locals import *
from pygame import display

from data import Dwarf, Pickax, Player
from game import Game
from prefs import DisplayOptions
from rendering import Renderer
from substances import Metal, Wood

def main():
    n = 200000
    m = 200
    
    print 'How fast can a world with {0} items and {1} creatures run.'.format(n, m)

    pygame.init()
    
    game = Game((256,256,128))
    user = Player(game.world)

    for i in range(n):
        game.world.additem(Pickax((randint(0,255),randint(0,255),64),
                                  choice(Metal.__subclasses__()),
                                  choice(Wood.__subclasses__())))

    for i in range(m):
        game.schedule(Dwarf(user, (randint(0,255),randint(0,255),64)))

    display.set_mode((1400,800), HWSURFACE | RESIZABLE)

    renderers = [Renderer(game, user, DisplayOptions('FreeMono.ttf', False, 16, 18))]
    
    game_acc = 0
    render_acc = 0

    last = time()

    while renderers:
        current = time()
        delta = min(0.125, max(0, current - last))

        renderer = renderers[-1]   
        
        if renderer.game:
            game_acc += delta
            while game_acc > renderer.game.dt:
                renderer.game.step()
                game_acc -= renderer.game.dt
            rest = renderer.game.dt - game_acc
        else:
            rest = float('inf')
        
        render_acc += delta
        if render_acc > renderer.dt:
            child = renderer.step()
            if child != renderer:
                if child:
                    renderers.append(child)
                else:
                    renderers = renderers[:-1]
            render_acc = 0

        last = current

        sleep(min(rest, renderers[-1].dt if renderers else 0))

if __name__ == '__main__':
    main()
