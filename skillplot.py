import gettext
gettext.install('test')

from itertools import chain
from random import seed

from matplotlib.pyplot import plot, errorbar, axis, show

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
errs = [], []

for i in range(d):
    m = means[i]
    
    hdy = 0
    c = 0
    while c < 0.25 * n and m + hdy < 1:
        hdy += 0.001
        c = len([y for y in ys[n*i:n*i+n] if m <= y < m + hdy])

    ldy = 0
    c = 0
    while c < 0.25 * n and m - ldy > 0:
        ldy += 0.001
        c = len([y for y in ys[n*i:n*i+n] if m - ldy < y <= m])
        
    errs[0].append(hdy)
    errs[1].append(ldy)

plot(xs, ys, ',', alpha=0.1)
errorbar(ss, means, errs)
axis([0,1,0,1])

show()
