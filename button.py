import pygame
from pygame import display, event, font, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

class Button(object):
    def __init__(self, font, text, click):
        self.font = font
        self.text = text
        self.click = click
        self.location = None

    def draw(self, screen):
        if self.location:
            s = self.font.render(self.text, True, (255,255,255))
            size = s.get_size()
            self.rect = Rect([self.location[i]-size[i]/2 for i in range(2)],
                             size)
            screen.blit(s, self.rect.topleft)

    @property
    def size(self):
        return self.rect.size
    
    def handle(self, e):
        if (e.type == MOUSEBUTTONUP and e.button == 1 and
            self.rect.collidepoint(e.pos)):
            self.click()
