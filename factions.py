class Faction(object):
    def __init__(self, name, color, status, values):
        self.name = name
        self.color = color
        self.status = status
        self.values = dict([(v, 0.5) for v in values])

class Society(object):
    def __init__(self, factions):
        self.factions = factions

    def iterate(self):
        for f in self.factions:
            from random import random
            f.status = random()
            for v in f.values.keys():
                f.values[v] = random()
