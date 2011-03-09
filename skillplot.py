import gettext
gettext.install('test')

from itertools import chain
from random import seed

from matplotlib.pyplot import plot, errorbar, axis, show
from numpy import std

from data import SkilledLabor

class Skills(object):
    def __init__(self, exp):
        self._exp = exp

    def exp(self, skill):
        return self._exp

class Creature(object):
    def __init__(self, exp):
        self.skills = Skills(exp)

seed(0)

d = 200
n = 100

ss = [i/float(d) for i in range(d)]

xs = list(chain(*[n * [x] for x in ss]))
ys = [SkilledLabor.skilldisplayed(Creature(x)) for x in xs]

means = [sum(ys[n*i:n*i+n])/n for i in range(d)]
errs = [std(ys[n*i:n*i+n]) for i in range(d)]

plot(xs, ys, ',', alpha=0.1)
errorbar(ss, means, errs)
axis([0,1,0,1])

show()
