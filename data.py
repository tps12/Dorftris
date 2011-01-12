from random import randint

class Thing(object):
    def __init__(self, kind):
        self.kind = kind

class Creature(Thing):
    def __init__(self, kind):
        Thing.__init__(self, kind)
        self.location = None
        self.rest = randint(0,20)

    def step(self):
        if self.rest > 0:
            self.rest -= 1
        else:
            if self.location is not None:
                if randint(0,1):
                    self.location = (self.location[0],
                                     self.location[1] + randint(-1,1))
                else:
                    self.location = (self.location[0] + randint(-1,1),
                                     self.location[1])
            self.rest = 20
