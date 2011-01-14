from math import sqrt
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

class Beverage(Entity):
    def __init__(self):
        self.kind = 'beverage'

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
        self.reserved = False

class Container(Item):
    def __init__(self, kind, materials, location, capacity):
        Item.__init__(self, kind, materials, location)
        self.capacity = capacity
        self.contents = []

    def has(self, kind):
        return (any([isinstance(item, kind) for item in self.contents]) or
                any([item.has(kind) for item in self.contents
                     if isinstance(item, Container)]))

    def mass(self):
        return Thing.mass(self) + sum([item.mass() for item in self.contents])

class Barrel(Container):
    def __init__(self, location, substance):
        Container.__init__(self, 'barrel',
                           [Material(substance, 0.075)], location, 0.25)
        self.contents.append(Beverage())

class Task(object):
    def requirements(self):
        return []

    def work(self):
        return True

class GoToRandomGoal(Task):
    def __init__(self, subject, world):
        self.subject = subject
        self.world = world
        self.path = self.world.space.pathing.find_path(
            self.subject.location + (1,),
            tuple([randint(0, self.world.space.get_dimensions()[i]-1)
                   for i in range(2)]) + (1,))

    def work(self):
        if self.path == []:
            return True
        
        self.subject.location = self.path[0][0:2]
        self.path = self.path[1:]
        return self.path == []

class GoToGoal(Task):
    def __init__(self, subject, world, goal):
        self.subject = subject
        self.world = world
        self.path = self.world.space.pathing.find_path(
            self.subject.location + (1,),
            goal + (1,))

    def work(self):
        if self.path == []:
            return True
        
        self.subject.location = self.path[0][0:2]
        self.path = self.path[1:]
        return self.path == []

class MagicallyHydrate(Task):
    def __init__(self, subject):
        self.subject = subject

    def work(self):
        self.subject.hydration += 36000
        return True

class TaskImpossible(Exception):
    pass

class Acquire(Task):
    def __init__(self, subject, world, target):
        self.subject = subject
        self.world = world
        self.target = target
        self.nearest = None

    def requirements(self):
        if self.nearest is not None:
            return []
        
        try:
            self.nearest = sorted([item for item in self.world.items
                          if not item.reserved],
               key=lambda item: sqrt(
                   sum([(self.subject.location[i]-item.location[i])**2
                        for i in range(2)]))
                                  if item.location is not None else float('inf'))[0]
        except IndexError:
            raise TaskImpossible()

        if self.nearest.location is None:
            raise TaskImpossible()
        elif self.nearest.location == self.subject.location:
            return []
        else:
            self.nearest.reserved = True
            reqs = [GoToGoal(self.subject, self.world, self.nearest.location)]
            return reqs[0].requirements() + reqs

    def work(self):
        self.nearest.reserved = False
        self.nearest.location = None
        self.subject.inventory.append(self.nearest)
        return True

class Drink(Task):
    def __init__(self, subject, world):
        self.subject = subject
        self.world = world

    def requirements(self):
        if self.subject.has(Beverage):
            return []
        else:
            reqs = [Acquire(self.subject, self.world, Beverage)]
            return reqs[0].requirements() + reqs

    def work(self):
        self.subject.hydration += 36000
        return True

class Job(object):
    def __init__(self, tasks):
        self.tasks = tasks

    def work(self):
        if not len(self.tasks):
            return True

        self.tasks = self.tasks[0].requirements() + self.tasks
        self.tasks = self.tasks[1:] if self.tasks[0].work() else self.tasks
        return self.tasks == []

class GoToRandomPlace(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [GoToRandomGoal(subject, world)])

class Hydrate(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [Drink(subject,world)])

class Creature(Thing):
    def __init__(self, kind, location):
        Thing.__init__(self, kind, [Material(Meat, 0.075)])
        self.location = location
        self.inventory = []
        self.job = None
        self.hydration = randint(9000,36000)
        self.rest = randint(0,20)

    def has(self, kind):
        return (any([isinstance(item, kind) for item in self.inventory]) or
                any([item.has(kind) for item in self.inventory
                     if isinstance(item, Container)]))

    def step(self, world):
        self.hydration -= 1

        if self.hydration == 0:
            world.creatures.remove(self)
        
        if self.rest > 0:
            self.rest -= 1
        else:
            try:
                if self.job is None:
                    if self.hydration < 1000:
                        self.job = Hydrate(self, world)
                    else:
                        self.job = GoToRandomPlace(self, world)

                if self.job.work():
                    self.job = None
                    
            except TaskImpossible:
                pass
                
            self.rest = 20

class World(object):
    def __init__(self, space, items, creatures):
        self.space = space
        self.items = items
        self.creatures = creatures
