from random import choice, randint
from time import time

import pygame
from pygame import display, event, font, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import Sound
from pygame.sprite import *
from pygame.time import Clock

from button import Button
from data import Barrel, Beverage, Corpse, Entity, Stockpile
from glyphs import GlyphGraphics

class MainMenu(object):
    dt = 0.01
    
    def __init__(self):
        self.game = None
        
        pygame.init()

        key.set_repeat(100, 100)

        self.tile_width = 16
        self.tile_height = 18
        
        self.definefont()

        self.makescreen((1400,800))

        display.set_caption(_('Hex Grid'))

    def definefont(self):
        self.uifont = font.Font('FreeMono.ttf',
                                max(self.tile_width, self.tile_height))

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
        print 'new game'

    def quitgame(self):
        print 'quit'

    def step(self):
        done = False
        
        for e in event.get():
            if e.type == QUIT:
                done = True
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    done = True
                    
            elif e.type == MOUSEBUTTONUP:
                if e.button == 4:
                    # zoom in
                    self.tile_width += 2
                    self.tile_height += 2
                    self.definefont()
                    self.draw()
                    
                elif e.button == 5:
                    # zoom out
                    self.tile_width = max(self.tile_width - 2, 2)
                    self.tile_height = max(self.tile_height - 2, 4)
                    self.definefont()
                    self.draw()
                    
            elif e.type == VIDEORESIZE:
                self.makescreen(e.size)

            for b in self.buttons:
                b.handle(e)

        display.flip()

        return self if not done else None
