from pygame import draw, event, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Manufacturing
from makeitem import ChooseManufacturingItem

class ChooseManufacturingType(object):
    def __init__(self, playfield, font, prefs, showchild, dismiss):
        self._playfield = playfield
        self._bench = self._playfield.selection
        self._prefs = prefs
        self._showchild = showchild
        self._dismiss = dismiss
        
        self.scale(font)

    def _addbutton(self, surface, text, click, dy):
        button = Button(self._prefs, self._hotkeys, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]

    def _choose(self, job):
        return lambda: self._chooseitem(job)

    def _chooseitem(self, job):
        self._showchild(ChooseManufacturingItem(self._playfield.player,
                                                job.substance,
                                                self._font,
                                                self._prefs,
                                                self._showchild,
                                                self._chose,
                                                self._dismisschild))

    def _chose(self, item, substance):
        self._bench.jobs.append((item, substance))
        self._dismiss()

    def _dismisschild(self):
        self._dismiss()
        self._background = None
                
    def _makebackground(self, size):
        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        dy = 0

        self._hotkeys = []
        self._buttons = []
        for job in Manufacturing.__subclasses__():
            dy = self._addbutton(self._background,
                                 job.noun.capitalize(),
                                 self._choose(job),
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
                self._playfield.selection = None
                return True
        
        for button in self._buttons:
            if button.handle(e):
                return True
                
        return False

    def draw(self, surface):
        if self._playfield.selection != self._bench:
            self._dismiss()
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
