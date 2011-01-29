import gettext
gettext.install('dorftris')

from random import choice, randint, sample
from time import time

from game import Game
from rendering import Renderer

from data import Barrel, Dwarf, Goblin, Oak, SmallSpider, Stockpile, Tortoise

def main():
    game = Game((156, 104, 128))

    for i in range(20):
        game.world.space.maketree((randint(0, game.dimensions[0]-1),
                       randint(0, game.dimensions[1]-1),
                       64))    

    renderers = [Renderer(game)]

    kind = (Dwarf,Goblin,Tortoise,SmallSpider)

    for i in range(20):
        creature = choice(kind)((randint(0,game.dimensions[0]-1),
                                 randint(0,game.dimensions[1]-1),
                                 64))
        game.schedule(creature)

    for i in range(10):
        game.world.additem(Barrel((randint(0,game.dimensions[0]-1),
                                        randint(0,game.dimensions[1]-1),
                                        64),
                                       Oak))
        
    game_acc = 0
    render_acc = 0

    render_dt = 0.05

    last = time()

    while renderers:
        current = time()
        delta = min(0.125, max(0, current - last))

        game_acc += delta
        render_acc += delta

        while game_acc > game.dt:
            game.step()
            game_acc -= game.dt
        if render_acc > render_dt:
            if renderers[-1].step():
                renderers = renderers[:-1]
            render_acc = 0

        last = current

if __name__ == '__main__':
    main()
