import gettext
gettext.install('dorftris')

from random import randint

from game import Game
from rendering import Renderer

from data import Dwarf

def main():
    n = 2000
    
    print 'How fast can a world with {0} guys run.'.format(n)
    
    game = Game((256,256,128))
    renderer = Renderer(game)

    for i in range(n):
        game.world.creatures.append(Dwarf((randint(0,255),randint(0,255),64)))
    
    while not game.done:
        game.step()
        renderer.step()

if __name__ == '__main__':
    main()
