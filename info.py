from select import SelectionInfo

class InfoView(object):
    def __init__(self, playfield, font, prefs):
        self._playfield = playfield
        self._prefs = prefs       
        self._displays = [SelectionInfo(self._playfield,
                                        font,
                                        self._prefs)]
        self.scale(font)

    @property
    def width(self):
        return self._font.size('-' * 32)[0]
    
    def scale(self, font):
        self._font = font
        for d in self._displays:
            d.scale(self._font)

    def resize(self, size):
        for d in self._displays:
            d.resize(size)

    def handle(self, e):
        handled, child = self._displays[-1].handle(e)
        if handled:
            if child is self._displays[-1]:
                child = self
            return True, child

        return False, self

    def draw(self, surface):
        self._displays[-1].draw(surface)
