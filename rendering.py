from pygame import display, event, font, key, Rect
from pygame.locals import *

from screen import GameScreen
from status import StatusBar

class Renderer(object):
    dt = 0.05
    
    def __init__(self, game, zoom):
        self.game = game
        self.zoom = zoom
        
        self.definetiles()

        self.makescreen(display.get_surface().get_size())

    def definetiles(self):
        self.uifont = font.Font('FreeMono.ttf',
                                max(self.zoom.width, self.zoom.height))
        try:
            self.status.scale(self.uifont)
            self.display.scale(self.uifont)
        except AttributeError:
            self.status = StatusBar(self.game, self.uifont)
            self.display = GameScreen(self.game, self.uifont, self.zoom)
                
    def makebackground(self):
        self.status.resize(self.statussurf.get_size())
        self.display.resize(self.displaysurf.get_size())

    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)

        self.statussurf = self.screen.subsurface(Rect((0, size[1]-self.uifont.get_linesize()),
                                                      (size[0],
                                                       self.uifont.get_linesize())))
        self.displaysurf = self.screen.subsurface(Rect((0, 0),
                                                       (size[0], size[1]-self.uifont.get_linesize())))
        
        self.makebackground()

    def step(self):
        for e in event.get():
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

            self.display.handle(e)

        self.display.draw(self.displaysurf)
        self.status.draw(self.statussurf)

        display.flip()

        if self.game.done:
            self.game = None
            return None
        else:
            return self
