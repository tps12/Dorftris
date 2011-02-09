from pygame import Rect, Surface
from pygame.locals import *

class TreeOptions(object):
    empty = (255,255,255), u'\u2610'
    yes = (0,255,0), u'\u2611'
    no = (255,0,0), u'\u2612'

    collapsed = (255,255,255), u'\u25b6'
    expanded = (255,255,255), u'\u25e2'
    
    def __init__(self, options, font, prefs, changed):
        self._options = self._initoptions(options)
        self._prefs = prefs
        self._changed = changed

        self.scale(font)

    @classmethod
    def _initoptions(cls, branch):
        result = []
        for key, name, value in branch:
            if hasattr(value, '__iter__'):
                child = cls._initoptions(value)
            else:
                child = value
            result.append([key, name, False, child])
        return result

    def scale(self, font):
        self._font = font
        self._emp, self._y, self._n, self._col, self._exp = [
            self._font.render(s[1], True, s[0])
            for s in self.empty, self.yes, self.no,
            self.collapsed, self.expanded]

    def selected(self, branch = None):
        branch = branch or self._options
        
        result = []
        for key, name, expanded, value in branch:
            if hasattr(value, '__iter__'):
                result.extend(self.selected(value))
            elif value:
                result.append(key)
        return result

    def _setvalue(self, branch, key, value):
        if value is None:
            return
        
        for i in range(len(branch)):
            if branch[i][0] == key:
                if hasattr(branch[i][3], '__iter__'):
                    for child in branch[i][3]:
                        self._setvalue(branch[i][3], child[0], value)
                else:
                    branch[i][3] = value
                break
        else:
            raise ValueError

    def _boxhandler(self, branch, key, value):
        return lambda: self._setvalue(branch, key, value)

    def _setexpand(self, branch, key, expand):
        for i in range(len(branch)):
            if branch[i][0] == key:
                if hasattr(branch[i][3], '__iter__'):
                    branch[i][2] = expand
                else:
                    raise ValueError
                break
        else:
            raise ValueError

    def _arrowhandler(self, branch, key, expand):
        return lambda: self._setexpand(branch, key, expand)

    def _drawboxes(self, branch, key, a, b, aval, bval):
        boxes = Surface((a.get_width() + b.get_width(), self._emp.get_height()),
                        flags=SRCALPHA)
        locs = (0,0), (a.get_width(), 0)
        boxes.blit(a, locs[0])
        boxes.blit(b, locs[1])
        return [(Rect(locs[i], self._emp.get_size()), 1,
                 self._boxhandler(branch, key, (aval,bval)[i]))
                for i in range(len(locs))], boxes

    def _drawbranch(self, indent, branch):
        result = []
        truths = []
        boxoffset = 0
        for key, name, expanded, value in branch:
            space = self._font.render(' '*4*indent, False, (0,0,0))
            title = self._font.render(name, True, (255,255,255))

            if hasattr(value, '__iter__'):
                arrow = self._exp if expanded else self._col
                lines, suboffset, allsame = self._drawbranch(indent+1, value)
                selected = allsame
                boxoffset = max(boxoffset, suboffset)
            else:
                arrow = None
                lines = []
                selected = value

            width = (space.get_width() +
                     (arrow.get_width() if arrow else 0) +
                     title.get_width())
            height = title.get_height()
            image = Surface((width, height), flags=SRCALPHA)
            image.blit(space, (0,0))
            if arrow:
                loc = space.get_width(), 0
                image.blit(arrow, loc)
                buttons = [(Rect(loc, arrow.get_size()), 0,
                            self._arrowhandler(branch, key, not expanded))]
            else:
                buttons = []
            image.blit(title, (image.get_width()-title.get_width(), 0))

            if selected:
                boxes = self._y, self._emp
                actions = None, False
            elif selected == False:
                boxes = self._emp, self._n
                actions = True, None
            else:
                boxes = self._emp, self._emp
                actions = True, False

            boxbuttons, boximage = self._drawboxes(branch, key,
                                                   *(boxes + actions))
            buttons.extend(boxbuttons)

            result.append((image, buttons, boximage))
            if expanded:
                result.extend(lines)
            
            truths.append(selected)
            boxoffset = max(boxoffset, image.get_width())

        allsame = (True if all(truths) else
                   False if all([t == False for t in truths]) else
                   None)
        return result, boxoffset, allsame

    def handle(self, e):
        if e.type == MOUSEBUTTONDOWN:
            for b in self._buttons:
                if b[0].collidepoint(e.pos):
                    b[1]()
                    return True
        return False

    def draw(self):
        entries, boxoffset, allsame = self._drawbranch(0, self._options)

        self._buttons = []

        dh = entries[0][0].get_height()
        surface = Surface((boxoffset + entries[0][2].get_width(), len(entries)*dh),
                          flags=SRCALPHA)
        h = 0
        for line, buttons, boxes in entries:
            surface.blit(line, (0, h))
            surface.blit(boxes, (boxoffset, h))

            self._buttons.extend([(b[0].move(b[1] * boxoffset, h), b[2])
                                  for b in buttons])
            
            h += dh

        return surface
