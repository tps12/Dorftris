from pygame import draw, event, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button

class DirectTree(object):
    # N, S, NE, NW, SE, SW
    arrows = u'\u2b06',u'\u2b07',u'\u2b08',u'\u2b09',u'\u2b0a',u'\u2b0b'
    
    def __init__(self, player, location, font, prefs, dismiss):
        self._player = player
        self._location = location
        self._prefs = prefs
        self._dismiss = dismiss
        
        self.scale(font)

    def _addbutton(self, surface, text, click, dy):
        button = Button(self._prefs, self._hotkeys, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]

    def _directer(self, direction):
        return lambda: self._direct(direction)

    def _direct(self, direction):
        self._player.felltree(self._location, direction)
        self._dismiss()
                
    def _makebackground(self, size):
        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        dy = 0

        self._hotkeys = []
        self._buttons = []
        for i in range(len(self.arrows)):
            dy = self._addbutton(self._background,
                                 self.arrows[i],
                                 self._directer(i),
                                 dy)
            
        if not self._buttons:
            self._dismiss()
   
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                self._dismiss()
                return True
        
        for button in self._buttons:
            if button.handle(e):
                return True
                
        return False

    def draw(self, surface):
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
