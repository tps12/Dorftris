import gettext
gettext.install('dorftris')

from random import randint
from time import time

from game import Game
from rendering import Renderer

from data import Barrel, Oak

def main():
    n = 100000
    
    print 'How fast can a world with {0} items run.'.format(n)
    
    game = Game((256,256,128))
    renderer = Renderer(game)

    for i in range(n):
        game.world.items.append(Barrel((randint(0,255),randint(0,255),64), Oak))

    start = time()
    
    while not game.done:
        game.step()
        renderer.step()

    print game.t/(time() - start), 'FPS'

if __name__ == '__main__':
    main()
