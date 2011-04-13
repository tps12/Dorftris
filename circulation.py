import gettext
gettext.install('dorftris')

from cPickle import dump, load

from math import asin, acos, atan2, pi, exp, sqrt, sin, cos

import wx, pygame
from pygame.locals import *

from etopo import Earth

def radius(i):
    return i*1600

def rotation(i):
    return i*10

def spin(i):
    a = abs(i)
    s = i / a if i else 1
    return s * pow(sqrt(360), a / 5.0)

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

def season(i):
    return [-1,
            -0.5,
            0,
            0.5,
            1,
            0.5,
            0,
            -0.5][i]

def colorscale(v):
    m = 1275
    r = (255 - m * v if v < 0.2 else
         0 if v < 0.6 else
         m * (v - 0.6) if v < 0.8 else
         255)
    g = (0 if v < 0.2 else
         m * (v - 0.2) if v < 0.4 else
         255 if v < 0.8 else
         255 - m * (v - 0.8))
    b = (255 if v < 0.4 else
         255 - m * (v - 0.4) if v < 0.6 else
         0)
    return r, g, b

def warmscale(v):
    m = 510
    r = 255
    g = v * m if v < 0.5 else 255
    b = 0 if v < 0.5 else m * (v - 0.5)
    return r, g, b

def coolscale(v):
    m = 1020
    r = 255 - m * v if v < 0.25 else 0
    g = (255 if v < 0.75 else
         255 - m * (v - 0.75))
    b = (255 - m * v if v < 0.25 else
         m * (v - 0.25) if v < 0.5 else
         255)
    return r, g, b

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

        self.selected = None
        self.adjacent = []
        self._screen = None

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        self._tilt = value
        self.climate.clear()
        self._screen = None

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self._screen = None

    @property
    def season(self):
        return self._season

    @season.setter
    def season(self, value):
        self._season = value
        self.climate.clear()
        self._screen = None

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self.climate.clear()
        self._screen = None

    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, value):
        self._spin = value
        self.climate.clear()
        self._screen = None

    @property
    def run(self):
        return self._run

    @run.setter
    def run(self, value):
        self._run = value
        self._screen = None

    @property
    def airflow(self):
        return self._airflow

    @airflow.setter
    def airflow(self, value):
        self._airflow = value
        self._screen = None

    TERRAIN = 0
    INSOLATION = 1
    TEMPERATURE = 2
    HUMIDITY = 3
    CLIMATE = 4

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self._screen = None

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

        self._screen = None

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

        self._screen = None

    def handle(self, e):
        if e.type == MOUSEBUTTONUP:
            mx, my = e.pos

            res = max([len(r) for r in self.tiles]), len(self.tiles)

            y = my / (self.size[1]/res[1])
            x = mx / (self.size[0]/res[0]) - (res[0] - len(self.tiles[y]))/2

            r = self.rotate
            o = r * len(self.tiles[y])/360

            xo = x + o
            if xo > len(self.tiles[y])-1:
                xo -= len(self.tiles[y])
            elif xo < 0:
                xo += len(self.tiles[y])
            
            if 0 <= y < len(self.tiles) and 0 <= xo < len(self.tiles[y]):
                if self.selected == (xo,y):
                    self.selected = None
                    self.adjacent = []
                else:
                    self.selected = (xo,y)
                    self.adjacent = self.adj[self.selected]

                self._screen = None

                return True

        return False
    
    def draw(self, surface):
        if not self.climate:
            self.resetclimate()

        if self.run:
            self.iterateclimate()
            
        if not self._screen or self._screen.get_size() != surface.get_size():
            self._screen = pygame.Surface(surface.get_size(), 0, 32)
            
            self.size = self._screen.get_size()
        
            self._screen.fill((0,0,0))

            res = max([len(r) for r in self.tiles]), len(self.tiles)
            template = pygame.Surface((self.size[0]/res[0],
                                       self.size[1]/res[1]), 0, 32)

            for y in range(res[1]):
                for x in range(len(self.tiles[y])):
                    block = template.copy()

                    r = self.rotate
                    o = r * len(self.tiles[y])/360

                    xo = x + o
                    if xo > len(self.tiles[y])-1:
                        xo -= len(self.tiles[y])
                    elif xo < 0:
                        xo += len(self.tiles[y])
                    h = self.tiles[y][xo][2]

                    climate = self.climate[(xo,y)]

                    if self.selected == (xo, y):
                        color = (255,0,255)
                    elif (xo, y) in self.adjacent:
                        color = (127,0,255)
                    elif self.mode == self.INSOLATION:
                        ins = self.insolation(y)                    
                        color = warmscale(ins)
                    elif h > 0:
                        if self.mode == self.CLIMATE:
                            color = (int(255 * (1 - climate[2])),
                                     255,
                                     int(255 * (1 - climate[1])))
                        elif self.mode == self.TEMPERATURE:
                            color = colorscale(climate[1])
                        elif self.mode == self.HUMIDITY:
                            color = coolscale(climate[2])
                        else:
                            color = (0,int(255 * (h/9000.0)),0)
                    else:
                        if self.mode == self.TEMPERATURE:
                            color = [(c+255)/2 for c in colorscale(climate[1])]
                        else:
                            color = (0,0,int(255 * (1 + h/11000.0)))

                    block.fill(color)

                    if self.airflow:
                        s = sin(pi/2 * (y - res[1]/2)/res[1]/2) * 90
                        s *= sin(pi/2 * (x - len(self.tiles[y])/2)/(len(self.tiles[y])/2))

                        w, h = [c-1 for c in block.get_size()]

                        angle = climate[0] + s
                        if angle >= 337.5 or angle < 22.5:
                            p = w/2, h-1
                            es = (0, 0), (w-1, 0)
                        elif 22.5 <= angle < 67.5:
                            p = w-1, h-1
                            es = (0, h-1), (w-1, 0)
                        elif 67.5 <= angle < 112.5:
                            p = w-1, h/2
                            es = (0, 0), (0, h-1)
                        elif 112.5 <= angle < 157.5:
                            p = w-1, 0
                            es = (w-1, h-1), (0, 0)
                        elif 157.5 <= angle < 202.5:
                            p = w/2, 0
                            es = (0, h-1), (w-1, h-1)
                        elif 202.5 <= angle < 247.5:
                            p = 0, 0
                            es = (0, h-1), (w-1, 0)
                        elif 247.5 <= angle < 292.5:
                            p = 0, h/2
                            es = (w-1, 0), (w-1, h-1)
                        else:
                            p = 0, h-1
                            es = (0, 0), (w-1, h-1)

                        pygame.draw.lines(block, (255,255,255), False,
                                          [es[0], p, es[1]])
                   
                    self._screen.blit(block,
                                      ((x + (res[0] - len(self.tiles[y]))/2)*block.get_width(),
                                       y*block.get_height()))
                    
        surface.blit(self._screen, (0,0))

