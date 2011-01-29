from codecs import open
from random import random
from string import whitespace
from sys import argv
from unicodedata import name

class Generator(object):
    def __init__(self, text):
        self.lexicon = text
        self.lengths = [0 for i in range(64)]
        self.successors = {}

    def process(self):
        word = 0
        last = None
        skip = False
        for c in self.lexicon.lower():
            if skip:
                if c in whitespace:
                    skip = False
                continue

            if word:
                if c in whitespace or 'LETTER' not in name(unicode(c)):
                    self.lengths[word] += 1
                    if last not in self.successors:
                        self.successors[last] = {}
                    if c in self.successors[last]:
                        self.successors[last][None] += 1
                    else:
                        self.successors[last][None] = 1
                    last = None
                    word = 0
                else:
                    if last not in self.successors:
                        self.successors[last] = {}
                    if c in self.successors[last]:
                        self.successors[last][c] += 1
                    else:
                        self.successors[last][c] = 1
                    last = c
                    word += 1
            else:
                if c in whitespace:
                    continue
                if 'LETTER' not in name(unicode(c)):
                    skip = True
                else:
                    if None not in self.successors:
                        self.successors[None] = {}
                    if c in self.successors[None]:
                        self.successors[None][c] += 1
                    else:
                        self.successors[None][c] = 1
                    last = c
                    word = 1

    def calculate(self):
        total = float(sum(self.lengths))
        self.thresholds = self.tothresholds([l/total for l in self.lengths])

        self.successorthresholds = {}
        for c in self.successors.keys():
            successors = []
            total = float(sum(self.successors[c].values()))
            running = 0
            for s in self.successors[c].keys():
                p = self.successors[c][s]/total
                running += p
                successors.append((running, s))
                if running >= 1:
                    break
            self.successorthresholds[c] = successors

    @staticmethod
    def tothresholds(ps):
        thresholds = []
        running = 0
        for p in ps:
            running += p
            thresholds.append(running)
            if running >= 1:
                break
        return thresholds

    @staticmethod
    def randomindex(thresholds):
        r = random()
        for i in range(len(thresholds)):
            if r <= thresholds[i]:
                return i

    def randomlength(self):
        return self.randomindex(self.thresholds)

    def randomsuccessor(self, c):
        successors = self.successorthresholds[c]
        if len(successors) == 1 and successors[0] == None:
            return None
        r = random()
        for t, s in successors:
            if r <= t and s:
                return s

    def generate(self):
        length = self.randomlength()
        value = ''
        while True:
            c = self.randomsuccessor(value[-1] if value else None)
            if c == None:
                return value
            value += c
            if len(value) >= length and None in self.successors[c]:
                return value

if __name__ == '__main__':
    with open(argv[1], 'r', 'utf_8') as f:
        g = Generator(f.read())
        g.process()
        g.calculate()
        print g.generate()
