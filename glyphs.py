class GlyphGraphics(object):
    glyphs = {
        'barrel': u'\u2338',
        'chair': u'\u2441',
        'corpse': u'\u20e0',
        'dwarf': u'\u263a',
        'goblin': u'\u263f',
        'ground': (u'\u02d2',u'\u02d3',u'\u02de',u'\u058a'),
        'pipe': u'\u221b',
        'spider-big': u'\u046a',
        'spider-small': u'\u046b',
        'tortoise': u'\u237e'
        }

    images = {}

    def __init__(self, font):
        self.font = font
        self.unknown = self._getimage(u'\ufffd')

    def _getimage(self, glyphs):
        if type(glyphs) is not tuple:
            glyphs = (glyphs,)
        return tuple([self.font.render(glyph, True, (0,0,0))
                      for glyph in glyphs])

    def __getitem__(self, thing):
        key = thing.kind
        try:
            return self.images[key]
        except KeyError:
            try:
                image = self._getimage(self.glyphs[key])
                self.images[key] = image
                return image
            except KeyError:
                return self.unknown
