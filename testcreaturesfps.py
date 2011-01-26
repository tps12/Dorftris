import gettext
gettext.install('dorftris')

from random import randint

from game import Game
from rendering import Renderer

from data import Tortoise

def main():
    print 'How fast can a world with lots of guys run.'
    
    game = Game((256,256,128))
    renderer = Renderer(game)

    for i in range(2000):
        game.world.creatures.append(Tortoise((randint(0,255),randint(0,255),64)))
    
    while not game.done:
        game.step()
        renderer.step()

if __name__ == '__main__':
    main()
