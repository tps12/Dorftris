from heapq import *
from itertools import count

class LongTermScheduler(object):
    REMOVED = 0

    def __init__(self):
        self.q = []
        self.d = {}
        self.counter = count(1)

    def add(self, t, target):
        entry = (t, next(self.counter), target)
        self.d[target] = entry
        heappush(self.q, entry)

    def scheduled(self, t):
        targets = []
        while self.q and self.q[0][0] <= t:
            entry = heappop(self.q)
            if entry[1] != self.REMOVED:
                targets.append(entry[2])
        return targets

    def delete(self, target):
        entry = self.d[target]
        entry[1] = self.REMOVED
