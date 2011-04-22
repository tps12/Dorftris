from cPickle import dump, load
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos

from etopo import Earth

from climateclassification import ClimateClassification

def cells(r):
    c = int(r/6400.0 + 2)
    if c < 1:
        c = 1
    elif not (c&1):
        c -= 1
    return c

def distance(c1, c2):
    lat1, lon1 = [c * pi/180 for c in c1]
    lat2, lon2 = [c * pi/180 for c in c2]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * atan2(sqrt(a), sqrt(1-a))

def bearing(c1, c2):
    lat1, lon1 = [c * pi/180 for c in c1]
    lat2, lon2 = [c * pi/180 for c in c2]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    theta = atan2(sin(dlon) * cos(lat2),
                  cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon))
    return (theta * 180/pi) % 360   

class ClimateDict(object):
    def __init__(self, dimensions):
        self._xmax, self._ymax = dimensions
        self._list = [None for i in range(self._xmax * self._ymax)]
        self.clear()

    def _index(self, p):
        return p[0] + p[1] * self._xmax

    def __getitem__(self, p):
        isset, value = self._list[self._index(p)]
        if not isset:
            raise KeyError
        return value

    def __setitem__(self, p, value):
        self._list[self._index(p)] = True, value

    def __delitem__(self, p):
        self._list[self._index(p)] = None, None

    def clear(self):
        for i in range(len(self._list)):
            self._list[i] = None, None

    def iteritems(self):
        for y in range(self._ymax):
            for x in range(self._xmax):
                isset, value = self._list[self._index((x,y))]
                if isset:
                    yield (x,y), value

    def __len__(self):
        return len(list(self.iteritems()))

