from detailview import DetailView
from data import SimpleItem
from makesubstance import ChooseManufacturingSubstance

class ChooseManufacturingItem(DetailView):
    def __init__(self, playfield, substance, font, prefs, showchild, chose, dismiss):
        DetailView.__init__(self, playfield, font, prefs, showchild, dismiss,
                            None, None)

        self._substance = substance
        self._chose = chose

    def _qualifyingitems(self, itemclass, substance):
        items = []
        for child in itemclass.__subclasses__():
            items.extend(self._qualifyingitems(child, substance))
        if itemclass.substancetest(substance) and hasattr(itemclass, 'noun'):
            items.append(itemclass)
        return items

    def _choose(self, item):
        return lambda: self._chooseitem(item)

    def _chooseitem(self, item):
        self.showchild(ChooseManufacturingSubstance(self.playfield,
                                                    self._substance,
                                                    self.font,
                                                    self.prefs,
                                                    self._choosesubstance(item),
                                                    self.dismisschild))

    def _choosesubstance(self, item):
        return lambda s: self._chosesubstance(item, s)

    def _chosesubstance(self, item, substance):
        self._chose(item, substance)
        self.dismiss()
                
    def addbuttons(self, surface, dy):
        for item in self._qualifyingitems(SimpleItem, self._substance):
            dy = self.addbutton(surface,
                                item.noun.capitalize(),
                                self._choose(item),
                                dy)
