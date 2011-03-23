from random import choice

class Faction(object):
    def __init__(self, name, color, status, values):
        self.name = name
        self.color = color
        self.status = status
        self.values = dict([(v, 0.5) for v in values])
        self.elite = None

    def ossify(self):
        d = 0.001
        for v in self.values.keys():
            if self.values[v] >= 0.5:
                self.values[v] = min(1, self.values[v] + d)
            else:
                self.values[v] = max(0, self.values[v] - d)

    def react(self, ruler):
        d = 0.001
        for v in self.values.keys():
            if ruler.values[v] >= 0.5:
                self.values[v] = max(0, self.values[v] - d)
            else:
                self.values[v] = min(1, self.values[v] + d)
        if all([abs(self.values[v] - ruler.values[v]) == 1
                for v in self.values.keys()]):
            self.elite = ruler

    def conform(self, ruler):
        d = 0.001
        for v in self.values.keys():
            if ruler.values[v] >= 0.5:
                self.values[v] = min(1, self.values[v] + d)
            else:
                self.values[v] = max(0, self.values[v] - d)
        if all([abs(self.values[v] - ruler.values[v]) == 1
                for v in self.values.keys()]):
            self.elite = ruler

    def repress(self, target):
        d = min(0.001, target.status)
        target.status -= d

    def rule(self, others):
        self.ossify()

        threat = max(others, key=lambda f: f.status)
        if threat.status > 0.5:
            # repress potential threat
            target = threat
        else:
            # repress underclass
            target = min(others, key=lambda f: f.status)
            
        self.repress(target)

    def wallow(self, others):
        ruler = max(others, key=lambda f: f.status)
        if ruler.status == 1:
            self.react(ruler)

    def muddle(self, others):
        ruler = max(others, key=lambda f: f.status)
        if ruler.status == 1:
            self.conform(ruler)

    def overthrow(self):
        d = min(0.01, self.elite.status - self.status)
        self.status += d
        self.elite.status -= d
        if self.status > self.elite.status:
            self.elite = None

    def struggle(self, others):
        d = min(0.001, 1 - self.status)
        self.status += d

    def iterate(self, others):
        if self.elite:
            self.overthrow()
        elif self.status == 1:
            self.rule(others)
        elif self.status == 0:
            self.wallow(others)
        elif all([f.status < 1 for f in others]):
            self.struggle(others)
        else:
            self.muddle(others)
            
class Society(object):
    def __init__(self, factions):
        self.factions = factions

    def iterate(self):
        f = choice(self.factions)
        f.iterate([e for e in self.factions if e != f])
