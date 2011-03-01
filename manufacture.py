from detailview import DetailView
from data import Manufacturing
from makeitem import ChooseManufacturingItem

class ChooseManufacturingType(DetailView):
    def __init__(self, playfield, font, prefs, showchild, dismiss):
        DetailView.__init__(self, playfield, font, prefs, showchild, dismiss,
                            None, None)

        self._bench = self.playfield.selection

    def _choose(self, job):
        return lambda: self._chooseitem(job)

    def _chooseitem(self, job):
        self.showchild(ChooseManufacturingItem(self.playfield,
                                               job.substance,
                                               self.font,
                                               self.prefs,
                                               self.showchild,
                                               self._chose,
                                               self.dismisschild))

    def _chose(self, item, substance):
        self._bench.jobs.append((item, substance))
        self.dismiss()

    def addbuttons(self, surface, dy):
        for job in Manufacturing.__subclasses__():
            dy = self.addbutton(surface,
                                job.noun.capitalize(),
                                self._choose(job),
                                dy)
        return dy

    def draw(self, surface):
        if self.playfield.selection != self._bench:
            self.dismiss()
        
        super(ChooseManufacturingType, self).draw(surface)
