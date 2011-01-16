from random import choice, randint

from data import Barrel, Corpse, Dwarf, Entity, Goblin, Oak, SmallSpider, Thing, Tortoise, World
from pathing import PathManager

class Game(object):
    def __init__(self):
     
        self.dimensions = 128, 128, 128

        kind = (Dwarf,Goblin,Tortoise,SmallSpider)

        class Tile(object):
            def __init__(self, passable, shade, varient):
                self.passable = passable
                self.shade = shade
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

            def get_dimensions(self):
                return self.dim

            def __getitem__(self, loc):
                if loc not in self.cache:
                    self.cache[loc] = Tile(loc[2] == 1,
                                           randint(65, 189),
                                           randint(0,3))
                return self.cache[loc]

        self.world = World(Space(self.dimensions), [], [])

        for i in range(20):
            creature = choice(kind)((randint(0,self.dimensions[0]-1),
                                     randint(0,self.dimensions[1]-1),
                                     1))
            self.world.creatures.append(creature)

        for i in range(10):
            self.world.items.append(Barrel((randint(0,self.dimensions[0]-1),
                                            randint(0,self.dimensions[1]-1),
                                            1),
                                           Oak))

        self.done = False
        self.paused = False

    def step(self):
        for creature in self.world.creatures:
            if not self.paused:
                creature.step(self.world)
           
