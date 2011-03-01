from detailview import DetailView
from data import Creature, CulturedCreature
from desc import CreatureDescription
from labors import LaborSelection

class CreatureDetails(DetailView):
    def __init__(self, creature, playfield, font, prefs,
                 dismiss, pushscreen, popscreen):
        DetailView.__init__(self, playfield, font, prefs, None, dismiss,
                            pushscreen, popscreen)
        self._creature = creature
        self._activity = self._creature.activity
        
    def addlines(self, surface, dy):
        dy = self.addline(surface,
                          self._creature.namecard(),
                          self.prefs.selectioncolor,
                          dy)
        dy = self.addline(surface,
                          self._creature.noun,
                          (255,255,255),
                          dy)
        dy = self.addline(surface,
                          self._creature.activity,
                          (255,255,255),
                          dy)
        return dy
    
    def addbuttons(self, surface, dy):
        dy = self.addbutton(surface,
                            _(u'Description'),
                            self._details,
                            dy)
        if self.playfield.player == self._creature.player:
            dy = self.addbutton(surface,
                                _(u'Labors'),
                                self._labors,
                                dy)
        if self.prefs.debugging:
            dy = self.addbutton(surface,
                                _(u'Debug'),
                                self._debug,
                                dy)
        return dy

    def _debug(self):
        self._creature.debug = True

    def _details(self):
         self.pushscreen(CreatureDescription(self._creature, self.font,
                                             self.popscreen))

    def _labors(self):
        self.pushscreen(LaborSelection(self._creature, self.font,
                                       self.popscreen))
    
    def draw(self, surface):
        if self.playfield.selection != self._creature:
            self.dismiss()
        
        activity = self._creature.activity
        if self._activity != activity:
            self._activity = activity
            self.refresh()

        super(CreatureDetails, self).draw(surface)        
