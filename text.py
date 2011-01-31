from pygame import Surface
from pygame.locals import *

class TextRenderer(object):
    def __init__(self, font, width):
        self._font = font
        self._width = width

    def render(self, text, color):
        words = text.split()
        lines = []
        h = 0
        i = 0
        j = 1
        while i < len(words):
            found = False
            if j == len(words):
                found = True
            elif self._font.size(' '.join(words[i:j]))[0] >= self._width:
                j = max(1, j-1)
                found = True

            if found:
                line = self._font.render(' '.join(words[i:j]), True, color)
                lines.append(line)
                h += line.get_height()
                i = j
            else:
                j += 1
        image = Surface((self._width, h), flags=SRCALPHA)
        h = 0
        for line in lines:
            image.blit(line, (0, h))
            h += line.get_height()
        return image
