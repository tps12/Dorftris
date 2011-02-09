from pygame import mouse, Rect
from pygame.locals import *

from scrollbutton import ScrollButton

class Scroll(object):
    glyphs = (u'\u25b3',u'\u25b2'), (u'\u25bd',u'\u25bc')
    
    def __init__(self, font, prefs, moved):
        self._prefs = prefs       
        self._offset = 0
        self._buttons = [ScrollButton(self.glyphs[i],
                                      font,
                                      self._prefs,
                                      (self.up, self.down)[i])
                         for i in range(2)]
        self._rects = [None for b in self._buttons]
        self._moved = moved
        
        self.scale(font)
    
    def scale(self, font):
        self._font = font
        for b in self._buttons:
            b.scale(self._font)

    @property
    def _increment(self):
        return self._buttons[0].height / 2

    def up(self):
        self._offset = max(0, self._offset - self._increment)
        self._moved()

    def down(self):
        self._offset = min(self._limit, self._offset + self._increment)
        self._moved()

    def poll(self):
        for i in range(len(self._buttons)):
            if (self._rects[i] and
                self._rects[i].collidepoint(mouse.get_pos()) and
                self._buttons[i].poll()):
                return True
            
        return False

    def draw(self, surface, content):
        surface.fill((0,0,0))
        surface.blit(content, (0, -self._offset))

        if content.get_height() > surface.get_height():
            for i in range(2):
                sb = self._buttons[i].draw()
                w = surface.get_width() - sb.get_width()
                h = surface.get_height() - sb.get_height() if i else 0
                self._rects[i] = Rect((w, h), sb.get_size())
                surface.blit(sb, (w,h))
            self._limit = content.get_height() - surface.get_height()
        else:
            self._limit = 0
