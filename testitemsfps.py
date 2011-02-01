import gettext
gettext.install('dorftris')

from random import randint
from time import time

from game import Game
from rendering import Renderer

from data import Barrel, Item

def main():
    n = 250000
    
    print 'How fast can a world with {0} items run.'.format(n)
    
    game = Game((256,256,128))
    renderer = Renderer(game)

    start = time()
    for i in range(n):
        game.world.additem(Item(Barrel, (randint(0,255),randint(0,255),64), 1.0))
    print time() - start

    game_acc = 0
    render_acc = 0

    render_dt = 0.05

    last = time()
    
    while not game.done:
        current = time()
        delta = min(0.125, max(0, current - last))

        game_acc += delta
        render_acc += delta

        while game_acc > game.dt:
            game.step()
            game_acc -= game.dt
        if render_acc > render_dt:
            renderer.step()
            render_acc = 0

        last = current

if __name__ == '__main__':
    main()
