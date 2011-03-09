import gettext
gettext.install('test')

from itertools import chain
from random import seed

from matplotlib.pyplot import plot, axis, show

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

d = 1000
n = 100

xs = list(chain(*[n * [x] for x in [i/float(d) for i in range(d)]]))
ys = [SkilledLabor.skilldisplayed(Creature(x)) for x in xs]

plot(xs, ys, ',', alpha=0.1)
axis([0,1,0,1])

show()
