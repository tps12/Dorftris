from pygame import draw, event, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Item
from makesubstance import ChooseManufacturingSubstance

class ChooseManufacturingItem(object):
    def __init__(self, player, substance, font, prefs, showchild, chose, dismiss):
        self._player = player
        self._substance = substance
        self._prefs = prefs
        self._showchild = showchild
        self._chose = chose
        self._dismiss = dismiss
        
        self.scale(font)

    def _qualifyingitems(self, itemclass, substance):
        items = []
        for child in itemclass.__subclasses__():
            items.extend(self._qualifyingitems(child, substance))
        if itemclass.substancetest(substance) and hasattr(itemclass, 'noun'):
            items.append(itemclass)
        return items

    def _addbutton(self, surface, text, click, dy):
        button = Button(self._prefs, self._hotkeys, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]

    def _choose(self, item):
        return lambda: self._chooseitem(item)

    def _chooseitem(self, item):
        self._showchild(ChooseManufacturingSubstance(self._player,
                                                     self._substance,
                                                     self._font,
                                                     self._prefs,
                                                     self._choosesubstance(item),
                                                     self._dismisschild))

    def _choosesubstance(self, item):
        return lambda s: self._chosesubstance(item, s)

    def _chosesubstance(self, item, substance):
        self._chose(item, substance)
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
        for item in self._qualifyingitems(Item, self._substance):
            dy = self._addbutton(self._background,
                                 item.noun.capitalize(),
                                 self._choose(item),
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
