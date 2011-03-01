from detailview import DetailView
from data import Item

class ChooseManufacturingSubstance(DetailView):
    def __init__(self, playfield, substance, font, prefs, chose, dismiss):
        DetailView.__init__(self, playfield, font, prefs, None, dismiss,
                            None, None)
        self._substance = substance
        self._chose = chose

    def _childsubstances(self, substance):
        substances = []
        for child in substance.__subclasses__():
            substances.extend(self._childsubstances(child))
        if hasattr(substance, 'adjective'):
            substances.append(substance)
        return substances

    def _choose(self, substance):
        return lambda: self._choosesubstance(substance)

    def _choosesubstance(self, substance):
        self._chose(substance)
        self.dismiss()

    def addbuttons(self, surface, dy):
        dy = self.addbutton(surface,
                            _(u'Any {substance}').format(substance=
                                                         self._substance.noun),
                            self._choose(self._substance),
                            dy)
        
        for substance in self._childsubstances(self._substance):
            dy = self.addbutton(surface,
                                substance.noun.capitalize(),
                                self._choose(substance),
                                dy)
        return dy
