class Faction(object):
    def __init__(self, name, color, status, values):
        self.name = name
        self.color = color
        self.status = status
        self.values = dict([(v, 0.5) for v in values])

def stasis(society):
    return stasis

class Society(object):
    def __init__(self, factions):
        self.factions = factions
        self.mode = stasis

    def iterate(self):
        self.mode = self.mode(self)
