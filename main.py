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

    renderer = Renderer(game)

    kind = (Dwarf,Goblin,Tortoise,SmallSpider)

    for i in range(20):
        creature = choice(kind)((randint(0,game.dimensions[0]-1),
                                 randint(0,game.dimensions[1]-1),
                                 64))
        game.world.creatures.append(creature)
        game.world.space[creature.location].contents.append(creature)

    for i in range(10):
        barrel = Barrel((randint(0,game.dimensions[0]-1),
                                        randint(0,game.dimensions[1]-1),
                                        64),
                                       Oak)
        game.world.items.append(barrel)
        game.world.space[barrel.location].items.append(barrel)

    game_acc = 0
    render_acc = 0

    game_dt = 0.1
    render_dt = 0.05

    last = time()
    
    while not game.done:
        current = time()
        delta = min(0.125, max(0, current - last))

        game_acc += delta
        render_acc += delta

        while game_acc > game_dt:
            game.step()
            game_acc -= game_dt
        if render_acc > render_dt:
            renderer.step()
            render_acc = 0

        last = current

if __name__ == '__main__':
    main()
