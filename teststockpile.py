import gettext
gettext.install('dorftris')

from game import Game
from rendering import Renderer

from data import Barrel, Dwarf, Oak, Stockpile

def main():
    print 'Dwarf should not keep moving barrels around.'
    
    game = Game((10,6,128))
    renderer = Renderer(game)

    dwarf = Dwarf((3,3,64))
    
    game.world.creatures.append(dwarf)

    for i in range(4):
        game.world.items.append(Barrel((8,i,64), Oak))

    game.world.stockpiles.append(Stockpile([(2,5,64)], [Barrel]))

    game.world.stockpiles.append(Stockpile([(4,5,64)], [Barrel]))
    
    while not game.done:
        game.step()
        renderer.step()

if __name__ == '__main__':
    main()
