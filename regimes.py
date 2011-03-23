from random import random

import pygame
from pygame import display, draw, event, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

pygame.init()

screen = display.set_mode((800,600),HWSURFACE)
display.set_caption('Regime Change')

background = Surface(screen.get_size())
background.fill((128,128,128))

screen.blit(background, (0,0))

done = False

while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                done = True

    display.flip()
