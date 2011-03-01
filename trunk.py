from detailview import DetailView

class DirectTree(DetailView):
    # N, S, NE, NW, SE, SW
    arrows = u'\u2b06',u'\u2b07',u'\u2b08',u'\u2b09',u'\u2b0a',u'\u2b0b'
    
    def __init__(self, playfield, location, font, prefs, dismiss):
        DetailView.__init__(self, playfield, font, prefs, None, dismiss,
                            None, None)
        self._location = location

    def _directer(self, direction):
        return lambda: self._direct(direction)

    def _direct(self, direction):
        self.playfield.player.felltree(self._location, direction)
        self.dismiss()

    def addbuttons(self, surface, dy):                
        for i in range(len(self.arrows)):
            dy = self.addbutton(surface,
                                self.arrows[i],
                                self._directer(i),
                                dy)
        return dy
