from random import randint, random

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

def conj(items):
    if not len(items):
        return ''
    elif len(items) == 1:
        return str(items[0])
    elif len(items) == 2:
        return ' and '.join(items)
    else:
        return ', and '.join([', '.join(items[:-1]), items[-1]])

t = 52000 + randint(-1000,1000)

months = [
    ('January', 31),
    ('February', 28),
    ('March', 31),
    ('April', 30),
    ('May', 31),
    ('June', 30),
    ('July', 31),
    ('August', 31),
    ('September', 30),
    ('October', 31),
    ('November', 30),
    ('December', 31)
    ]

def date(t):
    year = t/52
    day = 7 * (t - 52 * year)
    for m in months:
        if day - m[1] > 0:
            day -= m[1]
        else:
            month = m[0]
            break
    else:
        month = months[-1]
    return ' '.join(['In',month,'of year',str(year)])

print date(t), 'a struggle for power between the', conj([f.name for f in
                                                             society.factions])

ruler = None
underclass = None
uprising = None

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
        t += 1

        hierarchy = sorted(society.factions, key=lambda f: f.status, reverse=True)
        
        if hierarchy[0].status == 1:
            if hierarchy[0] != ruler:           
                ruler = hierarchy[0]
                state = (' '.join(['overthrows the', uprising.name])
                         if uprising and ruler == underclass
                         else 'takes over in the power vacuum')
                print date(t), 'the', ruler.name, state

                uprising = None
        else:
            ruler = None

        if hierarchy[-1].status == 0:
            if hierarchy[-1] != underclass:
                underclass = hierarchy[-1]
                print date(t), 'the', ruler.name, 'represses the', underclass.name

        if underclass and underclass.overthrow and underclass.overthrow != uprising:
            uprising = underclass.overthrow
            print date(t), 'the oppressed', underclass.name, 'revolts against the ruling', uprising.name

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
