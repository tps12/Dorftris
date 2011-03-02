from math import sqrt

from pygame import Rect
from pygame.mixer import *

from sound import Chop, Dig, Fall, Fight, Mine, Step

init()

class PlayfieldListener(object):
    sound = {
        Chop : Sound('chop.wav'),
        Dig : Sound('dirt.wav'),
        Fall : Sound('land.wav'),
        Fight : Sound('hurt.wav'),
        Mine : Sound('stone.wav'),
        Step : Sound('step.wav')
        }
        
    def __init__(self, playfield):
        self._playfield = playfield
        self._channels = [Channel(i) for i in range(8)]
        for i in range(len(self._channels)):
            self._channels[i].set_volume(1.0/(2**i))

    def _channelfromdistance(self, location):
        screen = Rect(self._playfield.offset, self._playfield.dimensions)
        if screen.collidepoint(location[0:2]):
            dist = 0
        else:
            if screen.left <= location[0] < screen.right:
                if location[1] < screen.top:
                    dist = screen.top - location[1]
                else:
                    dist = location[1] - screen.bottom
            elif screen.top <= location[1] < screen.bottom:
                if location[0] < screen.left:
                    dist = screen.left - location[0]
                else:
                    dist = location[0] - screen.left
            else:
                dist = min([sqrt(sum([(location[i]-p[i])**2 for i in range(2)]))
                            for p in (screen.topleft, screen.bottomleft,
                                      screen.topright, screen.bottomright)])
        dist /= 10
        dist += abs(location[2]-self._playfield.level)

        return self._channels[min(len(self._channels)-1, int(dist))]
        
    def play(self, sound, origin):
        if not sound:
            return
        
        c = self._channelfromdistance(origin)
        if not c.get_busy():
            c.play(self.sound[sound])
