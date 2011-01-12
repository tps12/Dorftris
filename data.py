from random import randint

class Substance(object):
    density = None

class Wood(Substance):
    pass

class Oak(Wood):
    density = 750.0

class Meat(Substance):
    density = 1000.0

class Material(object):
    def __init__(self, substance, amount):
        self.substance = substance
        self.amount = amount

    def mass(self):
        return self.substance.density * self.amount

class Entity(object):
    def __init__(self, kind):
        self.kind = kind

class Thing(Entity):
    def __init__(self, kind, materials):
        Entity.__init__(self, kind)
        self.materials = materials

    def mass(self):
        return sum([m.mass() for m in self.materials])

class Item(Thing):
    def __init__(self, kind, materials):
        Thing.__init__(self, kind, materials)

class Container(Item):
    def __init__(self, kind, materials, capacity):
        Item.__init__(self, kind, materials)
        self.capacity = capacity
        self.contents = []

class Barrel(Container):
    def __init__(self, substance):
        Container.__init__(self, 'barrel', [Material(substance, 0.075)], 0.25)

class Task(object):
    def __init__(self, subject):
        self.subject = subject

class MoveTo(Task):
    def __init__(self, subject, target):
        Task.__init__(self, subject)
        self.target = target

    def requirement(self):
        pass

    def perform(self):
        pass

class Acquire(Task):
    def __init__(self, subject, target):
        Task.__init__(self, subject)
        self.target = target

    def requirement(self):
        for item in self.subject.inventory:
            if item is self.target:
                return None
        else:
            return Acquire(self.subject, self.target)

    def perform(self):
        self.subject.

class Consume(Task):
    def __init__(self, subject, target):
        Task.__init__(self, subject)
        self.target = target

    def requirement(self):
        for item in self.subject.inventory:
            if item is self.target:
                return None
        else:
            return Acquire(self.subject, self.target)

    def perform(self):
        pass

class Job(object):
    def __init__(self, tasks):
        self.tasks = tasks

    def work(self):

class Drink(Job):
    def __init__(self):
        Job.__init__(self, [Consume(Beverage)])

class Creature(Thing):
    def __init__(self, kind):
        Thing.__init__(self, kind, [Material(Meat, 0.075)])
        self.location = None
        self.inventory = []
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
