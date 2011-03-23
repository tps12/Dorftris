from random import random

class Faction(object):
    def __init__(self, name, color, status, values):
        self.name = name
        self.color = color
        self.status = status
        self.values = dict([(v, 0.5) for v in values])

    def repress(self, target):
        d = min(0.001, target.status)
        target.status -= d

    def rule(self, others):
        threat = max(others, key=lambda f: f.status)
        if threat.status > 0.5:
            # repress potential threat
            target = threat
        else:
            # repress underclass
            target = min(others, key=lambda f: f.status)
            
        self.repress(target)

    def iterate(self, others):
        # mutate values
        for v in self.values.keys():
            self.values[v] = min(1, max(0, self.values[v] + (0.005 - 0.01 * random())))
        
        if self.status == 1:
            self.rule(others)
        elif self.status == 0:
            ruler = max(others, key=lambda f: f.status)
            if ruler.status == 1:
                # react to regime's values
                d = 0.01
                for v in self.values.keys():
                    if ruler.values[v] >= 0.5:
                        self.values[v] = max(0, self.values[v] - d)
                    else:
                        self.values[v] = min(1, self.values[v] + d)
        elif all([self.status > f.status for f in others]):
            # rise to power
            d = min(0.001, 1 - self.status)
            self.status += d
            for f in others:
                if f != self:
                    f.status -= d/len(others)

class Society(object):
    def __init__(self, factions):
        self.factions = factions

    def iterate(self):
        for f in self.factions:
            f.iterate([e for e in self.factions if e != f])
