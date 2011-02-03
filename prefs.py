from pygame.font import Font, SysFont

class DisplayOptions(object):
    def __init__(self, fontname, sysfont, width, height):
        self._fontname = fontname
        self._fontclass = SysFont if sysfont else Font
        self.width = width
        self.height = height
        self.selectioncolor = 0, 255, 0
        self.debugging = True

    @property
    def font(self):
        return self._fontclass(self._fontname, max(self.width, self.height))
