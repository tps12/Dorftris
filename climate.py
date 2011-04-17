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

                t = ins * (1-h/11000.0) if h > 0 else ins
                self.climate[(x,y)] = d, t, (0.5 + exp(t)/e2) * (h <= 0), 0

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
                    
        self.dirty = True

    def _definemapping(self):
        mapping = {}

        def addmap(s, d, w):
            if d in mapping:
                l = mapping[d]
            else:
                l = []
                mapping[d] = l
            l.append((s,w))

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

    def iterateclimate(self):
        e2 = 2 * exp(1)
        for y in range(len(self.tiles)):
            ins = self.insolation(y)
            
            for x in range(len(self.tiles[y])):
                climate = self.climate[(x,y)]

                sws = self._mapping[(x,y)]
                    
                t = h = 0
                for s, w in sws:
                    st, sh = self.climate[s][1:3]
                    t += st * w
                    h += sh * w
                
                if self.tiles[y][x][2] > 0:
                    t += 0.0125 * ins
                    t = min(t, (1-self.tiles[y][x][2]/11000.0))
                else:
                    h += 0.125
                    
                h = min(h, (0.5 + exp(t)/e2))

                convective = max(0, min(h, t - climate[1]))
                h -= convective

                stratiform = max(0, climate[2] - h)
                h = max(0, h - stratiform)

                p = climate[3] + convective + stratiform
                
                self._scratch[(x,y)] = (climate[0], climate[1], h, p)

        swap = self.climate
        self.climate = self._scratch
        self._scratch = swap

        self.dirty = True

    def average(self, steps):
        self.resetclimate()

        c = [[(0,0) for x in range(len(self.tiles[y]))]
             for y in range(len(self.tiles))]
        for (x,y), (d,t,h,p) in self.climate.iteritems():
            c[y][x] = t, h, p
        
        for i in range(steps):
            self.iterateclimate()
            for (x,y), (d,t,h,p) in self.climate.iteritems():
                c[y][x] = c[y][x][0] + t, c[y][x][1] + h, c[y][x][2] + p
            
        value = [[(self.tiles[y][x][2], tuple([n/(steps+1) for n in c[y][x]]))
                  for x in range(len(self.tiles[y]))]
                 for y in range(len(self.tiles))]
        return value

    def update(self):
        if not self.climate:
            self.resetclimate()

        if self.run:
            self.iterateclimate()
