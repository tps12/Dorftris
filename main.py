import gettext
gettext.install('dorftris')

from random import choice, randint, sample

from game import Game
from rendering import Renderer

from data import Barrel, Dwarf, Goblin, Oak, SmallSpider, Stockpile, Tortoise

def main():
    game = Game()
    renderer = Renderer(game)

    kind = (Dwarf,Goblin,Tortoise,SmallSpider)

    for i in range(20):
        creature = choice(kind)((randint(0,game.dimensions[0]-1),
                                 randint(0,game.dimensions[1]-1),
                                 64))
        game.world.creatures.append(creature)

    for i in range(10):
        game.world.items.append(Barrel((randint(0,game.dimensions[0]-1),
                                        randint(0,game.dimensions[1]-1),
                                        64),
                                       Oak))

    for i in range(10):
        c = (randint(0,game.dimensions[0]-1),
             randint(0,game.dimensions[1]-1),
             64)
        if game.world.space[c].is_passable():
            neighbors = [(x,y,c[2]) for (x,y) in
                         game.world.space.pathing.adjacent_xy((c[0:2]))]
            game.world.stockpiles.append(
                Stockpile([p for p in [c] +
                           sample(neighbors, randint(0, len(neighbors)))
                           if game.world.space[p].is_passable()],
                          [Barrel]))
    
    while not game.done:
        game.step()
        renderer.step()

if __name__ == '__main__':
    main()
