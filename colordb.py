from math import sqrt

from colors import colordict

def match(c):
    return colordict[min(colordict.keys(),
                         key=lambda v: sqrt(sum([(c[i]-v[i])**2
                                                  for i in range(3)])))]
