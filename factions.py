class Faction(object):
    def __init__(self, name, color, status, values):
        self.name = name
        self.color = color
        self.status = status
        self.values = dict([(v, 0.5) for v in values])

def stasis(society):
    return stasis

def disarray(society):
    ascendant = max(society.factions, key=lambda f: f.status)
    d = min(0.01, 1 - ascendant.status)
    ascendant.status += d
    for f in society.factions:
        if f == ascendant:
            continue
        f.status = max(f.status - d/(len(society.factions)-1), 0)
    return disarray

class Society(object):
    def __init__(self, factions):
        self.factions = factions
        self.mode = disarray

    def iterate(self):
        self.mode = self.mode(self)
