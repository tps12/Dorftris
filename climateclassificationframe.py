import wx

from climateclassification import ClimateClassDisplay
from wxpygame import PygameDisplay

def rotation(i):
    return i*10

class DisplayControls(wx.PyPanel):
    def __init__(self, parent, display):
        wx.PyPanel.__init__(self, parent)
        self._display = display

        lines = wx.BoxSizer(wx.VERTICAL)

        rotate = wx.Slider(self, wx.ID_ANY, 0, -18, 18, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SCROLL, self._onrotate, rotate)
        self._onrotate(wx.ScrollEvent(pos=rotate.Value))
        lines.Add(rotate, flag=wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(lines)
        self.Layout()

    def _modehandler(self, mode):
        def onmode(event):
            self._display.mode = mode
        return onmode

    def _onrotate(self, event):
        self._display.rotate = rotation(-event.Position)

class ClimateClassFrame(wx.Frame):
    def __init__(self, parent, summary):
        wx.Frame.__init__(self, parent, -1, size = (1600, 1000))

        summarydisplay = ClimateClassDisplay(summary)
        self.display = PygameDisplay(self, -1, summarydisplay)
       
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)
       
        self.SetTitle(u'Classification')
              
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.display, 1, flag = wx.EXPAND)

        self.sizer.Add(DisplayControls(self, summarydisplay), flag=wx.EXPAND)
       
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
 
    def Kill(self, event):
        self.display.Kill(event)
        self.Destroy()
 
    def OnSize(self, event):
        self.Layout()
