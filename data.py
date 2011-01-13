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
    def __init__(self, kind, materials, location):
        Thing.__init__(self, kind, materials)
        self.location = location

class Container(Item):
    def __init__(self, kind, materials, location, capacity):
        Item.__init__(self, kind, materials, location)
        self.capacity = capacity
        self.contents = []

class Barrel(Container):
    def __init__(self, location, substance):
        Container.__init__(self, 'barrel',
                           [Material(substance, 0.075)], location, 0.25)

class Task(object):
    def perform(self, subject, world):
        return True

class GoToGoal(Task):
    def __init__(self, goal):
        self.goal = goal

    def perform(self, subject, world):
        pass

class Job(object):
    def __init__(self, tasks):
        self.tasks = tasks

    def work(self, subject, world):
        return True

class GoToRandomPlace(Job):
    def __init__(self):
        Job.__init__(self, [])

    def work(self, subject, world):
        if subject.path is not None:
            subject.location = subject.path[0][0:2]
            subject.path = subject.path[1:] if len(subject.path) > 1 else None
        else:
            subject.path = world.space.pathing.find_path(
                (subject.location[0], subject.location[1], 1),
                (randint(0, world.space.get_dimensions()[0]-1),
                 randint(0, world.space.get_dimensions()[1]-1),
                 1))
        return subject.path is None

class Creature(Thing):
    def __init__(self, kind, location):
        Thing.__init__(self, kind, [Material(Meat, 0.075)])
        self.location = location
        self.path = None
        self.inventory = []
        self.job = None
        self.rest = randint(0,20)

    def step(self, world):
        if self.rest > 0:
            self.rest -= 1
        else:
            if self.job is None:
                self.job = GoToRandomPlace()

            if self.job.work(self, world):
                self.job = None
                
            self.rest = 20

class World(object):
    def __init__(self, space, items, creatures):
        self.space = space
        self.items = items
        self.creatures = creatures
