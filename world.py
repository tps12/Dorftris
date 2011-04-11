from math import acos, asin, atan2, pi, sqrt

from pygame import display, draw, event, font, key, Rect, Surface
from pygame.locals import *

from etopo import Earth
from planet import Planet
from showplanet import Globe
from planetsettings import PlanetSettings

class RenderWorld(object):
    game = None
    dt = 0.01
    
    def __init__(self, zoom):
        self.zoom = zoom
        self.rotate = 0

        self._zoomrate = 0
        self._zooming = None

        self.left = PlanetSettings(self.zoom, Earth())
        self.right = Globe(self.zoom, self.left.planet, self._zoom)
        
        self.definetiles()

        self.makescreen(display.get_surface().get_size())

    def _zoom(self):
        self._zooming = 0

    def definetiles(self):
        self.uifont = self.zoom.font
        self.left.definetiles()
        self.right.definetiles()
                                                 
    def makescreen(self, size):
        self.screen = display.set_mode(size, HWSURFACE | RESIZABLE)

        self.titleheight = self.uifont.get_height()

        self.leftsize = min(size[0]/2,size[1]-2*self.titleheight)
        d = self.leftsize

        if self._zooming is not None:
            if self._zoomrate < 100:
                self._zoomrate += 5
            self._zooming += self._zoomrate
            
            self.leftsize -= self._zooming
            if self.leftsize <= 0:
                self.leftsize = d
                self.left = self.right
                self.right = self.left.detail()
                self._zoomrate = 0
                self._zooming = None

        lt = self.uifont.render(self.left.description, True, (255,255,255))
        self.screen.blit(lt, ((d - lt.get_width())/2,0))
        scale = self.left.scale
        if scale:
            ls = self.uifont.render(_(u'Scale: {scale}').format(scale=scale),
                                    True, (255,255,255))
            self.screen.blit(ls, (0,d+self.titleheight))

        if not self._zooming:
            rt = self.uifont.render(self.right.description, True, (255,255,255))
            self.screen.blit(rt, (d + (d - rt.get_width())/2, 0))

            scale = self.right.scale
            if scale:
                rs = self.uifont.render(_(u'Scale: {scale}').format(scale=scale),
                                        True, (255,255,255))
                self.screen.blit(rs, (d,d+self.titleheight))
        
        self.leftsurf = self.screen.subsurface(Rect((0,self.titleheight),
                                                    2*(d,)))
        self.rightsurf = self.screen.subsurface(Rect((self.leftsize,
                                                      self.titleheight),
                                                     2*(d,)))

        

    def step(self):
        done = False
        
        for e in event.get():

            pos = e.pos if 'pos' in e.dict else None
            if pos:
                e.dict['pos'] = pos[0], pos[1] - self.titleheight
            if self.left.handle(e):
                continue

            if pos:
                e.dict['pos'] = pos[0] - self.leftsize, pos[1] - self.titleheight
            if self.right.handle(e):
                continue

            if pos:
                e.dict['pos'] = pos
            
            if e.type == QUIT:
                done = True
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    done = True                   
            elif e.type == MOUSEBUTTONUP:
                if e.button == 4:
                    self.zoom.width += 2
                    self.zoom.height += 2
                    self.makescreen(self.screen.get_size())
                    self.definetiles()
                    
                elif e.button == 5:
                    self.zoom.width = max(self.zoom.width - 2, 2)
                    self.zoom.height = max(self.zoom.height - 2, 4)
                    self.makescreen(self.screen.get_size())
                    self.definetiles()
                    
            elif e.type == VIDEORESIZE:
                self.makescreen(e.size)
                self.definetiles()

        if self._zooming is not None:
            self.makescreen(self.screen.get_size())

        self.left.draw(self.leftsurf)
        self.right.draw(self.rightsurf)

        display.flip()

        return None if done else self