class PygameDisplay(wx.Window):
    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID)
        self.parent = parent
        self.hwnd = self.GetHandle()
       
        self.size = self.GetSizeTuple()
        self.size_dirty = True
       
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
       
        self.fps = 60.0
        self.timespacing = 1000.0 / self.fps
        self.timer.Start(self.timespacing, False)

        self.climate = ClimateSimulation()

    def Update(self, event):
        # Any update tasks would go here (moving sprites, advancing animation frames etc.)
        self.Redraw()

    def OnClick(self, event):
        self.climate.handle(pygame.event.Event(MOUSEBUTTONUP,
                                               {'button': 1,
                                                'pos': event.Position.Get()}))

    def Redraw(self):
        if self.size_dirty:
            self.screen = pygame.Surface(self.size, 0, 32)
            self.size_dirty = False

        self.climate.draw(self.screen)

        s = pygame.image.tostring(self.screen, 'RGB')  # Convert the surface to an RGB string
        img = wx.ImageFromData(self.size[0], self.size[1], s)  # Load this string into a wx image
        bmp = wx.BitmapFromImage(img)  # Get the image in bitmap form
        dc = wx.ClientDC(self)  # Device context for drawing the bitmap
        dc.DrawBitmap(bmp, 0, 0, False)  # Blit the bitmap image to the display
        del dc
 
    def OnPaint(self, event):
        self.Redraw()
        event.Skip()  # Make sure the parent frame gets told to redraw as well
 
    def OnSize(self, event):
        self.size = self.GetSizeTuple()
        self.size_dirty = True
 
    def Kill(self, event):
        # Make sure Pygame can't be asked to redraw /before/ quitting by unbinding all methods which
        # call the Redraw() method
        # (Otherwise wx seems to call Draw between quitting Pygame and destroying the frame)
        # This may or may not be necessary now that Pygame is just drawing to surfaces
        self.Unbind(event = wx.EVT_PAINT, handler = self.OnPaint)
        self.Unbind(event = wx.EVT_TIMER, handler = self.Update, source = self.timer)
 
