from string import letters

import pygame
from pygame import display, event, font, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

class Button(object):
    def __init__(self, prefs, hotkeys, text, click, centered=None):
        self.font = prefs.font
        self.hotkeycolor = prefs.hotkeycolor
        for c in text.lower():
            if c in letters and c not in hotkeys:
                self.hotkey = c
                hotkeys.append(self.hotkey)
                break
        else:
            for i in range(1, 11):
                c = unicode(i % 10)
                if c not in hotkeys:
                    self.hotkey = c
                    hotkeys.append(self.hotkey)
                    break
            else:
                self.hotkey = None
            
        self.text = text
        if self.hotkey:
            self.text = u': {text}'.format(text=self.text)
        self.click = click
        self.location = None
        self.center = False if centered is None else centered

    def draw(self, screen):
        if self.location:
            s = self.font.render(self.text, True, (255,255,255))
            
            if self.hotkey:
                h = self.font.render(self.hotkey, True, self.hotkeycolor)
                t = Surface((h.get_width() + s.get_width(),
                             max(h.get_height(), s.get_height())),
                            flags = s.get_flags())
                t.blit(h, (0, 0))
                t.blit(s, (h.get_width(), 0))
                s = t
                
            size = s.get_size()
            self.rect = Rect([self.location[i]-size[i]/2 for i in range(2)]
                             if self.center else self.location, size)
            screen.blit(s, self.rect.topleft)

    @property
    def size(self):
        return self.rect.size
    
    def handle(self, e):
        if ((e.type == MOUSEBUTTONDOWN and e.button == 1 and
             self.rect.collidepoint(e.pos)) or
            (self.hotkey and e.type == KEYDOWN and e.unicode == self.hotkey)):
            self.click()
            return True
