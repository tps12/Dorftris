import gettext
gettext.install('dorftris')

from game import Game
from rendering import Renderer

from data import Barrel, Beverage, Dwarf, Item, Oak, Stockpile

def main():
    print 'Dwarf should not keep moving barrels around.'
    
    game = Game((10,6,128))
    renderer = Renderer(game)

    game.schedule(Dwarf((3,3,64)))

    for i in range(4):
        game.world.additem(Item(Barrel, (8,i,64), 1.0))

    game.world.addstockpile(Stockpile([(2,5,64)], [Beverage.stocktype]))

    game.world.addstockpile(Stockpile([(4,5,64)], [Beverage.stocktype]))
    
    while not game.done:
        game.step()
        renderer.step()

if __name__ == '__main__':
    main()