class Frame(wx.Frame):
    @staticmethod
    def radstr(i):
        return '{r} km'.format(r=radius(i))

    @staticmethod
    def spinstr(i):
        s = spin(i)
        return '{w:.0f} d/y {dir}'.format(w=abs(s),
                                          dir=u' to '.join(
                                              (u'W',u'E')
                                              if s > 0 else
                                              (u'E',u'W')))

    @staticmethod
    def tiltstr(d):
        return u'{d}\u00b0'.format(d=d)

    @staticmethod
    def seasonstr(i):
        return [u'Southern solstice',
                u'Northern spring',
                u'Northward equinox',
                u'Northern summer',
                u'Northern solstice',
                u'Southern spring',
                u'Southward equinox',
                u'Southern summer'][i]
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, size = (1600, 1000))
       
        self.display = PygameDisplay(self, -1)
       
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)
       
        self.curframe = 0
       
        self.SetTitle(self.display.climate.planet.name)
       
        self.slider = wx.Slider(self, wx.ID_ANY, 4, 1, 80, style = wx.SL_HORIZONTAL)
        self.display.climate.radius = radius(self.slider.Value)
        self.radius = wx.TextCtrl(self, wx.ID_ANY,
                                  self.radstr(self.slider.Value))
       
        self.order = wx.Slider(self, wx.ID_ANY, 10, -15, 15, style = wx.SL_HORIZONTAL)
        self.order.Bind(wx.EVT_SCROLL, self.OnSpin)
        self.display.climate.spin = spin(self.order.Value)/360.0
        self.spin = wx.TextCtrl(self, wx.ID_ANY,
                                self.spinstr(self.order.Value))
       
        self.tilt = wx.Slider(self, wx.ID_ANY, 23, 0, 90, style = wx.SL_HORIZONTAL)
        self.display.climate.tilt = self.tilt.Value
        self.tilt.Bind(wx.EVT_SCROLL, self.OnTilt)
        self.angle = wx.TextCtrl(self, wx.ID_ANY,
                                 self.tiltstr(self.tilt.Value))
       
        self.timer = wx.Timer(self)
       
        self.Bind(wx.EVT_SCROLL, self.OnScroll)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
       
        self.timer.Start((1000.0 / self.display.fps))
       
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer2.Add(self.slider, 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer2.Add(self.radius, 0, flag = wx.EXPAND | wx.ALL, border = 5)
        
        self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer4.Add(self.order, 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer4.Add(self.spin, 0, flag = wx.EXPAND | wx.ALL, border = 5)
        
        self.sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer3.Add(self.tilt, 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer3.Add(self.angle, 0, flag = wx.EXPAND | wx.ALL, border = 5)
        
        self.sizer.Add(self.sizer2, 0, flag = wx.EXPAND)
        self.showair = wx.CheckBox(self, wx.ID_ANY, u'Show circulation')
        self.sizer.Add(self.showair, 0, flag = wx.EXPAND)
        
        self.sizer.Add(self.sizer4, 0, flag = wx.EXPAND)

        self.sizer.Add(self.sizer3, 0, flag = wx.EXPAND)

        self.time = wx.Slider(self, wx.ID_ANY, 2, 0, 7, style = wx.SL_HORIZONTAL)
        self.display.climate.season = season(self.time.Value)
        self.season = wx.TextCtrl(self, wx.ID_ANY,
                                  self.seasonstr(self.time.Value))
        self.time.Bind(wx.EVT_SCROLL, self.OnSeason)

        self.sizer6 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer6.Add(self.time, 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer6.Add(self.season, 0, flag = wx.EXPAND | wx.ALL, border = 5)

        self.sizer.Add(self.sizer6, 0, flag = wx.EXPAND)

        self.showinsol = wx.CheckBox(self, wx.ID_ANY, u'Show insolation')
        self.sizer.Add(self.showinsol, 0, flag = wx.EXPAND)

        self.showtemp = wx.CheckBox(self, wx.ID_ANY, u'Show temperature')
        self.showhum = wx.CheckBox(self, wx.ID_ANY, u'Show humidity')
        self.showclime = wx.CheckBox(self, wx.ID_ANY, u'Show climate')
        self.run = wx.CheckBox(self, wx.ID_ANY, u'Iterate')
        def onrun(event):
            self.display.climate.run = self.run.Value
        self.Bind(wx.EVT_CHECKBOX, onrun, self.run)
        onrun(None)
        self.iterate = wx.Button(self, wx.ID_ANY, u'Step')
        self.iterate.Bind(wx.EVT_BUTTON, self.OnIterate)
        self.reset = wx.Button(self, wx.ID_ANY, u'Reset')
        self.reset.Bind(wx.EVT_BUTTON, self.OnReset)

        self.sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer5.Add(self.showtemp, 0, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer5.Add(self.showhum, 0, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer5.Add(self.showclime, 0, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer5.Add(self.run, 0, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer5.Add(self.iterate, 0, flag = wx.EXPAND | wx.ALL, border = 5)
        self.sizer5.Add(self.reset, 0, flag = wx.EXPAND | wx.ALL, border = 5)

        def mode(event):
            self.display.climate.mode = (
                ClimateSimulation.INSOLATION if self.showinsol.Value else
                ClimateSimulation.TEMPERATURE if self.showtemp.Value else
                ClimateSimulation.HUMIDITY if self.showhum.Value else
                ClimateSimulation.CLIMATE if self.showclime.Value else
                ClimateSimulation.TERRAIN)

        self.Bind(wx.EVT_CHECKBOX, mode, self.showinsol)
        self.Bind(wx.EVT_CHECKBOX, mode, self.showtemp)
        self.Bind(wx.EVT_CHECKBOX, mode, self.showhum)
        self.Bind(wx.EVT_CHECKBOX, mode, self.showclime)
        mode(None)

        def air(event):
            self.display.climate.airflow = self.showair.Value
        self.Bind(wx.EVT_CHECKBOX, air, self.showair)
        air(None)

        self.sizer.Add(self.sizer5, 0, flag = wx.EXPAND)

        self.sizer.Add(self.display, 1, flag = wx.EXPAND)

        self.rotate = wx.Slider(self, wx.ID_ANY, 0, -18, 18, style = wx.SL_HORIZONTAL)
        def onrotate(event):
            self.display.climate.rotate = rotation(self.rotate.Value)
        self.Bind(wx.EVT_SCROLL,
                  onrotate,
                  self.rotate)
        onrotate(None)
        self.sizer.Add(self.rotate, 0, flag = wx.EXPAND)
       
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()

    def OnIterate(self, event):
        self.display.climate.iterateclimate()

    def OnReset(self, event):
        self.display.climate.resetclimate()
 
    def Kill(self, event):
        self.display.Kill(event)
        self.Destroy()
 
    def OnSize(self, event):
        self.Layout()
 
    def Update(self, event):
        pass
 
    def OnScroll(self, event):
        self.display.climate.radius = radius(self.slider.Value)
        self.radius.Value = self.radstr(self.slider.Value)

    def OnTilt(self, event):
        self.display.climate.tilt = self.tilt.Value
        self.angle.Value = self.tiltstr(self.tilt.Value)

    def OnSpin(self, event):
        self.display.climate.spin = spin(self.order.Value)/360.0
        self.spin.Value = self.spinstr(self.order.Value)

    def OnSeason(self, event):
        self.display.climate.season = season(self.time.Value)
        self.season.Value = self.seasonstr(self.time.Value)
 
class App(wx.App):
    def __init__(self, redirect=True):
        wx.App.__init__(self, redirect)
        
    def OnInit(self):
        pygame.font.init()
        
        self.frame = Frame(parent = None)
        self.frame.Show()
        self.SetTopWindow(self.frame)
       
        return True
 
if __name__ == "__main__":
    app = App(False)
    app.MainLoop()
