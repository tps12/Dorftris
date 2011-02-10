from pygame import draw, event, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Creature, CulturedCreature
from desc import CreatureDescription
from labors import LaborSelection
from text import TextRenderer

class CreatureDetails(object):
    def __init__(self, creature, playfield, font, prefs):
        self._creature = creature
        self._playfield = playfield
        self._activity = self._creature.activity
        self._prefs = prefs
        self._showdetails = False
        self._showlabors = False
        
        self.scale(font)

    def _addline(self, surface, text, color, dy):
        image = self._renderer.render(text, color)
        surface.blit(image, (0,dy))
        return dy + image.get_height()

    def _addbutton(self, surface, text, click, dy):
        button = Button(self._font, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]
        
    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])

        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        dy = 0
        dy = self._addline(self._background,
                           self._creature.namecard(),
                           self._prefs.selectioncolor,
                           dy)
        dy = self._addline(self._background,
                           self._creature.noun,
                           (255,255,255),
                           dy)
        dy = self._addline(self._background,
                           self._creature.activity,
                           (255,255,255),
                           dy)

        self._buttons = []
        dy = self._addbutton(self._background,
                             _(u'Description'),
                             self._details,
                             dy)
        if self._playfield.player == self._creature.player:
            dy = self._addbutton(self._background,
                                 _(u'Labors'),
                                 self._labors,
                                 dy)
        if self._prefs.debugging:
            dy = self._addbutton(self._background,
                                 _(u'Debug'),
                                 self._debug,
                                 dy)

    def _debug(self):
        self._creature.debug = True

    def _details(self):
        self._showdetails = True

    def _labors(self):
        self._showlabors = True
    
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                return True, False, None
        
        elif (e.type == MOUSEBUTTONDOWN and
            e.button == 1):
            for button in self._buttons:
                if button.handle(e):
                    break
        
        if self._showdetails:
            self._showdetails = False
            return True, False, CreatureDescription(self._creature, self._font)

        if self._showlabors:
            self._showlabors = False
            return True, False, LaborSelection(self._creature, self._font)
        
        return False, False, self

    def draw(self, surface):
        if self._playfield.selection != self._creature:
            event.post(event.Event(KEYDOWN,
                                   {'key': K_ESCAPE, 'unicode': None, 'mod': None}))
        
        activity = self._creature.activity
        if self._activity != activity:
            self._background = None
            self._activity = activity
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
