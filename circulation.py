import gettext
gettext.install('dorftris')

from cPickle import dump, load

from math import asin, acos, atan2, pi, exp, sqrt, sin, cos

import wx, pygame
from pygame.locals import *

from climate import ClimateSimulation
from climateclassificationframe import ClimateClassFrame
from climatedisplay import ClimateDisplay

from wxpygame import PygameDisplay

def radius(i):
    return i*1600

def rotation(i):
    return i*10

def spin(i):
    a = abs(i)
    s = i / a if i else 1
    return s * pow(sqrt(360), a / 5.0)

def season(i):
    return [-1,
            -0.5,
            0,
            0.5,
            1,
            0.5,
            0,
            -0.5][i]

class SimulationControls(wx.PyPanel):
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

    def __init__(self, parent, sim):
        wx.PyPanel.__init__(self, parent)
        self._sim = sim

        lines = wx.BoxSizer(wx.VERTICAL)

        self._radius = wx.TextCtrl(self, wx.ID_ANY)
        self._rate = wx.TextCtrl(self, wx.ID_ANY)
        self._tilt = wx.TextCtrl(self, wx.ID_ANY)
        self._season = wx.TextCtrl(self, wx.ID_ANY)

        for name, value, low, high, handler, display in [
            (u'Radius:', 4, 1, 80, self._onradius, self._radius),
            (u'Rotation rate:', 10, -15, 15, self._onrate, self._rate),
            (u'Axial tilt:', 23, 0, 90, self._ontilt, self._tilt),
            (u'Season:', 2, 0, 7, self._onseason, self._season)
            ]:
            controls = wx.BoxSizer(wx.HORIZONTAL)
            slider = wx.Slider(self, wx.ID_ANY,
                               value, low, high,
                               style=wx.SL_HORIZONTAL)
            self.Bind(wx.EVT_SCROLL, handler, slider)
            handler(wx.ScrollEvent(pos=slider.Value))

            controls.Add(wx.StaticText(self, wx.ID_ANY, name))
            controls.Add(slider, 1)
            controls.Add(display)

            lines.Add(controls, flag=wx.EXPAND)

        proc = wx.BoxSizer(wx.HORIZONTAL)

        classify = wx.Button(self, wx.ID_ANY, u'Classify...')
        self.Bind(wx.EVT_BUTTON, self._onclassify, classify)
        proc.Add(classify)

        lines.Add(proc)
                           
        self.SetAutoLayout(True)
        self.SetSizer(lines)
        self.Layout()

    def _onclassify(self, event):
        summary = self._sim.classify([season(i) for i in range(8)])
        ClimateClassFrame(None,
                          summary,
                          self._sim.sealevel).Show()

    def _onradius(self, event):
        self._sim.radius = radius(event.Position)
        self._radius.Value = self.radstr(event.Position)

    def _onrate(self, event):
        self._sim.spin = spin(event.Position)/360.
        self._rate.Value = self.spinstr(event.Position)

    def _ontilt(self, event):
        self._sim.tilt = event.Position
        self._tilt.Value = self.tiltstr(event.Position)

    def _onseason(self, event):
        self._sim.season = season(event.Position)
        self._season.Value = self.seasonstr(event.Position)

class DisplayControls(wx.PyPanel):
    def __init__(self, parent, display):
        wx.PyPanel.__init__(self, parent)
        self._display = display

        lines = wx.BoxSizer(wx.VERTICAL)

        rotate = wx.Slider(self, wx.ID_ANY, 0, -18, 18, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SCROLL, self._onrotate, rotate)
        self._onrotate(wx.ScrollEvent(pos=rotate.Value))
        lines.Add(rotate, flag=wx.EXPAND)

        modes = wx.BoxSizer(wx.HORIZONTAL)
        style = wx.RB_GROUP
        for name, mode in [(u'Terrain', ClimateDisplay.TERRAIN),
                           (u'Temperature', ClimateDisplay.TEMPERATURE),
                           (u'Moisture from sea', ClimateDisplay.SEABREEZE),
                           (u'Moisture from convection', ClimateDisplay.CONVECTION),
                           (u'Total precipitation', ClimateDisplay.PRECIPITATION),
                           (u'Insolation', ClimateDisplay.INSOLATION)]:
            button = wx.RadioButton(self, wx.ID_ANY, name, style=style)
            self.Bind(wx.EVT_RADIOBUTTON, self._modehandler(mode), button)
            modes.Add(button)
            if style:
                self._modehandler(mode)(None)
                style = 0
        lines.Add(modes, flag=wx.EXPAND)

        airflow = wx.CheckBox(self, wx.ID_ANY, u'Show circulation')
        self.Bind(wx.EVT_CHECKBOX, self._onairflow, airflow)
        event = wx.CommandEvent()
        event.Value = airflow.Value
        self._onairflow(event)
        lines.Add(airflow)
        
        self.SetAutoLayout(True)
        self.SetSizer(lines)
        self.Layout()

    def _modehandler(self, mode):
        def onmode(event):
            self._display.mode = mode
        return onmode

    def _onairflow(self, event):
        self._display.airflow = event.Checked()
        
    def _onrotate(self, event):
        self._display.rotate = rotation(-event.Position)

class Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, size = (1600, 1000))

        self.sim = ClimateSimulation()
        self.map = ClimateDisplay(self.sim)
        self.display = PygameDisplay(self, -1, self.map)
       
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)
       
        self.curframe = 0
       
        self.SetTitle(self.sim.planet.name)
              
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(SimulationControls(self, self.sim), flag=wx.EXPAND)

        self.sizer.Add(self.display, 1, flag = wx.EXPAND)

        self.sizer.Add(DisplayControls(self, self.map), flag=wx.EXPAND)
       
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
 
    def Kill(self, event):
        self.display.Kill(event)
        self.Destroy()
 
    def OnSize(self, event):
        self.Layout()
 
class App(wx.App):
    def __init__(self, redirect=True):
        wx.App.__init__(self, redirect)
        
    def OnInit(self):
        self.frame = Frame(parent = None)
        self.frame.Show()
        self.SetTopWindow(self.frame)
       
        return True
 
if __name__ == "__main__":
    app = App(False)
    app.MainLoop()
