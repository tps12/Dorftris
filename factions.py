class Faction(object):
    def __init__(self, name, color, status, values):
        self.name = name
        self.color = color
        self.status = status
        self.values = dict([(v, 0.5) for v in values])

    def iterate(self, others):
        if self.status == 1:
            # ruling
            threat = max(others, key=lambda f: f.status)
            if threat.status > 0.5:
                # repress potential threat
                target = threat
            else:
                # repress underclass
                target = min(others, key=lambda f: f.status)

            d = min(0.001, target.status)
            target.status -= d
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
