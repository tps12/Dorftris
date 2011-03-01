from detailview import DetailView
from data import Furnishings

class FurnishingSelect(DetailView):
    def __init__(self, playfield, location, font, prefs, dismiss):
        DetailView.__init__(self, playfield, font, prefs, None, dismiss,
                            None, None)
        self._location = location

    def _choose(self, item):
        return lambda: self._furnish(item)

    def _furnish(self, item):
        self.playfield.player.furnish(self._location, item)
        self.dismiss()
                
    def addbuttons(self, surface, dy):
        for pile in self.playfield.player.getstockpiles(Furnishings):
            for item in pile.contents:
                if item.reserved:
                    continue
                dy = self.addbutton(surface,
                                    item.description(),
                                    self._choose(item),
                                    dy)
        for item in self.playfield.player.unstockpileditems(Furnishings):
            if item.reserved:
                continue
            dy = self.addbutton(surface,
                                item.description(),
                                self._choose(item),
                                dy)
            
        return dy
