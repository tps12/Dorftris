from pygame import draw, event, Rect, Surface
from pygame.locals import *
from pygame.sprite import *

from button import Button
from data import Stockpile
from furnish import FurnishingSelect
from space import Earth, Floor, TreeTrunk
from text import TextRenderer
from trunk import DirectTree

class RegionDetails(object):
    def __init__(self, locations, playfield, font, prefs, describetile,
                 showchild, dismiss, pushscreen, popscreen):
        self._locations = locations
        self._playfield = playfield
        self._prefs = prefs
        self._describe = describetile
        self._showchild = showchild
        self._dismiss = dismiss
        self._pushscreen = pushscreen
        self._popscreen = popscreen
        
        self.scale(font)

    def _addline(self, surface, text, color, dy):
        image = self._renderer.render(text, color)
        surface.blit(image, (0,dy))
        return dy + image.get_height()

    def _addbutton(self, surface, text, click, dy):
        button = Button(self._prefs, self._hotkeys, text, click)
        button.location = 0, dy
        button.draw(surface)
        self._buttons.append(button)
        return dy + button.size[1]
        
    def _makebackground(self, size):
        self._renderer = TextRenderer(self._font, size[0])

        self._background = Surface(size, flags=SRCALPHA)
        self._background.fill((0,0,0))

        desc = None
        for location in self._locations:
            d = self._describe(location)
            if desc is None:
                desc = d
            elif d != desc:
                desc = _(u'{n} spaces').format(n=len(self._locations))
                break

        dy = 0
        dy = self._addline(self._background,
                           desc,
                           self._prefs.selectioncolor,
                           dy)

        self._hotkeys = []
        self._buttons = []
        if self._allclearfloor(self._locations):
            dy = self._addbutton(self._background,
                                 _(u'Dig down'),
                                 self._designate,
                                 dy)
            dy = self._addbutton(self._background,
                                 _(u'Make stockpile'),
                                 self._stockpile,
                                 dy)
            if (len(self._locations) == 1 and
                not self._playfield.game.world.space[
                    self._locations[0]].furnishing):
                dy = self._addbutton(self._background,
                                     _(u'Furnish'),
                                     self._furnish,
                                     dy)
        elif self._allsolidwalls(self._locations):
            dy = self._addbutton(self._background,
                                 _(u'Dig out'),
                                 self._designate,
                                 dy)
        elif (len(self._locations) == 1 and
              isinstance(self._playfield.game.world.space[
                  self._locations[0]], TreeTrunk)):
            dy = self._addbutton(self._background,
                                 _(u'Fell'),
                                 self._fell,
                                 dy)

    def _allclearfloor(self, tiles):
        return all([isinstance(self._playfield.game.world.space[(x,y,z)], Floor)
                    for (x,y,z) in tiles])

    def _allsolidwalls(self, tiles):
        return all([isinstance(self._playfield.game.world.space[tile], Earth)
                    for tile in tiles])

    def _clearselectedtiles(self):
        self._playfield.selection = None

    def _stockpile(self):
        self._playfield.player.addstockpile(Stockpile(self._locations, []))
        self._clearselectedtiles()

    def _fell(self):
        self._showchild(DirectTree(self._playfield.player,
                                   self._playfield.selection,
                                   self._font,
                                   self._prefs,
                                   self._dismiss))
        
        self._clearselectedtiles()

    def _furnish(self):
        self._showchild(FurnishingSelect(self._playfield.player,
                                         self._playfield.selection,
                                         self._font,
                                         self._prefs,
                                         self._dismiss))
        
        self._clearselectedtiles()

    def _designatetile(self, location):
        x, y, z = location
        tile = self._playfield.game.world.space[(x,y,z)]
        if isinstance(tile, Floor):
            floor = self._playfield.game.world.space[(x,y,z-1)]
            if isinstance(floor, Earth):
                self._playfield.player.designatefordigging((x,y,z-1))
        elif isinstance(tile, Earth):
            self._playfield.player.designatefordigging((x,y,z))

    def _designate(self):
        for location in self._locations:
            self._designatetile(location)
        
        self._clearselectedtiles()
        
    def scale(self, font):
        self._font = font
        self._background = None

    def resize(self, size):
        pass

    def handle(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                self._playfield.selection = None
                return True
            
        for button in self._buttons:
            if button.handle(e):
                return True
        
        return False

    def draw(self, surface):
        if not (self._playfield.selection == self._locations or
                (len(self._locations) == 1 and
                 self._locations[0] == self._playfield.selection)):
            self._dismiss()
        
        if not self._background:
            self._makebackground(surface.get_size())
            surface.blit(self._background, (0,0))
