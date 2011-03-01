from detailview import DetailView
from data import Stockpile
from furnish import FurnishingSelect
from space import Earth, Floor, TreeTrunk
from trunk import DirectTree

class RegionDetails(DetailView):
    def __init__(self, locations, playfield, font, prefs, describetile,
                 showchild, dismiss, pushscreen, popscreen):
        DetailView.__init__(self, playfield, font, prefs, showchild, dismiss,
                            pushscreen, popscreen)
        self._locations = locations
        self._describe = describetile

    def addlines(self, surface, dy):
        desc = None
        for location in self._locations:
            d = self._describe(location)
            if desc is None:
                desc = d
            elif d != desc:
                desc = _(u'{n} spaces').format(n=len(self._locations))
                break

        dy = self.addline(surface,
                          desc,
                          self.prefs.selectioncolor,
                          dy)
        return dy

    def addbuttons(self, surface, dy):
        if self._allclearfloor(self._locations):
            dy = self.addbutton(surface,
                                _(u'Dig down'),
                                self._designate,
                                dy)
            dy = self.addbutton(surface,
                                _(u'Make stockpile'),
                                self._stockpile,
                                dy)
            if (len(self._locations) == 1 and
                not self.playfield.game.world.space[
                    self._locations[0]].furnishing):
                dy = self.addbutton(surface,
                                    _(u'Furnish'),
                                    self._furnish,
                                    dy)
        elif self._allsolidwalls(self._locations):
            dy = self.addbutton(surface,
                                _(u'Dig out'),
                                self._designate,
                                dy)
        elif (len(self._locations) == 1 and
              isinstance(self.playfield.game.world.space[
                  self._locations[0]], TreeTrunk)):
            dy = self.addbutton(self._background,
                                _(u'Fell'),
                                self._fell,
                                dy)

    def _allclearfloor(self, tiles):
        return all([isinstance(self.playfield.game.world.space[(x,y,z)], Floor)
                    for (x,y,z) in tiles])

    def _allsolidwalls(self, tiles):
        return all([isinstance(self.playfield.game.world.space[tile], Earth)
                    for tile in tiles])

    def _clearselectedtiles(self):
        self.playfield.selection = None

    def _stockpile(self):
        self.playfield.player.addstockpile(Stockpile(self._locations, []))
        self._clearselectedtiles()

    def _fell(self):
        self.showchild(DirectTree(self.playfield,
                                  self.playfield.selection,
                                  self.font,
                                  self.prefs,
                                  self.dismiss))
        
        self._clearselectedtiles()

    def _furnish(self):
        self.showchild(FurnishingSelect(self.playfield,
                                        self.playfield.selection,
                                        self.font,
                                        self.prefs,
                                        self.dismiss))
        
        self._clearselectedtiles()

    def _designatetile(self, location):
        x, y, z = location
        tile = self.playfield.game.world.space[(x,y,z)]
        if isinstance(tile, Floor):
            floor = self.playfield.game.world.space[(x,y,z-1)]
            if isinstance(floor, Earth):
                self.playfield.player.designatefordigging((x,y,z-1))
        elif isinstance(tile, Earth):
            self.playfield.player.designatefordigging((x,y,z))

    def _designate(self):
        for location in self._locations:
            self._designatetile(location)
        
        self._clearselectedtiles()
        
    def draw(self, surface):
        if not (self.playfield.selection == self._locations or
                (len(self._locations) == 1 and
                 self._locations[0] == self.playfield.selection)):
            self.dismiss()

        super(RegionDetails, self).draw(surface)
        
