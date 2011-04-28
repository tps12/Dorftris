import math

from star import Star

class StarData(object):
    def __init__(self):
        self.stars = [s for s in self.readdata()]
        self.rotation = 0, (0,0,0)

    @staticmethod
    def correct(cells):
        hip = int(cells[1])
        
        if hip == 37677:
            cells[11] = 19
        elif hip == 55203:
            cells[8:10] = 169.545625, 31.529361
            cells[11] = 136
        elif hip == 78727:
            cells[8:10] = 241.09, -11.373639
            cells[11] = 35
        elif hip == 26220:
            cells[11] = 2
            cells[37] = 0.07
        elif hip == 45085:
            cells[11] = 0.7
        elif hip == 51192:
            cells[11] = 0.5
        elif hip == 82671:
            cells[11] = 0.6
        elif hip == 26221:
            cells[11] = 2
        elif hip == 105186:
            cells[11] = 0.054
        elif hip == 113561:
            cells[11] = 0.42
        elif hip == 115125:
            cells[8:10] = 349.777785, -13.4585517
            cells[11] = 33
        elif hip == 12086:
            cells[11] = 16
        elif hip == 89439:
            return None
        elif hip == 32609:
            cells[37] = 0.48
        elif hip == 81702:
            cells[11] = 0.007
        elif hip == 21148:
            cells[11] = 0.006
        elif hip == 29225:
            return None
        elif hip == 67861:
            return None
        elif hip == 82716:
            cells[11] = 2.27
        elif hip == 88298:
            return None
        elif hip == 92136:
            return None
        elif hip == 32226:
            cells[11] = 1.14
        elif hip == 34561:
            cells[11] = 1.46
        elif hip == 41074:
            return None
        elif hip == 52827:
            cells[11] = 0.54
        elif hip == 62931:
            return None
        elif hip == 65129:
            cells[11] = 0.65
        elif hip == 89440:
            return None

        return cells

    @classmethod
    def readdata(cls):
        with open('hipparcos-naked.txt', 'r') as f:
            with open('star-distances.txt', 'r') as d:
                first = True
                for line in f:
                    if first:
                        first = False
                    else:
                        cells = cls.correct(line.split('|'))
                        if not cells:
                            continue

                        pi = float(cells[11]) / 1000

                        yield Star(cls.getlocation(float(cells[8]),
                                                   float(cells[9]),
                                                   pi),
                                   float(cells[37]),
                                   cls.getmagnitude(float(cells[5]), pi),
                                   float(d.readline()))

    @staticmethod
    def getmagnitude(visual, pi):
        return visual + 5 * (math.log10(pi) + 1)

    @staticmethod
    def getlocation(alpha, delta, pi):
        r = 3.26/pi
        theta = (delta + 90) * math.pi / 180
        phi = - alpha * math.pi / 180
        return r, theta, phi

class RandomStars(object):
    def __init__(self):
        import pygame
        from random import uniform
        
        self._hist = pygame.image.load('hist.pgm')
        self.stars = [self.getrandom() for i in range(6000)]

        z = uniform(-1, 1)
        theta = uniform(0, 2 * math.pi)
        r = math.sqrt(1 - z ** 2)
        u = r * math.cos(theta), r * math.sin(theta), z
        
        self.rotation = uniform(0, 2 * math.pi), u

    def getrandom(self):
        from random import random, uniform, randint, gauss
        from math import sqrt, acos

        w, h = self._hist.get_size()
        while True:
            c = uniform(-0.274, 3.271)
            m = uniform(-15.329, 7.49)

            x = int((c + 0.274) * w/(3.271+0.274))
            y = int((m + 15.329) * h/(7.49+15.329))
            
            if randint(0, 255) > self._hist.get_at((x,y))[0]:

                r = uniform(1, 3.26/pow(10, (m - 6)/5 - 1))
                if random() > sqrt((x*y)/float(w*h)):
                    theta = acos(max(-1, min(1, gauss(0, 0.125))))
                else:
                    theta = acos(uniform(-1, 1))
                phi = uniform(0, 2 * math.pi)
                return Star((r, theta, phi), c, m, abs(math.pi/2 - theta))

if __name__ == '__main__':
    from matplotlib import pyplot, axes
    import numpy

    from sys import argv

    d = StarData()
    r = RandomStars()

    pyplot.subplot(321)
    pyplot.scatter([s.color for s in d.stars],
                   [s.magnitude for s in d.stars],
                   marker='+',
                   alpha=0.025)

    pyplot.subplot(322)
    pyplot.scatter([s.color for s in r.stars],
                   [s.magnitude for s in r.stars],
                   marker='+',
                   alpha=0.025)

    pyplot.subplot(323)
    H, xedges, yedges = numpy.histogram2d(
        [s.color for s in d.stars],
        [s.magnitude for s in d.stars],
        normed=True,
        bins=(100,100))
    
    extent = [xedges[0], xedges[-1] * 10, yedges[0], yedges[-1]]                
    pyplot.imshow(H,
                  cmap=pyplot.cm.gray_r,
                  extent=extent,
                  interpolation='nearest')
    
    pyplot.subplot(324)
    H, xedges, yedges = numpy.histogram2d(
        [s.color for s in r.stars],
        [s.magnitude for s in r.stars],
        normed=True,
        bins=(100,100))
    
    extent = [xedges[0], xedges[-1] * 10, yedges[0], yedges[-1]]                
    pyplot.imshow(H,
                  cmap=pyplot.cm.gray_r,
                  extent=extent,
                  interpolation='nearest')

    from mpl_toolkits.mplot3d import axes3d

    axes = pyplot.subplot(325, projection='3d')
    axes.scatter([s.color for s in d.stars],
                 [s.magnitude for s in d.stars],
                 [s.offset for s in d.stars])

    axes = pyplot.subplot(326, projection='3d')
    axes.scatter([s.color for s in r.stars],
                 [s.magnitude for s in r.stars],
                 [s.offset for s in r.stars])

    pyplot.show()
