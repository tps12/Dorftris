from pygame.locals import *

from scrollbutton import ScrollButton

class Scroll(object):
    glyphs = (u'\u25b3',u'\u25b2'), (u'\u25bd',u'\u25bc')
    
    def __init__(self, font, prefs):
        self._prefs = prefs       
        self._offset = 0
        self._buttons = [ScrollButton(self.glyphs[i],
                                      font,
                                      self._prefs,
                                      (self.up, self.down)[i])
                         for i in range(2)]
        
        self.scale(font)
    
    def scale(self, font):
        self._font = font
        for b in self._buttons:
            b.scale(self._font)

    def up(self):
        if self._offset > 0:
            self._offset -= 1

    def down(self):
        self._offset += 1

    def handle(self, e):
        for b in self._buttons:
            if b.poll():
                return True

        return False

    def draw(self, surface, content):
        surface.blit(content, (0, self._offset))

        if content.get_height() > surface.get_height():
            up = self._buttons[0].draw()
            w = surface.get_width() - up.get_width()
            surface.blit(up, (w, 0))
            down = self._buttons[1].draw()
            surface.blit(down, (w, surface.get_height() - down.get_height()))
