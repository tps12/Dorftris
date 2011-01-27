import gettext
gettext.install('dorftris')

from game import Game
from rendering import Renderer

from data import Barrel, Dwarf, Oak, Stockpile

def main():
    print 'Dwarf should store barrel in stockpile, then drink from it.'
    
    game = Game((10,6,128))
    renderer = Renderer(game)

    dwarf = Dwarf((3,3,64))
    dwarf.hydration = 1200
    
    game.world.space[dwarf.location].contents.append(dwarf)
    game.schedule(dwarf)

    barrel = Barrel((8,4,64), Oak)
    
    game.world.items.append(barrel)
    game.world.space[barrel.location].items.append(barrel)

    game.world.stockpiles.append(Stockpile([(2,5,64)], [Barrel]))
    
    while not game.done:
        game.step()
        renderer.step()

if __name__ == '__main__':
    main()
