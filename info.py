from select import SelectionInfo

class InfoView(object):
    def __init__(self, playfield, font, prefs, push):
        self._playfield = playfield
        self._prefs = prefs
        self._pushscreen = push

        self._displays = [SelectionInfo(self._playfield,
                                        font,
                                        self._prefs,
                                        self._pushdisplay,
                                        self._pushscreen)]
        
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

    def _pushdisplay(self, child):
        self._displays.append(child)

    def _popdisplay(self):
        del self._displays[-1]

    def handle(self, e):
        return self._displays[-1].handle(e)

    def draw(self, surface):
        self._displays[-1].draw(surface)
