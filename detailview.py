from pygame import Surface
from pygame.locals import *

from button import Button
from text import TextRenderer

class DetailView(object):
    def __init__(self, playfield, font, prefs,
                 showchild, dismiss, pushscreen, popscreen):
        self.playfield = playfield
        self.prefs = prefs
        self.showchild = showchild
        self.dismiss = dismiss
        self.pushscreen = pushscreen
        self.popscreen = popscreen

        self.scale(font)

        self._buttons = []        

    def addline(self, surface, text, color, dy):
        image = self._renderer.render(text, color)
        surface.blit(image, (0,dy))
        return dy + image.get_height()

    def addbutton(self, surface, text, click, dy):
        button = Button(self.prefs, self._hotkeys, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]

    def addlines(self, surface, dy):
        return dy
        
    def addbuttons(self, surface, dy):
        return dy
        
    def _makebackground(self, size):
        self._renderer = TextRenderer(self.font, size[0])

        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        dy = self.addlines(self._background, 0)

        self._hotkeys = []
        del self._buttons[:]

        dy = self.addbuttons(self._background, dy)

    def refresh(self):
        self._background = None

    def dismisschild(self):
        self.dismiss()
        self.refresh()

    def scale(self, font):
        self.font = font
        self.refresh()

    def resize(self, size):
        pass

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                self.playfield.selection = None
                return True
            
        for button in self._buttons:
            if button.handle(e):
                return True
        
        return False

    def draw(self, surface):
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
