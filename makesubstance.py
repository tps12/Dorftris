from pygame import draw, event, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Item

class ChooseManufacturingSubstance(object):
    def __init__(self, player, substance, font, prefs, dismiss):
        self._player = player
        self._substance = substance
        self._prefs = prefs
        self._dismiss = dismiss
        
        self.scale(font)

    def _childsubstances(self, substance):
        substances = []
        for child in substance.__subclasses__():
            substances.extend(self._childsubstances(child))
        if hasattr(substance, 'adjective'):
            substances.append(substance)
        return substances

    def _addbutton(self, surface, text, click, dy):
        button = Button(self._font, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]

    def _choose(self, substance):
        return lambda: self._choosesubstance(substance)

    def _choosesubstance(self, substance):
        print 'chose', substance
        self._dismiss()
                
    def _makebackground(self, size):
        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        dy = 0

        self._buttons = []
        dy = self._addbutton(self._background,
                             _(u'Any {substance}').format(substance=
                                                          self._substance.noun),
                             self._choose(self._substance),
                             dy)
        
        for substance in self._childsubstances(self._substance):
            dy = self._addbutton(self._background,
                                 substance.noun.capitalize(),
                                 self._choose(substance),
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
        
        elif (e.type == MOUSEBUTTONDOWN and
            e.button == 1):
            for button in self._buttons:
                if button.handle(e):
                    return True
                
        return False

    def draw(self, surface):
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
