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

        self.world = World(NoiseSpace(self.dimensions), self.reschedule)
        self._schedule = deque([[] for i in range(120)])
            
        self.done = False
        self.paused = False

    def schedule(self, creature):
        self.world.space[creature.location].creatures.append(creature)
        self.world.creatures.append((creature, self.world.time))
        self.reschedule(creature)

    def reschedule(self, target):
        rest = int(target.rest)
        self._schedule[rest].append((target, self.world.time))
        target.rest -= rest

    def getscheduled(self):
        scheduled = self._schedule.popleft()
        self._schedule.append([])
        return scheduled

    def step(self):       
        if not self.paused:
            targets = self.getscheduled()
            for target, t in targets:
                if target.step(self.world, self.world.time - t):
                    if isinstance(target, Creature):
                        self.world.creatures.remove((target, t))
                else:
                    self.reschedule(target)
            self.world.liquids()
            self.world.time += 1
