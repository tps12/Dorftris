from collections import deque
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

        self.clock = Clock()
        self.lasttime = None
        self.fps = deque()

    def _sprite(self, text, x, color = None):
        color = color if color is not None else (255,255,255)
        
        sprite = DirtySprite()
        sprite.image = self.font.render(text, True, color)
        sprite.rect = sprite.image.get_rect().move(x, 0)

        return sprite

    def zoom(self, font):
        self.font = font

        self.background = None
        
        self.sprites.empty()

        x = 0
        self.pausesprite = self._sprite(self.pausestring, x)
        x += self.pausesprite.rect.width
        self.timesprites = [self._sprite(t, x) for t in self.timestrings]
        x += max([s.rect.width for s in self.timesprites])
        self.fpssprites = [self._sprite(self.fpsstring.format(num=9999, g=g), x)
                           for g in '','G']
        self.fpssprites[1].rect.move_ip(self.fpssprites[1].rect.width, 0)

        apply(self.sprites.add,
              [self.pausesprite] + self.timesprites + self.fpssprites)

        self._dirty()

    def _dirty(self):
        self.paused = None
        self.timeindex = -1

    def resize(self, size):
        self.background = Surface(size, flags=SRCALPHA)
        self.background.fill((0,0,0))

        self._dirty()

    def draw(self, surface):
        paused = self.game.paused
        if self.paused != paused:
            self.paused = paused
            self.pausesprite.visible = self.paused
            self.pausesprite.dirty = True

        timeindex = self.game.timescales.index(0.1 / self.game.dt)
        if self.timeindex != timeindex:
            self.timeindex = timeindex
            for i in range(len(self.timesprites)):
                self.timesprites[i].visible = i == self.timeindex
                self.timesprites[i].dirty = True
            self.fps.clear()

        if not self.lasttime:
            self.lasttime = self.game.t, time()
        else:
            if self.paused:
                fps = 0
                self.lasttime = self.game.t, time()
            else:
                frames = self.game.t - self.lasttime[0]
                t = time()
                secs = t - self.lasttime[1]
                if secs > 0:
                    if len(self.fps) > 20:
                        self.fps.popleft()
                    self.fps.append(frames/secs)
                    fps = sum(self.fps)/len(self.fps)
                else:
                    fps = None

                self.lasttime = self.game.t, t

            if fps is not None:
                image = self.font.render(
                    self.fpsstring.format(num=int(fps+0.5), g=''),
                    True, (255,255,255))
                self.fpssprites[0].image.fill((0,0,0))
                self.fpssprites[0].image.blit(image,
                                              (self.fpssprites[0].rect.width-
                                               image.get_width(), 0))

            self.fpssprites[0].dirty = True

        image = self.font.render(
            self.fpsstring.format(num=int(self.clock.get_fps()+0.5), g='G'),
            True, (255,255,255))
        self.fpssprites[1].image.fill((0,0,0))
        self.fpssprites[1].image.blit(image,
                                      (self.fpssprites[1].rect.width-
                                       image.get_width(), 0))
        self.fpssprites[1].dirty = True

        self.sprites.clear(surface, self.background)
        self.sprites.draw(surface)

        self.clock.tick()
