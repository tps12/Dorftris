from random import choice, randint
from time import time

import pygame
from pygame import display, event, font, key
from pygame.locals import *

from button import Button
from data import Barrel, Dwarf, Goblin, Oak, SmallSpider, Tortoise
from game import Game
from rendering import Renderer
from zoom import TileDimensions

class MainMenu(object):
    dt = 0.01
    
    def __init__(self):
        self.game = None
        
        pygame.init()

        key.set_repeat(100, 100)

        self.zoom = TileDimensions(16, 18)
        
        self.definefont()

        self.makescreen((1400,800))

        display.set_caption(_('Hex Grid'))

        self.child = None
        self.done = False

    def definefont(self):
        self.uifont = font.Font('FreeMono.ttf',
                                max(self.zoom.width,
                                    self.zoom.height))

    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)
        self.draw()

    def draw(self):
        self.screen.fill((0,0,0))

        self.buttons = [
            Button(self.uifont, _('New Game'), self.newgame),
            Button(self.uifont, _('Quit'), self.quitgame)
            ]

        size = self.screen.get_size()
        y = size[1]/2

        for b in self.buttons:
            b.location = (size[0]/2, y)
            b.draw(self.screen)
            y += b.size[1]

    def newgame(self):
        self.game = Game((156, 104, 128))

        for i in range(20):
            self.game.world.space.maketree((randint(0, self.game.dimensions[0]-1),
                           randint(0, self.game.dimensions[1]-1),
                           64))    

        kind = (Dwarf,Goblin,Tortoise,SmallSpider)

        for i in range(20):
            creature = choice(kind)((randint(0,self.game.dimensions[0]-1),
                                     randint(0,self.game.dimensions[1]-1),
                                     64))
            self.game.schedule(creature)

        for i in range(10):
            self.game.world.additem(Barrel((randint(0,self.game.dimensions[0]-1),
                                            randint(0,self.game.dimensions[1]-1),
                                            64),
                                           Oak))

        self.child = Renderer(self.game, self.zoom)

    def quitgame(self):
        self.done = True

    def step(self):
        if self.child:
            self.definefont()
            self.makescreen(self.screen.get_size())
            self.child = None
        
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
