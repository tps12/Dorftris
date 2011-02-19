from random import choice, randint, sample

from substances import Clay, Grass, Leaf, Wood, Stone
from pathing import PathManager

class Tile(object):
    __slots__ = ('passable',
                 'color',
                 'substance',
                 'revealed',
                 'designation',
                 'varient',
                 'creatures',
                 'items')
    
    def __init__(self, passable, substance, varient, color=None):
        self.substance = substance
        self.color = (color if color is not None
                      else self.randomizecolor(self.substance.color)
                      if self.substance else None)
        self.passable = passable
        self.revealed = False
        self.designation = None
        self.varient = varient
        self.creatures = []
        self.items = []

    def is_passable(self):
        return self.passable

    @staticmethod
    def randomizecolor(color):
        r = randint(-64,+64)
        return tuple([max(0,min(255,c+r)) for c in color])

    @property
    def description(self):
        return self.substance.noun if self.substance else None

class Empty(Tile):
    __slots__ = ()
    
    def __init__(self):
        Tile.__init__(self, True, None, 0)

    @property
    def description(self):
        return _(u'empty space')

class Floor(Tile):
    __slots__ = ('covering', 'furnishing', 'stockpiles')
    
    def __init__(self, varient, covering=None):
        Tile.__init__(self, True, None, varient)
        self.covering = covering
        self.furnishing = None
        self.color = (self.randomizecolor(self.covering.color)
                      if self.covering else None)
        self.stockpiles = None

    def addstockpile(self, player, stockpile):
        if self.stockpiles is None:
            self.stockpiles = {}
        if player in self.stockpiles:
            raise KeyError
        self.stockpiles[player] = stockpile

    def removestockpile(self, player):
        if self.stockpiles is not None and player in self.stockpiles:
            del self.stockpiles[player]
        if not self.stockpiles:
            self.stockpiles = None

    @property
    def description(self):
        return (self.covering.adjective
                if hasattr(self.covering, 'adjective')
                else _(u'{substance}-covered').format(
                    substance=self.covering.noun)
                if self.covering else None)

class Earth(Tile):
    __slots__ = ()

    def __init__(self, substance, varient):
        Tile.__init__(self, False, substance, varient)

class Direction(object):
    N = 0
    S = 1
    NE = 2
    NW = 3
    SE = 4
    SW = 5

class Tree(object):
    __slots__ = 'location','wood','leaf','color','trunk','branches','leaves','fell'
    
    def __init__(self, location, wood, leaf):
        self.location = location
        self.wood = wood
        self.leaf = leaf
        self.color = Tile.randomizecolor(self.wood.color)
        
        self.trunk = []
        self.branches = []
        self.leaves = []
        self.fell = None

    @property
    def description(self):
        return self.wood.noun

class Branch(Tile):
    __slots__ = ('tree')

    def __init__(self, tree, varient):
        Tile.__init__(self, False, tree.wood, varient, tree.color)
        self.tree = tree
        self.tree.branches.append(self)

    @property
    def description(self):
        return _(u'{tree} branch').format(tree=self.tree.description)

class Leaves(Tile):
    __slots__ = ('tree')

    def __init__(self, tree):
        Tile.__init__(self, True, tree.leaf, randint(0,2))
        self.tree = tree
        self.tree.leaves.append(self)

    @property
    def description(self):
        return _(u'{tree} leaves').format(tree=self.tree.description)

class TreeTrunk(Tile):
    __slots__ = ('tree')

    def __init__(self, tree):
        Tile.__init__(self, False, tree.wood, 0, tree.color)
        self.tree = tree
        self.tree.trunk.append(self)

    @property
    def description(self):
        return _(u'{tree} trunk').format(tree=self.tree.description)

class Space(object):
    def __init__(self, dim):
        self.dim = (dim[0], dim[1], dim[2])
        self.pathing = PathManager(self)
        self.cache = {}
        self.changed = False

    def maketree(self, loc):
        tree = Tree(loc, choice(Wood.__subclasses__()), Leaf)
        
        surround = self.pathing.adjacent_xy(loc[0:2])
        height = randint(6,18)
        branch = None
        for i in range(height):
            trunk = (loc[0], loc[1], loc[2] + i)
            tile = TreeTrunk(tree)
            self.cache[trunk] = tile
            color = tile.color
            if i > 3:
                branch = choice([b for b in surround if b != branch] + [None])
                if branch is not None:
                    varient = -1
                    if branch[0] == loc[0]:
                        if branch[1] == loc[1] - 1:
                            varient = 1 # N
                        else:
                            varient = 0 # S
                    elif branch[0] < loc[0]:
                        if branch[1] == loc[1] + (loc[0]&1):
                            varient = 2 # SW
                        else:
                            varient = 4 # NW
                    else:
                        if branch[1] == loc[1] + (loc[0]&1):
                            varient = 3 # SE
                        else:
                            varient = 5 # NE
                    self.cache[branch + (loc[2]+i,)] = Branch(tree, varient)
            if i > 2:
                available = [s for s in surround
                             if s + (loc[2]+i,) not in self.cache]
                leaves = sample(available, len(available)-1)
                for leaf in leaves:
                    self.cache[leaf + (loc[2]+i,)] = Leaves(tree)
        self.cache[loc[0:2] + (loc[2]+height,)] = Leaves(tree)

    def get_dimensions(self):
        return self.dim

    def groundlevel(self, x, y):
        return 64

    def soillevel(self, x, y):
        return 3

    def __getitem__(self, loc):
        if not all([0 <= loc[i] < self.dim[i] for i in range(3)]):
            return None
        
        g = self.groundlevel(loc[0], loc[1])
        
        if loc not in self.cache:
            if loc[2] == g:
                tile = Floor(randint(0,3), Grass)
            elif loc[2] > g:
                tile = Empty()
            elif loc[2] > g - self.soillevel(loc[0], loc[1]):
                tile = Earth(Clay, randint(0,3))
            else:
                tile = Earth(Stone, randint(0,3))

            if not isinstance(tile, Empty):
                for x, y in self.pathing.adjacent_xy(loc[0:2]):
                    if self.groundlevel(x, y) <= loc[2]:
                        tile.revealed = True
                        break
                
            self.cache[loc] = tile
        else:
            tile = self.cache[loc]
            
        if loc[2] >= g:
            tile.revealed = True
        return tile

    def __setitem__(self, loc, item):
        if loc not in self.cache:
            raise ValueError

        self.cache[loc] = item
        self.changed = True
