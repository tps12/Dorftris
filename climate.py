from cPickle import dump, load
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos

from etopo import Earth

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
    
    def __init__(self):
        self.planet = Earth()

        self.tiles = []
        for lat in range(-89, 91, 2):
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
                self.adj = load(f)
        except Exception as er:
            print repr(er)
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
            
            for i in range(1, len(self.tiles)):
                for j in range(len(self.tiles[i])):
                    c1 = self.tiles[i][j][0:2]
                    for k in range(len(self.tiles[i-1])):
                        if distance(c1, self.tiles[i-1][k][0:2]) < pi/60:
                            addadjes((j,i),(k,i-1))
                    addadj((j,i),(j-1 if j > 0 else len(self.tiles[i])-1, i))
                    addadj((j,i),(j+1 if j < len(self.tiles[i])-1 else 0, i))

            with open(self.ADJ_CACHE, 'w') as f:
                dump(self.adj, f, 0)

        xmax = max([len(self.tiles[i]) for i in range(len(self.tiles))])
        self.climate, self._scratch = [ClimateDict((xmax, len(self.tiles)))
                                       for i in range(2)]

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

    @property
    def run(self):
        return self._run

    @run.setter
    def run(self, value):
        self._run = value

    def insolation(self, y):
        theta = 2 * pi * (y - len(self.tiles)/2)/len(self.tiles)/2
        theta += (self.tilt * pi/180) * self.season
        ins = max(0, cos(theta))
        return 0.5 + (ins - 0.5) * cos(self.tilt * pi/180)

    def resetclimate(self):
        res = max([len(r) for r in self.tiles]), len(self.tiles)
        
        c = cells(self.radius)

        for y in range(res[1]):
            n = abs(y + 0.5 - res[1]/2)/(float(res[1]/2)/c)
            n = int(n) & 1
            n = n if y >= res[1]/2 else not n
            d = 180 - 180 * n

            s = self.spin
            ce = 2 * s * sin(2 * pi * (y - res[1]/2)/res[1]/2)
            d += atan2(ce, 1) * 180/pi
            d %= 360
            
            for x in range(len(self.tiles[y])):
                h = self.tiles[y][x][2]
                ins = self.insolation(y)
                
                self.climate[(x,y)] = d, ins, 1.0 * (h <= 0)

        self.sadj = {}
        for (x,y), ns in self.adj.iteritems():
            c = self.tiles[y][x][0:2]
            self.sadj[(x,y)] = sorted(self.adj[(x,y)],
                                      key=lambda a: cos(
                                          (bearing(c,
                                                   self.tiles[a[1]][a[0]][0:2])
                                           - d) * pi / 180))

        self._definemapping()
                    
        self.dirty = True

    def _definemapping(self):
        mapping = {}

        def addmap(s, d, w):
            if s in mapping:
                l = mapping[s]
            else:
                l = []
                mapping[s] = l
            l.append((d,w))

        seen = set()

        # map destinations for every tile
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                s = self.sadj[(x,y)]
                ns = s[-3:]

                for n in ns:
                    addmap((x,y), n, 0.5 if n is s[-1] else 0.25)
                    seen.add(n)

        # map from sources for any tile that hasn't been targeted
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if (x,y) not in seen:
                    s = self.sadj[(x,y)]
                    ns = s[:3]
                    
                    for n in ns:
                        addmap(n, (x,y), 0.5 if n is s[0] else 0.25)

        # normalize weights
        self._mapping = {}
        for (s, dws) in mapping.iteritems():
            t = sum([w for (d, w) in dws])
            self._mapping[s] = [(d, w/t) for (d,w) in dws]

    def iterateclimate(self):
        dc = {}

        def addd(d, s, i):
            if d in dc:
                l = dc[d]
            else:
                l = []
                dc[d] = l
            l.append((s, i))

        seen = set()

        for ((x,y), (d,t,h)) in self.climate.iteritems():
            if (x,y) not in self.adj:
                continue
            
            s = self.sadj[(x,y)]
            ns = s[-3:]

            for n in ns:
                addd(n, (t,h), 0.5 if n is s[-1] else 0.25)

                seen.add(n)

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if (x,y) not in seen:
                    s = self.sadj[(x,y)]
                    ns = s[:3]
                    for n in ns:
                        d,t,h = self.climate[n]
                    
                        addd((x,y), (t,h), 0.5 if n is s[0] else 0.25)

        for y in range(len(self.tiles)):
            ins = self.insolation(y)
            
            for x in range(len(self.tiles[y])):
                if self.tiles[y][x][2] <= 0:
                    h = 1.0
                else:
                    h = max(0, self.climate[(x,y)][2] - 0.025 * ins)
                    self.climate[(x,y)] = self.climate[(x,y)][0:2] + (h,)
                    
        e2 = 2 * exp(1)
        for ((x,y), ss) in dc.iteritems():
            nt, nh = [sum([e[0][i] * e[1] for e in ss]) for i in range(2)]
            d = sum([e[1] for e in ss])
            t, h = nt / d, nh / d
            if self.tiles[y][x][2] > 0:
                t = max(t, self.tiles[y][x][2]/11000)
            
            climate = self.climate[(x,y)]
            self.climate[(x,y)] = (climate[0],
                                   0.5 * climate[1] + 0.5 * t,
                                   0.5 * climate[2] + 0.5 * h * (0.5 + exp(t)/e2))

        self.dirty = True

    def average(self, steps):
        self.resetclimate()

        c = [[(0,0) for x in range(len(self.tiles[y]))]
             for y in range(len(self.tiles))]
        for (x,y), (d,t,h) in self.climate.iteritems():
            c[y][x] = t, h
        
        for i in range(steps):
            self.iterateclimate()
            for (x,y), (d,t,h) in self.climate.iteritems():
                c[y][x] = c[y][x][0] + t, c[y][x][1] + h
            
        value = [[(self.tiles[y][x][2], tuple([n/(steps+1) for n in c[y][x]]))
                  for x in range(len(self.tiles[y]))]
                 for y in range(len(self.tiles))]
        return value

    def update(self):
        if not self.climate:
            self.resetclimate()

        if self.run:
            self.iterateclimate()
