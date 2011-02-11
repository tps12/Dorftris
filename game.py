from collections import deque
from random import choice, randint, sample

from data import *
from noisespace import NoiseSpace
from pathing import PathManager

class Game(object):
    def __init__(self, dimensions):
     
        self.dimensions = dimensions

        self.timescales = [ 0.2, 0.5, 1.0, 2.0, 5.0 ]
        self.dt = 0.1

        self.world = World(NoiseSpace(self.dimensions), [])
        self._schedule = deque([[] for i in range(128)])
            
        self.done = False
        self.paused = False

    def schedule(self, creature):
        self.world.space[creature.location].creatures.append(creature)
        self.world.creatures.append((creature, self.world.time))
        self.reschedule(creature)

    def reschedule(self, creature):
        rest = int(creature.rest)
        self._schedule[rest].append((creature, self.world.time))
        creature.rest -= rest

    def getscheduled(self):
        scheduled = self._schedule.popleft()
        self._schedule.append([])
        return scheduled

    def step(self):       
        if not self.paused:
            creatures = self.getscheduled()
            for creature, t in creatures:
                if creature.step(self.world, self.world.time - t):
                    self.world.creatures.remove((creature, t))
                else:
                    self.reschedule(creature)
            self.world.time += 1
