import wx

from climatesummary import ClimateSummaryDisplay
from wxpygame import PygameDisplay

class ClimateSummaryFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, size = (1600, 1000))

        self.display = PygameDisplay(self, -1, ClimateSummaryDisplay(None))
       
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)
       
        self.SetTitle(u'Summary')
              
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.display, 1, flag = wx.EXPAND)
       
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
 
    def Kill(self, event):
        self.display.Kill(event)
        self.Destroy()
 
    def OnSize(self, event):
        self.Layout()
