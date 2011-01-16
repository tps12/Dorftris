from unittest import TestCase, main

from data import Dwarf, Goblin, SeekAndDestroy, World
from pathing import PathManager

class GoblinTestCase(TestCase):
    def test_hydrated_goblin_starts_seeking(self):
        class Tile(object):
            def __init__(self, passable):
                self.passable = passable
                
            def is_passable(self):
                return self.passable

        class Space(object):
            def __init__(self, dim):
                self.dim = (dim[0], dim[1], 2)
                self.pathing = PathManager(self)

            def get_dimensions(self):
                return self.dim

            def __getitem__(self, loc):
                return Tile(loc[2] == 1)

        world = World(Space((10,10)), [], [])

        world.creatures.append(Dwarf((2,3)))
        world.creatures.append(Goblin((7,8)))

        for c in world.creatures:
            c.hydration = 36000

        for c in world.creatures:
            c.rest = 0
            c.step(world)

        self.assertEqual(isinstance(world.creatures[1].job, SeekAndDestroy), True)

    def test_goblin_kills_dwarf(self):
        class Tile(object):
            def __init__(self, passable):
                self.passable = passable
                
            def is_passable(self):
                return self.passable

        class Space(object):
            def __init__(self, dim):
                self.dim = (dim[0], dim[1], 2)
                self.pathing = PathManager(self)

            def get_dimensions(self):
                return self.dim

            def __getitem__(self, loc):
                return Tile(loc[2] == 1)

        world = World(Space((10,10)), [], [])

        dwarf = Dwarf((2,3))
        world.creatures.append(dwarf)
        goblin = Goblin((7,8))
        world.creatures.append(goblin)

        for c in world.creatures:
            c.hydration = 36000

        while dwarf in world.creatures:
            for c in world.creatures:
                c.rest = 0
                c.step(world)

    def test_goblin_stops_after_killing_dwarf(self):
        class Tile(object):
            def __init__(self, passable):
                self.passable = passable
                
            def is_passable(self):
                return self.passable

        class Space(object):
            def __init__(self, dim):
                self.dim = (dim[0], dim[1], 2)
                self.pathing = PathManager(self)

            def get_dimensions(self):
                return self.dim

            def __getitem__(self, loc):
                return Tile(loc[2] == 1)

        world = World(Space((10,10)), [], [])

        dwarf = Dwarf((2,3))
        world.creatures.append(dwarf)
        goblin = Goblin((7,8))
        world.creatures.append(goblin)

        for c in world.creatures:
            c.hydration = 36000

        while dwarf in world.creatures:
            for c in world.creatures:
                c.rest = 0
                c.step(world)

        for c in world.creatures:
            c.rest = 0
            c.step(world)

        self.assertFalse(isinstance(goblin.job, SeekAndDestroy))

if __name__ == '__main__':
    main()
