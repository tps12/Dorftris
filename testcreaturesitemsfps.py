import gettext
gettext.install('dorftris')

from random import randint
from time import time

from game import Game
from rendering import Renderer

from data import Barrel, Dwarf, Oak

def main():
    n = 30000
    m = 1500
    
    print 'How fast can a world with {0} items and {1} creatures run.'.format(n, m)
    
    game = Game((256,256,128))
    renderer = Renderer(game)

    for i in range(n):
        b = Barrel((randint(0,255),randint(0,255),64), Oak)
        game.world.items.append(b)
        game.world.space[b.location].items.append(b)

    for i in range(m):
        d = Dwarf((randint(0,255),randint(0,255),64))
        game.world.creatures.append(d)
        game.world.space[d.location].contents.append(d)

    start = time()
    
    while not game.done:
        game.step()
        renderer.step()

    print game.t/(time() - start), 'FPS'

if __name__ == '__main__':
    main()
