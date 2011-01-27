import gettext
gettext.install('dorftris')

from random import randint
from time import time

from game import Game
from rendering import Renderer

from data import Dwarf

def main():
    n = 1500
    
    print 'How fast can a world with {0} guys run.'.format(n)
    
    game = Game((256,256,128))
    renderer = Renderer(game)

    for i in range(n):
        d = Dwarf((randint(0,255),randint(0,255),64))
        game.world.space[d.location].contents.append(d)
        game.schedule(d)

    start = time()
    
    while not game.done:
        game.step()
        renderer.step()

    print game.t/(time() - start), 'FPS'

if __name__ == '__main__':
    main()
