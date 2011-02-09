from pygame import event, mouse

class ScrollButton(object):
    def __init__(self, glyphs, font, prefs, down):
        self._glyphs = glyphs
        self._prefs = prefs
        self._down = down
        self._pressed = None
        self._last = 0

        self.scale(font)

    def scale(self, font):
        self._font = font
        self._images = [self._font.render(self._glyphs[i], True, (255,255,255))
                        for i in range(2)]
        self._pressed = False

    @property
    def height(self):
        return self._images[0].get_height()

    def poll(self, pos):
        if self._images[0].get_rect().collidepoint(pos):
            event.get()            
            pressed = mouse.get_pressed()[0]
        else:
            pressed = False
            
        changed = False
        if self._pressed != pressed:
            self._pressed = pressed
            changed = True
        
        if self._pressed:
            self._down()

        return changed

    def draw(self):
        return self._images[1 if self._pressed else 0]
