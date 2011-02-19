from random import choice, randint
from time import time

import pygame
from pygame import display, event, font, key
from pygame.locals import *

from button import Button
from data import Ax, Barrel, Pickax, Dwarf, Goblin, SmallSpider, Tortoise, Player, Workbench
from game import Game
from rendering import Renderer
from substances import Wood, Metal
from prefs import DisplayOptions
from world import RenderWorld

class MainMenu(object):
    dt = 0.01
    
    def __init__(self):
        self.game = None
        
        pygame.init()

        key.set_repeat(100, 100)

        self.zoom = DisplayOptions('FreeMono.ttf', False, 16, 18)
        
        self.definefont()

        self.makescreen((1400,800))

        display.set_caption(_(u'Hex Grid'))

        self.child = None
        self.done = False

    def definefont(self):
        self._font = self.zoom.font

    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)
        self.draw()

    def draw(self):
        self.screen.fill((0,0,0))

        self.buttons = [
            Button(self._font, _(u'New Game'), self.newgame, True),
            Button(self._font, _(u'Make World'), self.world, True),
            Button(self._font, _(u'Quit'), self.quitgame, True)
            ]

        size = self.screen.get_size()
        y = size[1]/2

        for b in self.buttons:
            b.location = (size[0]/2, y)
            b.draw(self.screen)
            y += b.size[1]

    def newgame(self):
        self.game = Game((156, 104, 128))
        user = Player(self.game.world)
        
        for i in range(20):
            x, y = [randint(0, self.game.dimensions[i]-1) for i in range(2)]
            self.game.world.space.maketree((x,y,
                                            self.game.world.space.groundlevel(x,y)))

        kind = (Dwarf,Goblin,Tortoise,SmallSpider)

        for i in range(20):
            race = choice(kind)
            player = user if race is Dwarf else None
            x, y = [randint(0, self.game.dimensions[i]-1) for i in range(2)]
            creature = race(player, (x,y,self.game.world.space.groundlevel(x,y)))
            self.game.schedule(creature)

        for i in range(10):
            x, y = [randint(0, self.game.dimensions[i]-1) for i in range(2)]
            self.game.world.additem(Barrel((x,y,
                                            self.game.world.space.groundlevel(x,y)),
                                           choice(Wood.__subclasses__())))

        x, y = [randint(0, self.game.dimensions[i]-1) for i in range(2)]
        self.game.world.additem(Pickax((x,y,
                                        self.game.world.space.groundlevel(x,y)),
                                       choice(Metal.__subclasses__()),
                                       choice(Wood.__subclasses__())))


        x, y = [randint(0, self.game.dimensions[i]-1) for i in range(2)]
        self.game.world.additem(Ax((x,y,
                                    self.game.world.space.groundlevel(x,y)),
                                   choice(Metal.__subclasses__()),
                                   choice(Wood.__subclasses__())))

        x, y = [randint(0, self.game.dimensions[i]-1) for i in range(2)]
        self.game.world.additem(Workbench((x,y,
                                        self.game.world.space.groundlevel(x,y)),
                                       choice(Wood.__subclasses__())))

        self.child = Renderer(self.game, user, self.zoom)

        user.foundsettlement('the fortress')

    def world(self):
        self.child = RenderWorld(self.zoom)

    def quitgame(self):
        self.done = True

    def step(self):
        if self.child:
            self.definefont()
            self.makescreen(self.screen.get_size())
            self.child = None

        if not self.game:
            self.newgame()
        else:
            self.done = True
        
        for e in event.get():
            if e.type == QUIT:
                self.done = True
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.done = True
                    
            elif e.type == MOUSEBUTTONUP:
                if e.button == 4:
                    # zoom in
                    self.zoom.width += 2
                    self.zoom.height += 2
                    self.definefont()
                    self.draw()
                    
                elif e.button == 5:
                    # zoom out
                    self.zoom.width = max(self.zoom.width - 2, 2)
                    self.zoom.height = max(self.zoom.height - 2, 4)
                    self.definefont()
                    self.draw()
                    
            elif e.type == VIDEORESIZE:
                self.makescreen(e.size)

            for b in self.buttons:
                b.handle(e)

        display.flip()

        if self.done:
            return None
        elif self.child:
            return self.child
        else:
            return self
