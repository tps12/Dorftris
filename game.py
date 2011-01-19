from random import choice, randint, sample

from data import Barrel, Corpse, Dwarf, Entity, Goblin, Oak, SmallSpider, Thing, Tortoise, World
from pathing import PathManager

class Game(object):
    def __init__(self):
     
        self.dimensions = 156, 104, 128

        kind = (Dwarf,Goblin,Tortoise,SmallSpider)

        class Tile(object):
            def __init__(self, kind, passable, color, varient):
                self.kind = kind
                self.passable = passable
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

                for i in range(20):
                    self.maketree((randint(0, self.dim[0]-1),
                                   randint(0, self.dim[1]-1),
                                   1))

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
                        color = (shade,shade/2,0)
                    else:
                        color = (shade,shade,shade)
                        
                    self.cache[loc] = Tile(None,
                                           loc[2] >= 64,
                                           color,
                                           randint(0,3))
                return self.cache[loc]

            def remove(self, loc):
                self.cache[loc] = Tile(None, True, (0,0,0), 0)
                self.changed = True

        self.world = World(Space(self.dimensions), [], [])

##        for i in range(20):
##            creature = choice(kind)((randint(0,self.dimensions[0]-1),
##                                     randint(0,self.dimensions[1]-1),
##                                     64))
##            self.world.creatures.append(creature)
##
##        for i in range(10):
##            self.world.items.append(Barrel((randint(0,self.dimensions[0]-1),
##                                            randint(0,self.dimensions[1]-1),
##                                            64),
##                                           Oak))

        self.world.creatures.append(Dwarf((64,64,64)))
            
        self.done = False
        self.paused = False

    def step(self):
        for creature in self.world.creatures:
            if not self.paused:
                creature.step(self.world)
           
