import pygame
from pygame import display, event, font, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

class Button(object):
    def __init__(self, font, text, click, centered=None):
        self.font = font
        self.text = text
        self.click = click
        self.location = None
        self.center = False if centered is None else centered

    def draw(self, screen):
        if self.location:
            s = self.font.render(self.text, True, (255,255,255))
            size = s.get_size()
            self.rect = Rect([self.location[i]-size[i]/2 for i in range(2)]
                             if self.center else self.location, size)
            screen.blit(s, self.rect.topleft)

    @property
    def size(self):
        return self.rect.size
    
    def handle(self, e):
        if (e.type == MOUSEBUTTONDOWN and e.button == 1 and
            self.rect.collidepoint(e.pos)):
            self.click()
            return True
