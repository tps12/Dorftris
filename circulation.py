import gettext
gettext.install('dorftris')

from math import asin, acos, pi, sqrt, sin

import wx, pygame

from etopo import Earth

def radius(i):
    return i*1600    

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

    def Update(self, event):
        # Any update tasks would go here (moving sprites, advancing animation frames etc.)
        self.Redraw()

    def Redraw(self):
        if self.size_dirty:
            self.screen = pygame.Surface(self.size, 0, 32)
            self.size_dirty = False

        self.screen.fill((0,0,0))

        template = pygame.Surface((self.size[0]/100,self.size[1]/100), 0, 32)

        size = min(self.size[0]/100, self.size[1]/100)

        arrow = pygame.Surface(2*(int(size/sqrt(2)),), 0, 32)
        pygame.draw.polygon(arrow, (255,255,255),
                            [(0,arrow.get_height()-1),
                             (arrow.get_width()/2, 0),
                             (arrow.get_width()-1,arrow.get_height()-1)])
        
        c = cells(radius(self.parent.slider.Value))
 
        for y in range(100):
            lat = asin(float(y-50)/50) * 180/pi
            r = int(sqrt(2500 - (50-y)**2))

            n = abs(lat) / (90/c)
            n = int(n) & 1
            n = n if lat >= 0 else not n
            d = 180 * n
            
            for x in range(50-r, 50+r):
                block = template.copy()

                v = [float(x-r)/50, float(y-50)/50]

                if x >= 50:
                    lon = -acos(float((x-(50-r)-r))/r) * 180/pi
                else:
                    lon = 180 + acos(float(r-(x-(50-r)))/r) * 180/pi

                if lon > 180:
                    lon -= 360

                h = self.planet.sample(lat, lon)
                color = ((0,int(255 * (h/9000.0)),0) if h > 0
                         else (0,0,int(255 * (1 + h/11000.0))))

                block.fill(color)

                if self.parent.showair.Value:
                    s = lat * float(r-(x-(50-r)))/r

                    angle = pygame.transform.rotate(arrow, d + s)

                    block.blit(angle, ((block.get_width() - angle.get_width())/2,
                                       (block.get_height() - angle.get_height())/2))
                
                self.screen.blit(block, (x*block.get_width(),
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
       
        self.timer = wx.Timer(self)
       
        self.Bind(wx.EVT_SCROLL, self.OnScroll)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
       
        self.timer.Start((1000.0 / self.display.fps))
       
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer2.Add(self.slider, 1, flag = wx.EXPAND | wx.RIGHT, border = 5)
        self.sizer2.Add(self.radius, 0, flag = wx.EXPAND | wx.ALL, border = 5)
        self.showair = wx.CheckBox(self, wx.ID_ANY, u'Show circulation')
        self.sizer.Add(self.sizer2, 0, flag = wx.EXPAND)
        self.sizer.Add(self.showair, 0, flag = wx.EXPAND)
        self.sizer.Add(self.display, 1, flag = wx.EXPAND)
       
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
 
class App(wx.App):
    def OnInit(self):
        pygame.font.init()
        
        self.frame = Frame(parent = None)
        self.frame.Show()
        self.SetTopWindow(self.frame)
       
        return True
 
if __name__ == "__main__":
    app = App()
    app.MainLoop()
