from random import random

import pygame
from pygame import display, draw, event, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from factions import *

pygame.init()

screen = display.set_mode((800,600),HWSURFACE)
display.set_caption('Regime Change')

background = Surface(screen.get_size())
background.fill((128,128,128))

plot = background.subsurface(Rect(0,
                                  0,
                                  background.get_width(),
                                  background.get_height()/2))
chart = background.subsurface(Rect(0,
                                   plot.get_height(),
                                   background.get_width(),
                                   background.get_height()-plot.get_height()))

values = 'militarism', 'moralism'
society = Society([Faction('aristocracy', (0,0,255), random(), values),
                   Faction('merchant class', (0,255,0), random(), values),
                   Faction('populace', (255,0,0), random(), values)])

done = False

while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                done = True

    old = plot.copy()
    plot.blit(old, (0,0), Rect(1,0,old.get_width()-1,old.get_height()))
    plot.fill((0,0,0), Rect(plot.get_width()-2,0,1,plot.get_height()))
                
    screen.blit(background, (0,0))

    display.flip()
