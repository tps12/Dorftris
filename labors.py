from pygame import Rect, Surface
from pygame.locals import *

from data import LaborOptions
from scroll import Scroll
from tree import TreeOptions

class LaborSelection(object):
    dt = 0.01
    
    def __init__(self, creature, font, dismiss):
        self._creature = creature
        self._dismiss = dismiss
        self._tree = TreeOptions(self._laboroptions(), font, None, self.changed)

        self.scale(font)

    def _laboroptions(self, branch = None):
        if not branch:
            return [self._laboroptions(cat) for cat in LaborOptions]
            
        if hasattr(branch, '__iter__'):
            return branch, branch[0], [self._laboroptions(child)
                                       for child in branch[1]]
        else:
            return branch, branch.noun, (branch in self._creature.labors)

    def _makebackground(self, size):
        self._background = Surface(size, flags = SRCALPHA)
        
        self._scroll.draw(self._background, self._tree.draw())

    def changed(self):
        del self._creature.labors[:]
        self._creature.labors.extend(self._tree.selected())
        
        self._background = None

    def scrolled(self):
        self._background = None

    def scale(self, font):
        self._font = font
        
        self._background = None
        self._scroll = Scroll(self._font, None, self.scrolled)
        self._tree.scale(self._font)

    def resize(self, size):
        self._background = None

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                self._dismiss()
                return True

        if self._tree.handle(e):
            self._background = None
            return True

        return False

    def draw(self, surface):
        if self._scroll.poll():
            self._background = None
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
