from random import random

import pygame
from pygame import display, draw, event, font, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from factions import *

pygame.init()

screen = display.set_mode((800,600),HWSURFACE)
display.set_caption('Regime Change')

background = Surface(screen.get_size())
background.fill((128,128,128))

text = font.SysFont('Courier', 10)

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
for f in society.factions:
    for v in f.values.keys():
        f.values[v] = random()

charts = [chart.subsurface(Rect(i * chart.get_width()/len(society.factions),
                                0,
                                chart.get_width()/len(society.factions),
                                chart.get_height()))
          for i in range(len(society.factions))]

done = False
paused = False

while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                done = True
            elif e.key == K_SPACE:
                paused = not paused

    if not paused:
        society.iterate()

        # scroll
        old = plot.copy()
        plot.blit(old, (0,0), Rect(1,0,old.get_width()-1,old.get_height()))
        plot.fill((0,0,0), Rect(plot.get_width()-2,0,1,plot.get_height()))
    
    for i in range(len(society.factions)):
        f = society.factions[i]
        
        # draw current status
        plot.set_at((plot.get_width()-2,
                     int((1-f.status) * (plot.get_height()-1))),
                    f.color)

        # draw chart
        c = charts[i]
        c.fill((0,0,0))
        c.blit(text.render(f.name, True, f.color), (0,0))

        vs = f.values.keys()
        for i in range(len(vs)):
            h = c.get_height() - 2 * text.get_height()
            h = int(f.values[vs[i]] * h)
            c.fill((255,255,255), Rect(i * c.get_width()/len(vs),
                                       c.get_height() - h - text.get_height(),
                                       c.get_width()/len(vs),
                                       h))
            
            c.blit(text.render(vs[i], True, (255,255,255)),
                   (i * c.get_width()/len(vs),
                    c.get_height() - text.get_height()))
                
    screen.blit(background, (0,0))

    display.flip()
