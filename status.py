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

class StatusBar(object):
    pausestring = _('*** PAUSED ***')
    timestrings = [
        _(u'\u2155 speed'),
        _(u'\u00bd speed'),
        _('Normal speed'),
        _(u'2\u00d7 speed'),
        _(u'5\u00d7 speed')
        ]
    fpsstring = _('{num:d} {g}FPS')

    def __init__(self, game, font):
        self.game = game

        self.sprites = LayeredDirty()

        self.zoom(font)

        self.paused = None
        self.timeindex = -1
        self.fps = []

    def _sprite(self, text, color = None):
        color = color if color is not None else (255,255,255)
        
        sprite = DirtySprite()
        sprite.image = self.font.render(text, True, color)
        sprite.rect = sprite.image.get_rect()

        return sprite

    def zoom(self, font):
        self.font = font
        
        self.sprites.empty()

        self.pausesprite = self._sprite(self.pausestring)
        self.timesprites = [self._sprite(t) for t in self.timestrings]
        self.fpssprites = [self._sprite(self.fpsstring.format(num=9999, g=g))
                           for g in '','G']

        apply(self.sprites.add,
              [self.pausesprite] + self.timesprites + self.fpssprites)

    def draw(self, surface):
        paused = self.game.paused
        if self.paused != paused:
            self.paused = paused

        timeindex = self.game.timescales.index(0.1 / self.game.dt)
        if self.timeindex != timeindex:
            del self.fps[:]
