from collections import deque
from random import choice, randint, sample
from time import time

from data import Oak, World
from pathing import PathManager

class Game(object):
    def __init__(self, dimensions):
     
        self.dimensions = dimensions

        class Tile(object):
            def __init__(self, kind, passable, color, varient):
                self.kind = kind
                self.passable = passable
                self.revealed = False
                self.color = color
                self.varient = varient

            def varient(self):
                return self.varient
                
            def is_passable(self):
                return self.passable

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
                for i in range(height):
                    trunk = (loc[0], loc[1], loc[2] + i)
                    self.cache[trunk] = Tile('tree-trunk', False,
                                             Oak.color, 0)
                    if i > 3:
                        branch = choice([b for b in surround
                                         if b != branch] + [None])
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
                            self.cache[branch + (loc[2]+i,)] = Tile('branch',
                                                                    False,
                                                                    Oak.color,
                                                                    varient)
                    if i > 2:
                        available = [s for s in surround
                                     if s + (loc[2]+i,) not in self.cache]
                        leaves = sample(available, len(available)-1)
                        for leaf in leaves:
                            self.cache[leaf + (loc[2]+i,)] = Tile('leaves',
                                                                  False,
                                                                  (0,randint(65,189),0),
                                                                  0)
                self.cache[loc[0:2] + (height+1,)] = Tile('leaves',
                                                          False,
                                                          (0,randint(65,189),0),
                                                          0)

            def get_dimensions(self):
                return self.dim

            def __getitem__(self, loc):
                if not all([0 <= loc[i] < self.dim[i] for i in range(3)]):
                    return None
                
                if loc not in self.cache:
                    shade = randint(65, 189)
                    if loc[2] == 63:
                        color = (0,shade,0)
                    elif loc[2] >= 61:
                        color = (shade*3/4,shade/2,0)
                    else:
                        color = (shade,shade,shade)
                        
                    self.cache[loc] = Tile(None,
                                           loc[2] >= 64,
                                           color,
                                           randint(0,3))
                return self.cache[loc]

            def remove(self, loc):
                self.cache[loc] = Tile(None, True, (0,0,0), 0)
                for n in self.pathing.adjacent_xy(loc[0:2]):
                    self[n + (loc[2],)].revealed = True
                self.changed = True

        self.world = World(Space(self.dimensions), [], [])
        self.schedule = None

        self.t = 0
        self.lasttime = None
        self.targettime = 1/60.0
            
        self.done = False
        self.paused = False

    def step(self):
        if self.schedule is None:
            self.schedule = deque([[] for i in range(128)])
            for c in self.world.creatures:
                self.schedule[c.rest].append(c)
        
        if not self.paused:
            t = time()
            elapsed = 0
            
            while elapsed < self.targettime:
                creatures = self.schedule.popleft()
                self.schedule.append([])
                for creature in creatures:
                    creature.step(self.world)
                    self.schedule[creature.rest].append(creature)
                    creature.rest = 0
                self.t += 1
                    
                self.lasttime = t
                t = time()
                elapsed += max(0, min(0.125, t - self.lasttime))

        self.lasttime = time()
