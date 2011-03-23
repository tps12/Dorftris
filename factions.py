from random import choice, random

class Faction(object):
    MUTATE_DELTA = 0.001
    OSSIFY_DELTA = 0.01
    OVERTHROW_DELTA = 0.01
    REACT_DELTA = 0.01
    REPRESS_DELTA = 0.01
    STRIVE_DELTA = 0.001
    
    def __init__(self, name, color, status, values):
        self.name = name
        self.color = color
        self.status = status
        self.values = dict([(v, 0.5) for v in values])
        self.overthrow = None

    def iteratestatus(self, others):
        if self.status == 1:
            target = choice(others)
            target.status = max(0, target.status - self.REPRESS_DELTA)
        elif self.overthrow:
            if self.status < self.overthrow.status:
                self.overthrow.status = max(0,
                                            self.overthrow.status -
                                            self.OVERTHROW_DELTA)
                self.status = min(1, self.status + self.OVERTHROW_DELTA)
            else:
                self.overthrow = None
        else:
            if self.status == 0:
                ruler = max(others, key=lambda f: f.status)
                if sum([abs(ruler.values[v] - self.values[v])
                        for v in self.values.keys()]) > 0.5 * len(self.values):
                    self.overthrow = ruler
            else:
                self.status = min(1, self.status + self.STRIVE_DELTA)

    def iteratevalues(self, others):
        v = choice(self.values.keys())
        
        if self.status == 1:
            d = (1 if self.values[v] >= 0.5 else -1) * self.OSSIFY_DELTA    
        elif self.status == 0:
            ruler = max(others, key=lambda f: f.status)
            d = (-1 if ruler.values[v] >= 0.5 else 1) * self.REACT_DELTA
        else:
            d = choice([1,-1]) * self.MUTATE_DELTA * random()

        self.values[v] = min(1, max(0, self.values[v] + d))
            
    def iterate(self, others):
        self.iteratestatus(others)
        self.iteratevalues(others)
            
class Society(object):
    def __init__(self, factions):
        self.factions = factions

    def iterate(self):
        f = choice(self.factions)
        f.iterate([e for e in self.factions if e != f])
