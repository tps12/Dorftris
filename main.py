import gettext
gettext.install('dorftris')

from random import choice, randint, sample

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

    for i in range(10):
        game.world.items.append(Barrel((randint(0,game.dimensions[0]-1),
                                        randint(0,game.dimensions[1]-1),
                                        64),
                                       Oak))
    
    while not game.done:
        game.step()
        renderer.step()

if __name__ == '__main__':
    main()
