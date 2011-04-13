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

        self.climate = {}

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

        self.dirty = True

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
            
            c = self.tiles[y][x][0:2]
            s = sorted(self.adj[(x,y)],
                       key=lambda a: cos(
                           (bearing(c, self.tiles[a[1]][a[0]][0:2]) - d) *
                           pi / 180))
            ns = s[-3:]

            for n in ns:
                de = self.tiles[n[1]][n[0]][2] - self.tiles[y][x][2]
                h *= max(0, min(1, 1 - (de / 4000)))
                
                addd(n, (t,h), 0.5 if n is s[-1] else 0.25)

            seen.add(n)

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if (x,y) not in seen:
                    c = self.tiles[y][x][0:2]
                    s = sorted(self.adj[(x,y)],
                               key=lambda a: cos(
                                   (bearing(c, self.tiles[a[1]][a[0]][0:2]) - d) *
                                   pi / 180))
                    ns = s[:3]
                    for n in ns:
                        d,t,h = self.climate[n]
                                            
                        de = self.tiles[y][x][2] - self.tiles[n[1]][n[0]][2]
                        h *= max(0, min(1, 1 - (de / 4000)))
                    
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
            climate = self.climate[(x,y)]
            self.climate[(x,y)] = (climate[0],
                                   0.5 * climate[1] + 0.5 * t,
                                   0.5 * climate[2] + 0.5 * h * (0.5 + exp(t)/e2))

        self.dirty = True

    def update(self):
        if not self.climate:
            self.resetclimate()

        if self.run:
            self.iterateclimate()
