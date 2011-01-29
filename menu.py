from random import choice, randint
from time import time

import pygame
from pygame import display, event, font, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import Sound
from pygame.sprite import *
from pygame.time import Clock

from data import Barrel, Beverage, Corpse, Entity, Stockpile
from glyphs import GlyphGraphics

INFO_WIDTH = 20
STATUS_HEIGHT = 2

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
        self.drawback()

    def drawback(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.uifont.render('Hello', True, (0,255,255)),
                         (self.screen.get_width()/2, self.screen.get_height()/2))

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
                    self.tile_width += 2
                    self.tile_height += 2
                    self.definefont()
                    self.drawback()
                    
                elif e.button == 5:
                    self.tile_width = max(self.tile_width - 2, 2)
                    self.tile_height = max(self.tile_height - 2, 4)
                    self.definefont()
                    self.drawback()
                    
            elif e.type == VIDEORESIZE:
                self.makescreen(e.size)

        display.flip()

        return self if not done else None
