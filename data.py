from collections import deque
from random import choice, randint

class Substance(object):
    color = None
    density = None

class AEther(Substance):
    color = (255,255,255)
    density = 0

class Wood(Substance):
    pass

class Oak(Wood):
    color = (139,69,19)
    density = 750.0

class Meat(Substance):
    color = (63,0,0)
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
        self.color = self.materials[0].substance.color
        self.location = location
        self.reserved = False

class OutOfSpace(Exception):
    pass

class Storage(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.contents = []

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
        if (self.space() > item.volume()):
            self.contents.append(item)
        else:
            raise OutOfSpace()

    def space(self):
        return self.capacity - sum([item.volume() for item in self.contents])

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

class WrongItemType(Exception):
    pass

class Stockpile(Storage, Entity):
    color = (255,255,255)
    
    def __init__(self, region, types):
        Storage.__init__(self, 0)
        Entity.__init__(self, 'stockpile')
        self.components = []
        self.types = types
        self.changed = False
        for location in region:
            self.annex(location)

    def add(self, item):
        if (any([isinstance(item, t) for t in self.types]) or
            (isinstance(item, Container) and
             any([item.has(t) for t in self.types]))):
            Storage.add(self, item)
            self.changed = True
        else:
            raise WrongItemType()

    def remove(self, item):
        success = Storage.remove(self, item)
        self.changed = success
        return success
        
    def annex(self, location):
        self.capacity += 1
        self.components.append(StockpileComponent(self, location))
        self.changed = True

class Container(Item, Storage):
    def __init__(self, kind, materials, location, capacity):
        Item.__init__(self, kind, materials, location)
        Storage.__init__(self, capacity)

    def volume(self):
        return Thing.volume(self) + self.capacity

    def mass(self):
        return Thing.mass(self) + sum([item.mass() for item in self.contents])

class StockpileComponent(Container):
    def __init__(self, stockpile, location):
        Container.__init__(self, stockpile.kind,
                           [Material(AEther, 0)], location, 1.0)
        self.stockpile = stockpile

    def description(self):
        return Storage.description(self.stockpile)

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

class GoToRandomAdjacency(Task):
    def __init__(self, subject, world):
        self.subject = subject
        self.world = world

    def work(self):
        adjacent = self.world.space.pathing.open_adjacent(
            self.subject.location)
        if len(adjacent) > 0:
            self.world.space[self.subject.location].creatures.remove(self.subject)
            self.subject.location = choice([a for a in adjacent])
            self.world.space[self.subject.location].creatures.append(self.subject)
        return True

class GoToGoal(Task):
    steps = 256
    
    def __init__(self, subject, world, goal):
        self.subject = subject
        self.world = world
        self.goal = goal

        self.p1 = self.world.space.pathing.path_op(
                      self.subject.location, goal)
        self.p2 = self.world.space.pathing.path_op(
                      goal, self.subject.location)
        self.path = None

    def work(self):
        if self.path == []:
            return True

        if self.path is None:
            if not self.p1.done and not self.p2.done:
                self.p1.iterate(self.steps)
                self.p2.iterate(self.steps)
                return False

            if self.p1.done:
                self.path = self.p1.path
            elif self.p2.path is not None:
                self.path = self.p2.path[::-1][1:] + [self.goal]

            if self.path is None:
                raise TaskImpossible()
        
        self.world.space[self.subject.location].creatures.remove(self.subject)
        self.subject.location = self.path[0]
        self.world.space[self.subject.location].creatures.append(self.subject)
        self.path = self.path[1:]
        return self.path == []

class TaskImpossible(Exception):
    pass

class Follow(Task):
    def __init__(self, subject, world, target):
        self.subject = subject
        self.world = world
        self.target = target
        self.path = []

    def work(self):
        if self.target.remove:
            return True
        
        if self.path == []:
            if self.subject.location == self.target.location:
                return True
            else:
                self.path = self.world.space.pathing.find_path(
                    self.subject.location,
                    self.target.location)

        if self.path[-1] != self.target.location:
            self.path[-1:] = self.world.space.pathing.find_path(
                self.path[-1], self.target.location)

        self.world.space[self.subject.location].creatures.remove(self.subject)
        self.subject.location = self.path[0]
        self.world.space[self.subject.location].creatures.append(self.subject)
        
        self.path = self.path[1:]
        return self.path == []

class Attack(Task):
    def __init__(self, subject, world, target):
        self.subject = subject
        self.world = world
        self.target = target
        self.nearest = None

    def requirements(self):
        if (self.nearest is not None and
            self.nearest.location == self.subject.location and
            self.nearest.health > 0):
            return []

        try:
            self.nearest = sorted([c for c in self.world.creatures
                                   if isinstance(c, self.target)],
                                  key = lambda c:
                                  self.world.space.pathing.distance_xy(
                                      self.subject.location,
                                      c.location[0:2]))[0]
        
        except IndexError:
            raise TaskImpossible()

        if self.world.space.pathing.distance_xy(
            self.subject.location[0:2],
            self.nearest.location[0:2]) > self.subject.eyesight:
            raise TaskImpossible()

        if self.nearest.location == self.subject.location:
            return []
        else:
            reqs = [Follow(self.subject, self.world, self.nearest)]
            return reqs[0].requirements() + reqs

    def work(self):
        self.nearest.health -= 1
        return self.nearest.health <= 0

class Acquire(Task):
    def __init__(self, subject, world, test, capacity):
        self.subject = subject
        self.world = world
        self.test = test
        self.capacity = capacity
        self.nearest = None
        self.stockpile = None

    def requirements(self):
        if self.stockpile is not None or self.nearest is not None:
            return []

        self.searchstockpiles()

        if self.nearest is None:
            for target in self.targets:
                try:
                    self.nearest = sorted([item for item in self.items()
                                           if self.test(item)],
                                          key = lambda item:
                                          self.world.space.pathing.distance_xy(
                                              self.subject.location[0:2],
                                              item.location[0:2]))[0]
                    break
                
                except IndexError:
                    continue
            else:
                raise TaskImpossible()

        location = (self.stockpile.components[0].location
                    if self.stockpile is not None
                    else self.nearest.location)

        if location is None:
            raise TaskImpossible()
        elif location == self.subject.location:
            return []
        else:
            self.nearest.reserved = True
            reqs = [GoToGoal(self.subject, self.world, location)]
            return reqs[0].requirements() + reqs

    def searchstockpiles(self):
        for stockpile in self.world.stockpiles:
            for target in self.targets:
                self.nearest = stockpile.find(self.test)
                if self.nearest is not None:
                    self.stockpile = stockpile
                    return

    def work(self):
        self.world.space[self.nearest.location].items.remove(self.nearest)
        self.nearest.location = None
        if self.stockpile is not None:
            self.stockpile.remove(self.nearest)
        self.subject.inventory.add(self.nearest)
        return True

class AcquireKind(Acquire):
    def __init__(self, subject, world, targets, capacity):
        Acquire.__init__(self, subject, world, self.istarget, capacity)
        self.targets = targets

    def items(self):
        return [item for item in self.world.items
                if item.location is not None and
                not item.reserved]

    def istarget(self, item):
        return any([(target.fluid and
                     isinstance(item, Storage) and item.has(target)) or
                    isinstance(item, target) for target in self.targets])

class AcquireNonStockpiled(AcquireKind):
    def __init__(self, subject, world, targets, capacity):
        AcquireKind.__init__(self, subject, world, targets, capacity)
        self.targets = targets

    def searchstockpiles(self):
        return
    
class Drink(Task):
    def __init__(self, subject, world):
        self.subject = subject
        self.world = world

    def requirements(self):
        if self.subject.inventory.has(Beverage):
            return []
        else:
            reqs = [AcquireKind(self.subject, self.world,
                            [Beverage], self.subject.inventory.space())]
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
        
        self.subject.hydration += 3600 * (sip / self.subject.thirst)
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
        self.world.space[item.location].items.append(item)
        item.reserved = False

        return False

class StoreItem(Task):
    def __init__(self, subject, world, stockpile):
        self.subject = subject
        self.world = world
        self.stockpile = stockpile

    def requirements(self):
        for t in self.stockpile.types:
            if self.subject.inventory.has(t):
                reqs = []
                break
        else:
            reqs = [AcquireNonStockpiled(self.subject, self.world,
                            self.stockpile.types, self.stockpile.space())]

        if self.subject.location != self.stockpile.components[0].location:
            reqs = reqs + [GoToGoal(self.subject, self.world,
                                    self.stockpile.components[0].location)]

        return reqs[0].requirements() + reqs if len(reqs) else reqs

    def work(self):
        item = self.subject.inventory.find(lambda item: True)

        self.subject.inventory.remove(item)

        if self.stockpile.space() >= item.volume():
            self.stockpile.add(item)
        else:
            item.location = self.subject.location
            self.world.space[item.location].items.append(item)

        item.reserved = False
                
        return True

class FillStockpile(Task):
    def __init__(self, subject, world):
        self.subject = subject
        self.world = world

    def requirements(self):
        stockpile = next((stockpile for stockpile in self.world.stockpiles
                          if stockpile.space()), None)
        if stockpile is None:
            return []

        self.world.stockpiles.remove(stockpile)
        self.world.stockpiles.append(stockpile)
        
        reqs = [StoreItem(self.subject, self.world, stockpile)]
        return reqs[0].requirements() + reqs

    def work(self):
        return True

class AttemptDigDesignation(Task):
    def __init__(self, subject, world):
        self.subject = subject
        self.world = world
        self.designation = self.world.designations.popleft()

    def requirements(self):
        x, y, z = self.designation
        for loc in [(x,y,z+1)] + [(x,y,z)
                                  for x,y in
                                  self.world.space.pathing.adjacent_xy((x,y))]:
            if self.subject.location == loc:
                return []
            elif self.world.space[loc].is_passable():
                reqs = [GoToGoal(self.subject, self.world, loc)]
                return reqs[0].requirements() + reqs

        self.world.designations.append(self.designation)

        raise TaskImpossible()

    def work(self):
        self.world.space.remove(self.designation)
        if self.subject.location[2] == self.designation[2]+1:
            self.world.space[self.subject.location].creatures.remove(self.subject)
            self.subject.location = self.designation
            self.world.space[self.subject.location].creatures.append(self.subject)
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

class Meander(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [GoToRandomAdjacency(subject, world)])

class Hydrate(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [Drink(subject, world)])

class DropExtraItems(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [DropItems(subject, world,
                                      lambda item: not item.reserved)])

class StoreInStockpile(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [FillStockpile(subject, world)])

class SeekAndDestroy(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [Attack(subject, world, Dwarf)])

class DigDesignation(Job):
    def __init__(self, subject, world):
        Job.__init__(self, [AttemptDigDesignation(subject, world)])

class Corpse(Item):
    def __init__(self, creature):
        Item.__init__(self, 'corpse', creature.materials, creature.location)
        self.origins = creature

    def description(self):
        return _('corpse of {0}').format(self.origins.description())

class JobOption(object):
    def __init__(self, definition, condition, priority):
        self.definition = definition
        self.condition = condition
        self.priority = priority

    @staticmethod
    def prioritykey(option):
        return option.priority

class Creature(Thing):
    jobs = sorted([
                   JobOption(Hydrate, lambda c, w: c.hydration < 1000, 0),
                   JobOption(DropExtraItems,
                             lambda c, w: c.inventory.find(lambda i:
                                                        isinstance(i, Item) and
                                                           not i.reserved), 99),
                   JobOption(Meander, lambda c, w: True, 100)
                   ],
                  key = JobOption.prioritykey)
    
    def __init__(self, kind, materials, color, location):
        Thing.__init__(self, kind, materials)
        self.color = color
        self.location = location
        self.inventory = Storage(1.0)
        self.job = None
        self.hydration = randint(900, 3600)
        self.rest = randint(0, self.speed)
        self.remove = False

    def die(self, world):
        self.remove = True
        world.items.append(Corpse(self))

    def newjob(self, world):
        for job in sorted([option for option in self.jobs
                           if option.condition(self, world)],
                          key = lambda option: option.priority):
            try:
                self.job = job.definition(self, world)
                if self.job.work():
                    self.job = None
                return
            except TaskImpossible:
                continue

    def step(self, world):
        self.hydration = max(self.hydration - 1, 0)

        if self.hydration == 0:
            self.health -= 1

        if self.health <= 0:
            self.die(world)
       
        try:                
            if self.job is None:
                self.newjob(world)
            elif self.job.work():
                self.job = None
                
        except TaskImpossible:
            self.job = None
            
        self.rest = self.speed

class Dwarf(Creature):
    eyesight = 10
    health = 10
    jobs = sorted(Creature.jobs +
                  [JobOption(DigDesignation,
                             lambda c, w: len(w.designations) > 0,
                             10),
                   JobOption(StoreInStockpile,
                             lambda c, w: len(w.stockpiles) > 0,
                             90)],
                  key = JobOption.prioritykey)
    speed = 3
    thirst = 0.03
    
    def __init__(self, location):
        r = randint(80,255)
        Creature.__init__(self, 'dwarf', [Material(Meat, 0.075)],
                          (r, r-40, r-80), location)
        
class Goblin(Creature):
    eyesight = 16
    health = 0
    jobs = sorted(Creature.jobs +
                  [JobOption(SeekAndDestroy,
                             lambda c, w: any([isinstance(c, Dwarf)
                                               for c in w.creatures]),
                             10)],
                  key = JobOption.prioritykey)
    speed = 2
    thirst = 0.01
    
    def __init__(self, location):
        Creature.__init__(self, 'goblin', [Material(Meat, 0.05)],
                          (32, 64+randint(0,127),64+randint(0,127)), location)

class Tortoise(Creature):
    eyesight = 4
    health = 10
    speed = 20
    thirst = 0.1
    
    def __init__(self, location):
        d = randint(-20,10)
        Creature.__init__(self, 'tortoise', [Material(Meat, 0.3)],
                          (188+d,168+d,138+d), location)

class SmallSpider(Creature):
    eyesight = 1
    health = 10
    speed = 1
    thirst = 0.0001
    
    def __init__(self, location):
        Creature.__init__(self, 'spider-small', [Material(Meat, 0.0001)],
                          (95, randint(0,40), 0), location)

class World(object):
    def __init__(self, space, items):
        self.space = space
        self.items = items
        self.creatures = []
        self.designations = deque()
        self.stockpiles = []

    def addstockpile(self, stockpile):
        self.stockpiles.append(stockpile)
