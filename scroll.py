from pygame.locals import *

class Scroll(object):
    def __init__(self, font, prefs):
        self._prefs = prefs       
        self._offset = 0
        
        self.scale(font)
    
    def scale(self, font):
        self._font = font

    def handle(self, e):
        pass

    def draw(self, surface, content):
        surface.blit(content, (0, self._offset))

        if content.get_height() > surface.get_height():
            up = self._font.render(u'\u25b3', True, (255,255,255))
            w = surface.get_width() - up.get_width()
            surface.blit(up, (w, 0))
            down = self._font.render(u'\u25bd', True, (255,255,255))
            surface.blit(down, (w, surface.get_height() - down.get_height()))
