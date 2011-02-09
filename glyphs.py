from data import *
from game import *
from space import *

from pygame.font import Font

class Air(object):
    pass

class GlyphGraphics(object):
    def __init__(self, size):
        self.font = Font('FreeMono.ttf', size)
        self.glyphs = {
            Air: u'\u00b7',
            Bag: u'\u01d2',
            Barrel: u'\u2338',
            Branch: (u'\u2b06',u'\u2b07',u'\u2b08',u'\u2b09',u'\u2b0a',u'\u2b0b'),
            'button': (u'\u250c',u'\u2500',u'\u2556',u'\u2551',u'\u255d',u'\u2550',u'\u2558',u'\u2502'),
            'chair': u'\u2441',
            Corpse: u'\u20e0',
            Dwarf: u'\u263a',
            Goblin: u'\u263f',
            'grapes': u'\u2031',
            Earth: (u'\u02d2',u'\u02d3',u'\u02de',u'\u058a'),
            'harp': u'\u01f7',
            Leaves: ('*', u'\u2051', u'\u2042'),
            LooseStone: u'\u2b22',
            'ox': u'\u2649',
            Pickax: u'\u23c9',
            'pig': u'\u2364',
            'piller': u'\u2161',
            'pipe': u'\u221b',
            'sheep': (u'\u222e', u'\u222b'),
            'shovel': u'\u020a',
            'spear': u'\u16cf',
            'spider-big': u'\u046a',
            SmallSpider: u'\u046b',
            Stockpile: u'\u2263',
            StockpileComponent: u'\u2263',
            TreeTrunk: (u'\u2b22', u'\u2b21', u'\u25ce'),
            Tortoise: u'\u237e',
            Workbench: u'\u2293'
            }

        self.images = {}

        self.unknown = self._getimage(u'\ufffd')

    def _getimage(self, glyphs):
        if type(glyphs) is not tuple:
            glyphs = (glyphs,)
        return tuple([self.font.render(glyph, True, (0,0,0))
                      for glyph in glyphs])

    def __getitem__(self, thing):
        key = thing if isinstance(thing, type) else thing.__class__
        try:
            return self.images[key]
        except KeyError:
            try:
                image = self._getimage(self.glyphs[key])
                self.images[key] = image
                return image
            except KeyError:
                return self.unknown
