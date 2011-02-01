from collections import deque
from random import choice, randint, sample

from data import *
from pathing import PathManager

class Tile(object):
    __slots__ = ('passable',
                 'color',
                 'substance',
                 'revealed',
                 'designated',
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
        self.designated = False
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
    __slots__ = ('covering')
    
    def __init__(self, varient, covering=None):
        Tile.__init__(self, True, None, varient)
        self.covering = covering
        self.color = (self.randomizecolor(self.covering.color)
                      if self.covering else None)

    @property
    def description(self):
        return self.covering.adjective if self.covering else None

class Earth(Tile):
    __slots__ = ()

    def __init__(self, substance, varient):
        Tile.__init__(self, False, substance, varient)

class Branch(Tile):
    __slots__ = ()

    def __init__(self, substance, varient, color):
        Tile.__init__(self, False, substance, varient, color)

    @property
    def description(self):
        return _('{tree} branch').format(tree=self.substance.noun)

class Leaves(Tile):
    __slots__ = ()

    def __init__(self, substance):
        Tile.__init__(self, True, substance, randint(0,2))

    @property
    def description(self):
        return self.substance.noun

class TreeTrunk(Tile):
    __slots__ = ()

    def __init__(self, substance, color=None):
        Tile.__init__(self, False, substance, 0, color)

    @property
    def description(self):
        return _('{wood} tree').format(wood=self.substance.noun)

class Space(object):
    def __init__(self, dim):
        self.dim = (dim[0], dim[1], dim[2])
        self.pathing = PathManager(self)
        self.cache = {}
        self.changed = False

    def maketree(self, loc):
        surround = self.pathing.adjacent_xy(loc[0:2])
        height = randint(6,18)
        branch = None
        wood = choice(Wood.__subclasses__())
        color = None
        for i in range(height):
            trunk = (loc[0], loc[1], loc[2] + i)
            tile = TreeTrunk(wood, color)
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
                    self.cache[branch + (loc[2]+i,)] = Branch(wood,
                                                              varient,
                                                              color)
            if i > 2:
                available = [s for s in surround
                             if s + (loc[2]+i,) not in self.cache]
                leaves = sample(available, len(available)-1)
                for leaf in leaves:
                    self.cache[leaf + (loc[2]+i,)] = Leaves(Leaf)
        self.cache[loc[0:2] + (loc[2]+height,)] = Leaves(Leaf)

    def get_dimensions(self):
        return self.dim

    def __getitem__(self, loc):
        if not all([0 <= loc[i] < self.dim[i] for i in range(3)]):
            return None
        
        if loc not in self.cache:
            if loc[2] == 64:
                self.cache[loc] = Empty(randint(0,3), Grass)
            elif loc[2] > 64:
                self.cache[loc] = Empty(randint(0,3))
            elif loc[2] >= 61:
                self.cache[loc] = Earth(Clay, randint(0,3))
            else:
                self.cache[loc] = Earth(Stone, randint(0,3))

        tile = self.cache[loc]
        if loc[2] >= 64:
            tile.revealed = True
        return tile

    def remove(self, loc):
        self.cache[loc] = Empty()
        for n in self.pathing.adjacent_xy(loc[0:2]):
            self[n + (loc[2],)].revealed = True
        self.changed = True

class Game(object):
    def __init__(self, dimensions):
     
        self.dimensions = dimensions

        self.timescales = [ 0.2, 0.5, 1.0, 2.0, 5.0 ]
        self.dt = 0.1

        self.world = World(Space(self.dimensions), [])
        self._schedule = deque([[] for i in range(128)])

        self.t = 0
            
        self.done = False
        self.paused = False

    def schedule(self, creature):
        self.world.space[creature.location].creatures.append(creature)
        self.world.creatures.append(creature)
        self.reschedule(creature)

    def reschedule(self, creature):
        rest = int(creature.rest)
        self._schedule[rest].append(creature)
        creature.rest -= rest

    def getscheduled(self):
        scheduled = self._schedule.popleft()
        self._schedule.append([])
        return scheduled

    def step(self):       
        if not self.paused:
            creatures = self.getscheduled()
            for creature in creatures:
                creature.step(self.world)
                if creature.remove:
                    self.world.creatures.remove(creature)
                else:
                    self.reschedule(creature)
            self.t += 1
