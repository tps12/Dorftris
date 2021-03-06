import gettext
gettext.install('dorftris')

from time import sleep, time

from menu import MainMenu

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
                game_acc -= renderer.game.dt
            rest = renderer.game.dt - game_acc
        else:
            rest = float('inf')
        
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

        sleep(min(rest, renderers[-1].dt if renderers else 0))
        
if __name__ == '__main__':
    main()
