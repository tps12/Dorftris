import gettext
gettext.install('dorftris')

from random import choice, randint, sample
from time import time

from game import Game
from menu import MainMenu
from rendering import Renderer

from data import Barrel, Dwarf, Goblin, Oak, SmallSpider, Stockpile, Tortoise

def main():
    renderers = [MainMenu()]

    game_acc = 0
    render_acc = 0

    last = time()

    while renderers:
        current = time()
        delta = min(0.125, max(0, current - last))

        renderer = renderers[-1]   

        if renderer.game:
            game_acc += delta
            while game_acc > renderer.game.dt:
                renderer.game.step()
                game_acc -= game.dt
        
        render_acc += delta
        if render_acc > renderer.dt:
            child = renderer.step()
            if child != renderer:
                if child:
                    renderers.append(child)
                else:
                    renderers = renderers[:-1]
            render_acc = 0

        last = current

if __name__ == '__main__':
    main()
