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

class Water(Substance):
    density = 1000.0

class Entity(object):
    def __init__(self, kind):
        self.kind = kind

    def description(self):
        return self.kind

class Thing(Entity):
    fluid = False
    
    def __init__(self, kind, materials):
        Entity.__init__(self, kind)
        self.materials = materials

    def volume(self):
        return sum([m.amount for m in self.materials])

    def mass(self):
        return sum([m.mass() for m in self.materials])

class Beverage(Thing):
    fluid = True
    
    def __init__(self, amount):
        Thing.__init__(self, 'beverage', [Material(Water, amount)])

    def description(self):
        return _('{0} ({1} L)').format(self.kind,
                                          self.materials[0].amount * 1000)

class Item(Thing):
    def __init__(self, kind, materials, location):
        Thing.__init__(self, kind, materials)
        self.location = location
        self.reserved = False

class OutOfSpace(Exception):
    pass

class Storage(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.contents = []

    def find(self, test):
        for item in self.contents:
            if test(item):
                return item
            elif isinstance(item, Storage):
                value = item.find(test)
                if value is not None:
                    return value
        return None

    def add(self, item):
        if (self.capacity - sum([item.volume() for item in self.contents]) >
            item.volume()):
            self.contents.append(item)
        else:
            raise OutOfSpace()

    def remove(self, item):
        if item in self.contents:
            self.contents.remove(item)
            return True
        else:
            for container in [item for item in self.contents
                              if isinstance(item, Storage)]:
                if container.remove(item):
                    return True
        return False

    def has(self, kind):
        return self.find(lambda item: isinstance(item, kind)) is not None

class Container(Item, Storage):
    def __init__(self, kind, materials, location, capacity):
        Item.__init__(self, kind, materials, location)
        Storage.__init__(self, capacity)

    def description(self):
        n = len(self.contents)
        if n == 0:
            return _('empty {0}').format(self.kind)
        elif n == 1:
            return _('{0} of {1}').format(self.kind,
                                          self.contents[0].description())
        else:
            return _('{0} containing {1}').format(self.kind,
                                                  ', '.join([item.description()
                                                             for item
                                                             in self.contents]))

    def volume(self):
        return Thing.volume(self) + self.capacity

    def mass(self):
        return Thing.mass(self) + sum([item.mass() for item in self.contents])

class Barrel(Container):
    def __init__(self, location, substance):
        Container.__init__(self, 'barrel',
                           [Material(substance, 0.075)], location, 0.25)
        self.contents.append(Beverage(self.capacity))

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

        test = None
        if self.target.fluid:
            test = lambda item: (isinstance(item, Storage) and
                                 len(item.contents) == 1 and
                                 isinstance(item.contents[0], self.target))
        else:
            test = lambda item: isinstance(item, self.target)

        try:
            self.nearest = sorted([item for item in self.world.items
                                   if item.location is not None and
                                   not item.reserved and
                                   test(item)],
                                  key = lambda item: sqrt(
                                      sum([(self.subject.location[i]-item.location[i])**2
                                           for i in range(2)])))[0]
        
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
        self.nearest.location = None
        self.subject.inventory.add(self.nearest)
        return True

class Drink(Task):
    def __init__(self, subject, world):
        self.subject = subject
        self.world = world

    def requirements(self):
        if self.subject.inventory.has(Beverage):
            return []
        else:
            reqs = [Acquire(self.subject, self.world, Beverage)]
            return reqs[0].requirements() + reqs

    def work(self):
        vessel = self.subject.inventory.find(lambda item:
                                             isinstance(item, Storage) and
                                             item.has(Beverage))
        
        bev = vessel.find(lambda item: isinstance(item, Beverage))
        sip = min(self.subject.thirst, bev.materials[0].amount)

        if sip == bev.materials[0].amount:
            vessel.remove(bev)
        else:
            bev.materials[0].amount -= sip
        
        self.subject.hydration += 36000 * (sip / self.subject.thirst)
        vessel.reserved = False
        return True

class DropItems(Task):
    def __init__(self, subject, world, test):
        self.subject = subject
        self.world = world
        self.test = test

    def work(self):
        item = self.subject.inventory.find(self.test)
        if item is None:
            return True

        self.subject.inventory.remove(item)
        
        item.location = self.subject.location
        item.reserved = False

        return False

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
        Job.__init__(self, [Drink(subject, world)])

class DropExtraItems(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [DropItems(subject, world,
                                      lambda item: not item.reserved)])

class Corpse(Item):
    def __init__(self, creature):
        Item.__init__(self, 'corpse', creature.materials, creature.location)
        self.origins = creature

    def description(self):
        return _('corpse of {0}').format(self.origins.description())

class Creature(Thing):
    color = (128,128,128)
    
    def __init__(self, kind, materials, location):
        Thing.__init__(self, kind, materials)
        self.location = location
        self.inventory = Storage(1.0)
        self.job = None
        self.hydration = randint(9000, 36000)
        self.rest = randint(0, self.speed)

    def die(self, world):
        world.creatures.remove(self)
        world.items.append(Corpse(self))

    def step(self, world):
        self.hydration -= 1

        if self.hydration == 0:
            self.die(world)
       
        if self.rest > 0:
            self.rest -= 1
        else:
            try:
                if self.job is None:
                    if self.hydration < 1000:
                        self.job = Hydrate(self, world)
                    elif self.inventory.find(lambda item: not item.reserved):
                        self.job = DropExtraItems(self, world)
                    else:
                        self.job = GoToRandomPlace(self, world)

                if self.job.work():
                    self.job = None
                    
            except TaskImpossible:
                pass
                
            self.rest = self.speed

class Dwarf(Creature):
    speed = 11
    thirst = 0.03
    
    def __init__(self, location):
        Creature.__init__(self, 'dwarf', [Material(Meat, 0.075)], location)
        
class Goblin(Creature):
    speed = 9
    thirst = 0.01
    
    def __init__(self, location):
        Creature.__init__(self, 'goblin', [Material(Meat, 0.05)], location)

class Tortoise(Creature):
    speed = 100
    thirst = 0.1
    
    def __init__(self, location):
        Creature.__init__(self, 'tortoise', [Material(Meat, 0.3)], location)

class SmallSpider(Creature):
    speed = 5
    thirst = 0.0001
    
    def __init__(self, location):
        Creature.__init__(self, 'spider-small', [Material(Meat, 0.0001)], location)

class World(object):
    def __init__(self, space, items, creatures):
        self.space = space
        self.items = items
        self.creatures = creatures
