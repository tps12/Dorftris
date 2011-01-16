import gettext
gettext.install('dorftris')

from game import Game
from rendering import Renderer

def main():
    game = Game()
    renderer = Renderer(game)
    
    while not game.done:
        game.step()
        renderer.step()

if __name__ == '__main__':
    main()
