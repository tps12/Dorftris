from detailview import DetailView

class ItemDetails(DetailView):
    def __init__(self, item, playfield, font, prefs,
                 dismiss, pushscreen, popscreen):
        DetailView.__init__(self, playfield, font, prefs, None, dismiss,
                            pushscreen, popscreen)
        self._item = item

    def addlines(self, surface, dy):
        dy = self.addline(surface,
                          self._item.description(),
                          self.prefs.selectioncolor,
                          dy)
        return dy

    def draw(self, surface):
        if self.playfield.selection != self._item:
            self.dismiss()

        super(ItemDetails, self).draw(surface)        
