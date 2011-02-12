from pygame import display, event, font, key, Rect
from pygame.locals import *

from screen import GameScreen
from status import StatusBar

class Renderer(object):
    def __init__(self, game, player, zoom):
        self.game = game
        self._player = player
        self.zoom = zoom
        
        self.definetiles()

        self.makescreen(display.get_surface().get_size())

    @property
    def dt(self):
        return self.display[-1].dt

    def definetiles(self):
        self.uifont = self.zoom.font
        try:
            self.status.scale(self.uifont)
            for d in self.display:
                d.scale(self.uifont)
        except AttributeError:
            self.status = StatusBar(self.game, self._player, self.zoom)
            self.display = [GameScreen(self.game, self._player,
                                       self.uifont, self.zoom,
                                       self._pushdisplay,
                                       self._popdisplay)]
                
    def makebackground(self):
        self.status.resize(self.statussurf.get_size())
        for d in self.display:
            d.resize(self.displaysurf.get_size())

    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)

        self.statussurf = self.screen.subsurface(Rect((0, size[1]-2 * self.uifont.get_linesize()),
                                                      (size[0],
                                                       2 * self.uifont.get_linesize())))
        self.displaysurf = self.screen.subsurface(Rect((0, 0),
                                                       (size[0], size[1]-2 * self.uifont.get_linesize())))
        
        self.makebackground()

    def _pushdisplay(self, child):
        self.display.append(child)
        self.definetiles()
        self.makebackground()

    def _popdisplay(self):
        del self.display[-1]
        self.definetiles()

    def step(self):
        for e in event.get():
            
            handled = self.display[-1].handle(e)
                
            if not handled:
                if e.type == QUIT:
                    self.game.done = True
                elif e.type == KEYDOWN:
                    pressed = key.get_pressed()
                    shifted = pressed[K_LSHIFT] or pressed[K_RSHIFT]
                    scroll = 10 if shifted else 1
                    
                    if e.key == K_ESCAPE:
                        self.game.done = True
                        
                    elif e.key == K_SPACE:
                        self.game.paused = not self.game.paused
                                            
                    elif e.unicode == '-':
                        timeindex = self.game.timescales.index(0.1 / self.game.dt)
                        if timeindex > 0:
                            timeindex -= 1
                            self.game.dt = 0.1 / self.game.timescales[timeindex]
                    elif e.unicode == '+':
                        timeindex = self.game.timescales.index(0.1 / self.game.dt)
                        if timeindex < len(self.game.timescales)-1:
                            timeindex += 1
                            self.game.dt = 0.1 / self.game.timescales[timeindex]
                        
                    elif e.unicode == 'd':
                        import pdb
                        pdb.set_trace()
                            
                elif e.type == MOUSEBUTTONUP:
                    if e.button == 4:
                        self.zoom.width += 2
                        self.zoom.height += 2
                        self.makescreen(self.screen.get_size())
                        self.definetiles()
                        
                    elif e.button == 5:
                        self.zoom.width = max(self.zoom.width - 2, 2)
                        self.zoom.height = max(self.zoom.height - 2, 4)
                        self.makescreen(self.screen.get_size())
                        self.definetiles()
                        
                elif e.type == VIDEORESIZE:
                    self.makescreen(e.size)
                    self.definetiles()

        self.display[-1].draw(self.displaysurf)
        self.status.draw(self.statussurf)

        display.flip()

        if self.game.done:
            self.game = None
            return None
        else:
            return self
