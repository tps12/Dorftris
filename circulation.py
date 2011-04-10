import gettext
gettext.install('dorftris')

from math import asin, acos, pi, sqrt, sin, cos

import wx, pygame

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
       
        self.fps = 60.0
        self.timespacing = 1000.0 / self.fps
        self.timer.Start(self.timespacing, False)
 
        self.planet = Earth()

        self.tiles = []
        for lat in range(-88, 88, 2):
            r = cos(lat * pi/180)
            row = []
            d = 2 / r
            lon = d/2
            while lon <= 180:
                row = ([self.planet.sample(lat, -lon)] +
                       row +
                       [self.planet.sample(lat, lon)])
                lon += d
            self.tiles.append(row)

    def Update(self, event):
        # Any update tasks would go here (moving sprites, advancing animation frames etc.)
        self.Redraw()

    def Redraw(self):
        if self.size_dirty:
            self.screen = pygame.Surface(self.size, 0, 32)
            self.size_dirty = False

        self.screen.fill((0,0,0))

        res = max([len(r) for r in self.tiles]), len(self.tiles)
        template = pygame.Surface((self.size[0]/res[0],self.size[1]/res[1]), 0, 32)

        size = min(self.size[0]/res[0], self.size[1]/res[1])

        arrow = pygame.Surface(2*(int(size/sqrt(2)),), 0, 32)
        pygame.draw.polygon(arrow, (255,255,255),
                            [(0,arrow.get_height()-1),
                             (arrow.get_width()/2, 0),
                             (arrow.get_width()-1,arrow.get_height()-1)])
        
        c = cells(radius(self.parent.slider.Value))

        for y in range(res[1]):

            n = abs(y - res[1]/2)/(float(res[1]/2)/c)
            n = int(n) & 1
            n = n if y > res[1]/2 else not n
            d = 180 * n
            
            for x in range(len(self.tiles[y])):
                block = template.copy()

                r = rotation(self.parent.rotate.Value)
                o = r * len(self.tiles[y])/360

                xo = x + o
                if xo > len(self.tiles[y])-1:
                    xo -= len(self.tiles[y])
                h = self.tiles[y][xo]

                if self.parent.showinsol.Value:
                    ins = cos(2 * pi * (y - res[1]/2)/res[1]/2)

                    ins = 0.5 + (ins - 0.5) * cos(self.parent.tilt.Value * pi/180)
                    
                    color = (255,
                             255 if ins >= 0.5 else int(255 * ins * 2),
                             0 if ins < 0.5 else int(255 * (ins - 0.5) * 2))
                else:
                    color = ((0,int(255 * (h/9000.0)),0) if h > 0
                             else (0,0,int(255 * (1 + h/11000.0))))

                block.fill(color)

                if self.parent.showair.Value:
                    s = sin(pi/2 * (y - res[1]/2)/res[1]/2) * 90
                    s *= sin(pi/2 * (x - len(self.tiles[y])/2)/(len(self.tiles[y])/2))
                    angle = pygame.transform.rotate(arrow, d + s)

                    block.blit(angle, ((block.get_width() - angle.get_width())/2,
                                       (block.get_height() - angle.get_height())/2))
                
                self.screen.blit(block, ((x + (res[0] - len(self.tiles[y]))/2)*
                                         block.get_width(),
                                         y*block.get_height()))

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
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, size = (600, 600))
       
        self.display = PygameDisplay(self, -1)
       
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)
       
        self.curframe = 0
       
        self.SetTitle(self.display.planet.name)
       
        self.slider = wx.Slider(self, wx.ID_ANY, 4, 1, 80, style = wx.SL_HORIZONTAL)
        self.radius = wx.TextCtrl(self, wx.ID_ANY,
                                  self.radstr(self.slider.Value))
       
        self.order = wx.Slider(self, wx.ID_ANY, 10, -15, 15, style = wx.SL_HORIZONTAL)
        self.order.Bind(wx.EVT_SCROLL, self.OnSpin)
        self.spin = wx.TextCtrl(self, wx.ID_ANY,
                                self.spinstr(self.order.Value))
       
        self.tilt = wx.Slider(self, wx.ID_ANY, 23, 0, 90, style = wx.SL_HORIZONTAL)
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
        self.showinsol = wx.CheckBox(self, wx.ID_ANY, u'Show insolation')
        self.sizer.Add(self.showinsol, 0, flag = wx.EXPAND)

        self.sizer.Add(self.display, 1, flag = wx.EXPAND)

        self.rotate = wx.Slider(self, wx.ID_ANY, 0, -18, 18, style = wx.SL_HORIZONTAL)
        self.sizer.Add(self.rotate, 0, flag = wx.EXPAND)
       
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
 
    def Kill(self, event):
        self.display.Kill(event)
        self.Destroy()
 
    def OnSize(self, event):
        self.Layout()
 
    def Update(self, event):
        pass
 
    def OnScroll(self, event):
        self.radius.Value = self.radstr(self.slider.Value)

    def OnTilt(self, event):
        self.angle.Value = self.tiltstr(self.tilt.Value)

    def OnSpin(self, event):
        self.spin.Value = self.spinstr(self.order.Value)
 
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