class ClimateSimulation(object):
    ADJ_CACHE = '.adj.pickle'

    maxelevation = 9000.0
    temprange = (-25.0, 50.0)
    sealevel = 0
    
    def __init__(self):
        self.planet = Earth()

        degrees = 2

        self.tiles = []
        for lat in range(-89, 91, degrees):
            r = cos(lat * pi/180)
            row = []
            d = 2 / r
            lon = d/2
            while lon <= 180:
                row = ([(lat, -lon, self.planet.sample(lat, -lon))] +
                       row +
                       [(lat, lon, self.planet.sample(lat, lon))])
                lon += d
            self.tiles.append(row)

        try:
            with open(self.ADJ_CACHE, 'r') as f:
                res, self.adj = load(f)
                if res != len(self.tiles):
                    raise Exception('Resolution mismatch')
        except Exception as er:
            print 'Cached adjacency list failed:', repr(er)
            self.adj = {}

            def addadj(t1, t2):
                if t1 in self.adj:
                    adj = self.adj[t1]
                else:
                    adj = []
                    self.adj[t1] = adj
                adj.append(t2)

            def addadjes(t1, t2):
                addadj(t1, t2)
                addadj(t2, t1)

            limit = 1.5 * degrees * (pi/180)
            
            for i in range(1, len(self.tiles)):
                for j in range(len(self.tiles[i])):
                    c1 = self.tiles[i][j][0:2]
                    for k in range(len(self.tiles[i-1])):
                        if distance(c1, self.tiles[i-1][k][0:2]) < limit:
                            addadjes((j,i),(k,i-1))
                    addadj((j,i),(j-1 if j > 0 else len(self.tiles[i])-1, i))
                    addadj((j,i),(j+1 if j < len(self.tiles[i])-1 else 0, i))

            with open(self.ADJ_CACHE, 'w') as f:
                dump((len(self.tiles), self.adj), f, 0)

        xmax = max([len(self.tiles[i]) for i in range(len(self.tiles))])

        dimensions = xmax, len(self.tiles)
        (self.climate,
         self.precipitation,
         self.convective,
         self.seabased,
         self.temperature) = [ClimateDict(dimensions) for i in range(5)]

        self.dirty = True

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        self._tilt = value
        self.climate.clear()

    @property
    def season(self):
        return self._season

    @season.setter
    def season(self, value):
        self._season = value
        self.climate.clear()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self.climate.clear()

    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, value):
        self._spin = value
        self.climate.clear()

    def insolation(self, y):
        theta = 2 * pi * (y - len(self.tiles)/2)/len(self.tiles)/2
        theta += (self.tilt * pi/180) * self.season
        ins = max(0, cos(theta))
        return 0.5 + (ins - 0.5) * cos(self.tilt * pi/180)

    def resetclimate(self):
        res = max([len(r) for r in self.tiles]), len(self.tiles)
        
        c = cells(self.radius)

        e2 = 2 * exp(1)
        for y in range(res[1]):
            n = abs(y + 0.5 - res[1]/2)/(float(res[1]/2)/c)
            n = int(n) & 1
            n = n if y >= res[1]/2 else not n
            d = 180 - 180 * n

            s = self.spin
            ce = 2 * s * sin(2 * pi * (y - res[1]/2)/res[1]/2)
            d += atan2(ce, 1) * 180/pi
            d %= 360

            ins = self.insolation(y)
            
            for x in range(len(self.tiles[y])):
                h = self.tiles[y][x][2]

                t = (ins * (1-(h - self.sealevel)/(self.maxelevation - self.sealevel))
                     if h > self.sealevel else ins)
                p = (cos((self.tiles[y][x][0]*2*c + self.tilt*self.season)*pi/180) + 1)/2
                self.climate[(x,y)] = (d,)
                self.temperature[(x,y)] = t
                self.seabased[(x,y)] = None
                self.convective[(x,y)] = p

        self.sadj = {}
        for (x,y), ns in self.adj.iteritems():
            c = self.tiles[y][x][0:2]
            d = self.climate[(x,y)][0]
            self.sadj[(x,y)] = sorted(self.adj[(x,y)],
                                      key=lambda a: cos(
                                          (bearing(c,
                                                   self.tiles[a[1]][a[0]][0:2])
                                           - d) * pi / 180))
        self._definemapping()
        self._seabreeze()
                    
        self.dirty = True

    def _seabreeze(self):
        frontier = []
        d = 0
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if self.tiles[y][x][2] <= self.sealevel:
                    self.seabased[(x,y)] = d
                    frontier.append((x,y))
                    
        while d < 10 and frontier:
            d += 1
            frontier = self._propagate(frontier, d)
            
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                seabased = self.seabased[(x,y)]
                if seabased is None:
                    h = 0
                else:
                    h = ((d - seabased)/float(d))**2
                p = min(1.0, h + self.convective[(x,y)])
                self.precipitation[(x,y)] = p
                self.seabased[(x,y)] = h
                
    def _propagate(self, sources, d):
        frontier = []
        for s in sources:
            for a in [p for (p,w) in self._destmap[s]]:
                if self.seabased[a] is None:
                    self.seabased[a] = d
                    frontier.append(a)
        return frontier

    def _definemapping(self):
        mapping = {}
        dests = {}

        def addmap(s, d, w):
            if d in mapping:
                l = mapping[d]
            else:
                l = []
                mapping[d] = l
            l.append((s,w))

            if s in dests:
                l = dests[s]
            else:
                l = []
                dests[s] = l
            l.append((d,w))

        seen = set()

        # map destinations for every tile
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                s = self.sadj[(x,y)]
                
                nws = [(a, cos((bearing(
                    self.tiles[y][x][0:2],
                    self.tiles[a[1]][a[0]][0:2])
                        - self.climate[(x,y)][0])*pi/180))
                       for a in self.sadj[(x,y)]]
                nws = [nw for nw in nws if nw[1] > 0]

                for n, w in nws:
                    addmap((x,y), n, w)
                    seen.add(n)

        # map from sources for any tile that hasn't been targeted
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if (x,y) not in seen:
                    s = self.sadj[(x,y)]

                    nws = [(a, -cos((bearing(
                        self.tiles[y][x][0:2],
                        self.tiles[a[1]][a[0]][0:2])
                            - self.climate[a][0])*pi/180))
                           for a in self.sadj[(x,y)]]
                    nws = [nw for nw in nws if nw[1] > 0]
                    
                    for n, w in nws:
                        addmap(n, (x,y), w)

        # normalize weights
        self._mapping = {}
        for (d, sws) in mapping.iteritems():
            t = sum([w for (s, w) in sws])
            self._mapping[d] = [(s, w/t) for (s,w) in sws]

        self._destmap = {}
        for (s, dws) in dests.iteritems():
            t = sum([w for (d, w) in dws])
            self._destmap[s] = [(d, w/t) for (d,w) in dws]

    def sources(self, p):
        return self._mapping[p]

    def average(self):
        self.resetclimate()
        return self._getaverage()

    def _getaverage(self):
        c = [[(0,0) for x in range(len(self.tiles[y]))]
             for y in range(len(self.tiles))]
        for (x,y), (d,) in self.climate.iteritems():
            c[y][x] = (self.tiles[y][x][2],
                       self.temperature[(x,y)],
                       self.precipitation[(x,y)])

        return c

    def classify(self, seasons):
        ss = []
        for s in seasons:
            self.season = s
            ss.append(self.average())
            
        seasons = []
        for y in range(len(ss[0])):
            row = []
            for x in range(len(ss[0][y])):
                row.append((ss[0][y][x][0],
                            [ss[i][y][x][1:] for i in range(len(ss))]))
            seasons.append(row)

        return ClimateClassification(seasons, self.temprange)
    
    def update(self):
        if not self.climate:
            self.resetclimate()
