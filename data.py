from codecs import open as openunicode
from collections import deque
from random import choice, gauss, randint, random
from re import search
from unicodedata import name as unicodename

from colordb import match as describecolor
from space import Earth, Empty
from substances import Meat, Water
from language import Generator

class Material(object):
    __slots__ = 'substance', 'amount'
    
    def __init__(self, substance, amount):
        self.substance = substance
        self.amount = amount

    def mass(self):
        return self.substance.density * self.amount

class Entity(object):
    __slots__ = 'kind',
    
    def __init__(self, kind):
        self.kind = kind

    def description(self):
        return self.kind

class Thing(Entity):
    __slots__ = 'materials',

    fluid = False
    
    def __init__(self, kind, materials):
        Entity.__init__(self, kind)
        self.materials = materials

    def volume(self):
        return sum([m.amount for m in self.materials])

    def mass(self):
        return sum([m.mass() for m in self.materials])

class StockpileType(object):
    def __init__(self, description):
        self.description = description

class Beverage(Thing):
    __slots__ = ()
    
    fluid = True
    
    def __init__(self, amount):
        Thing.__init__(self, 'beverage', [Material(Water, amount)])

    def description(self):
        return _('{drink} ({volume} L)').format(drink=self.noun,
                                                volume=
                                                self.materials[0].amount * 1000)

class Wine(Beverage):
    noun = _('wine')
    stocktype = StockpileType(_('wine'))

    def __init__(self, amount):
        Beverage.__init__(self, amount)

class Item(Thing):
    __slots__ = 'color', 'location', 'reserved'
    
    def __init__(self, kind, materials, location):
        Thing.__init__(self, kind, materials)
        self.color = self.materials[0].substance.color
        self.location = location
        self.reserved = False

class OutOfSpace(Exception):
    pass

class Storage(object):
    __slots__ = 'capacity', 'contents'
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.contents = []

    def description(self, name):
        n = len(self.contents)
        if n == 0:
            return _(u'empty {container}').format(container=name)
        elif n == 1:
            return _(u'{container} of {contents}').format(container=name,
                                                         contents=
                                                         self.contents[0]
                                                         .description())
        else:
            return _(u'{container} containing {items}').format(container=name,
                                                  items=', '.join([item.description()
                                                                  for item
                                                                  in self.contents]))

    def find(self, test):
        for item in self.contents:
            if test(item):
                return item
            elif hasattr(item, 'find'):
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
                              if hasattr(item, 'contents')]:
                if container.remove(item):
                    return True
        return False

    def has(self, kind):
        return self.find(lambda item: isinstance(item, kind)) is not None

class WrongItemType(Exception):
    pass

class Stockpile(Entity):
    __slots__ = 'storage', 'components', 'types', 'changed'
    
    color = (255,255,255)
    noun = _('stockpile')
    
    def __init__(self, region, types):
        Entity.__init__(self, 'stockpile')
        self.storage = Storage(0)
        self.components = []
        self.types = types
        self.changed = False
        for location in region:
            self.annex(location)

    @property
    def capacity(self):
        return self.storage.capacity

    @property
    def contents(self):
        return self.storage.contents
            
    def description(self):
        return self.storage.description(self.noun)
    
    def find(self, test):
        return self.storage.find(test)

    def space(self):
        return self.storage.space()
    
    def has(self, kind):
        return self.storage.has(kind)

    def accepts(self, option):
        return option in self.types

    def add(self, item):
        if self.accepts(item.stocktype):
            self.storage.add(item)
            self.changed = True
        else:
            raise WrongItemType()

    def remove(self, item):
        success = self.storage.remove(item)
        if success:
            self.changed = True
        return success
        
    def annex(self, location):
        self.storage.capacity += 1.0
        self.components.append(StockpileComponent(self, location))
        self.changed = True

class Container(Item):
    __slots__ = 'storage',
    
    def __init__(self, kind, materials, location, capacity):
        Item.__init__(self, kind, materials, location)
        self.storage = Storage(capacity)

    @property
    def capacity(self):
        return self.storage.capacity

    @property
    def contents(self):
        return self.storage.contents

    @property
    def stocktype(self):
        if self.contents:
            first = self.contents[0].stocktype
            return (first
                    if all([c.stocktype == first for c in self.contents[1:]])
                    else None)
        else:
            return self.containerstocktype

    def volume(self):
        return Thing.volume(self) + self.capacity

    def mass(self):
        return Thing.mass(self) + sum([item.mass() for item in self.contents])

    def description(self):
        return self.storage.description('{substance} {container}'.format(
            substance = self.materials[0].substance.adjective,
            container = self.noun))

    def find(self, test):
        return self.storage.find(test)

    def add(self, item):
        return self.storage.add(item)

    def space(self):
        return self.storage.space()

    def remove(self, item):
        return self.storage.remove(item)

    def has(self, kind):
        return self.storage.has(kind)

class StockpileComponent(Container):
    __slots__ = 'stockpile',
    
    def __init__(self, stockpile, location):
        Container.__init__(self, stockpile.kind,
                           [Material(AEther, 0)], location, 1.0)
        self.stockpile = stockpile

    def description(self):
        return self.stockpile.description

class Corpse(Item):
    __slots__ = 'origins',
    
    stocktype = StockpileType(_('Corpse'))
        
    def __init__(self, creature):
        Item.__init__(self, 'corpse', creature.materials, creature.location)
        self.origins = creature

    def description(self):
        return _('corpse of {0}').format(self.origins.description())

class Barrel(Container):
    __slots__ = ()

    noun = _('barrel')
    
    containerstocktype = StockpileType(_('Empty barrel'))
    
    def __init__(self, location, substance):
        Container.__init__(self, 'barrel',
                           [Material(substance, 0.075)], location, 0.25)
        self.contents.append(Wine(self.capacity))

Arms = _('Weapons and armor'), []
BuildingMaterials = _('Building materials'), []
Clothing = _('Clothing'), []
Drinks = _('Drink'), [Wine.stocktype]
Food = _('Food'), []
Furniture = _('Furnishings'), []
Products = _('Trade products and supplies'), [Barrel.containerstocktype]
Refuse = _('Refuse'), [Corpse.stocktype]
Resources = _('Raw materials'), []
Tools = _('Tools and equipment'), []

StockpileCategories = [
    Arms,
    BuildingMaterials,
    Clothing,
    Drinks,
    Food,
    Furniture,
    Products,
    Resources,
    Tools
    ]

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
            self.nearest.location[0:2]) > self.subject.eyesight():
            raise TaskImpossible()

        if self.nearest.location == self.subject.location:
            return []
        else:
            reqs = [Follow(self.subject, self.world, self.nearest)]
            return reqs[0].requirements() + reqs

    def work(self):
        self.nearest.health -= 1
        return self.nearest.health <= 0

class AcquireItem(Task):
    def __init__(self, subject, world, item):
        self.subject = subject
        self.world = world
        self.item = item

    def requirements(self):
        if self.subject.location != self.item.location:
            try:
                reqs = [GoToGoal(self.subject, self.world,
                                        self.item.location)]
            except:
                raise TaskImpossible()
        else:
            reqs = []

        return reqs[0].requirements() + reqs if reqs else reqs

    def work(self):
        self.world.removefromstockjobs(self.item)
        self.world.space[self.item.location].items.remove(self.item)
        self.item.location = None
        self.subject.inventory.add(self.item)
        return True

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
            try:
                self.nearest = sorted([item for item in self.items()
                                       if self.test(item)],
                                      key = lambda item:
                                      self.world.space.pathing.distance_xy(
                                          self.subject.location[0:2],
                                          item.location[0:2]))[0]
            except IndexError:
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
                     hasattr(item, 'has') and item.has(target)) or
                    isinstance(item, target) for target in self.targets])

class AcquireNonStockpiled(Acquire):
    def __init__(self, subject, world, stockpile):
        Acquire.__init__(self, subject, world, self.istarget, stockpile.capacity)
        self.destination = stockpile

    def items(self):
        return [item for item in self.world.items
                if item.location is not None and
                not item.reserved]

    def istarget(self, item):
        return self.destination.accepts(item.stocktype)

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
                                             hasattr(item, 'has') and
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
    def __init__(self, subject, world, stockpile, item):
        self.subject = subject
        self.world = world
        self.stockpile = stockpile
        self.item = item

    def find(self, item):
        return item == self.item

    def requirements(self):
        if self.subject.inventory.find(self.find) is None:
            reqs = [AcquireItem(self.subject, self.world, self.item)]
        else:
            reqs = []

        if self.subject.location != self.stockpile.components[0].location:
            reqs = reqs + [GoToGoal(self.subject, self.world,
                                    self.stockpile.components[0].location)]

        return reqs[0].requirements() + reqs if len(reqs) else reqs

    def work(self):
        item = self.subject.inventory.find(self.find)

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
        stockjob = next((j for j in self.world.stockjobs.itervalues()
                         if j[0] and j[1]), None)
        if stockjob is None:
            raise TaskImpossible()

        stockpile, item = [q[0] for q in stockjob]
        
        reqs = [StoreItem(self.subject, self.world, stockpile, item)]
        return reqs[0].requirements() + reqs

    def work(self):
        return True

class AttemptDigDesignation(Task):
    def __init__(self, subject, world):
        self.subject = subject
        self.world = world
        self.designation = self.world.digjobs.popleft()

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

        self.world.digjobs.append(self.designation)

        raise TaskImpossible()

    def work(self):
        self.world.dig(self.designation)
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

class JobOption(object):
    def __init__(self, definition, condition, priority):
        self.definition = definition
        self.condition = condition
        self.priority = priority

    @staticmethod
    def prioritykey(option):
        return option.priority

class PhysicalAttribute(object):
    description = None
    adverbs = _('great'), _('considerable'), _('average'), _('unremarkable'), _('not much')

class Sense(PhysicalAttribute):
    adverbs = _('excellent'), _('keen'), _('average'), _('dull'), _('extremely dull')

class Strength(PhysicalAttribute):
    description = _('strength')

class Speed(PhysicalAttribute):
    description = _('speed')

class Sight(Sense):
    description = _('eyesight')

class Hearing(Sense):
    description = _('hearing')

class Smell(Sense):
    description = _('olfactory powers')

class Dexterity(PhysicalAttribute):
    description = _('dexterity')

class Toughness(PhysicalAttribute):
    description = _('physical fortitude')

def sampleattributes(attributes):
    return dict((a, gauss(attributes[a], 10)) for a in attributes.keys())

def indefinitearticle(noun):
    m = search('LETTER ([^ ])', unicodename(unicode(noun[0])))
    return _('an') if m and all([c in 'AEIOUH' for c in m.group(1)]) else _('a')

class Creature(Thing):
    __slots__ = (
        'attributes',
        'color',
        'location',
        'inventory',
        'job',
        'hydration',
        'rest',
        'remove'
        )
    
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
        self.attributes = sampleattributes(self.race)
        self.color = color
        self.location = location
        self.inventory = Storage(1.0)
        self.job = None
        self.hydration = randint(900, 3600)
        self.rest = random() * self.speed()
        self.remove = False

    def propername(self):
        return _(u'this')

    def namecard(self):
        return _(u'{a} {name}').format(a=indefinitearticle(self.noun),
                                      name=self.noun).capitalize()

    def objectpronoun(self):
        return _(u'it')

    def subjectpronoun(self):
        return _(u'it')

    def sexdescription(self):
        return _(u'neuter')

    def colordescription(self):
        return _(u'is the color {hue}').format(hue=describecolor(self.color))

    def die(self, world):
        self.remove = True
        world.additem(Corpse(self))

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

    def eyesight(self):
        return gauss(self.attributes[Sight],10) / 10

    def speed(self):
        return 20 - gauss(self.attributes[Speed],10) / 10

    def attributetext(self, attribute):
        normal = self.race[attribute]
        d = self.attributes[attribute] - normal
        if d > 20:
            adv = attribute.adverbs[0]
        elif d > 10:
            adv = attribute.adverbs[1]
        elif d < -20:
            adv = attribute.adverbs[3]
        elif d < -10:
            adv = attribute.adverbs[4]
        else:
            return None
            
        if (d > 15 and normal < 90) or (d < -15 and normal > 110):
            qual = ' ' + _(u'for {a} {race}').format(
                a=indefinitearticle(self.noun), race=self.noun)
        elif (d > 25 and normal > 110) or (d < -25 and normal < -90):
            qual = ' ' + _(u'even for {a} {race}').format(
                a=indefinitearticle(self.noun), race=self.noun)
        else:
            qual = ''
            
        return _(u'{adverb} {attribute}{qualifier}').format(
            adverb=adv,
            attribute=attribute.description,
            qualifier=qual)

    def physical(self):
        pronoun = self.subjectpronoun().capitalize()
        
        value = _(u'{name} is {a} {race}. {she} {has_coloring}.').format(
            name=self.propername().title(),
            a=indefinitearticle(self.noun),
            race=self.noun,
            she=pronoun,
            has_coloring=self.colordescription())
        
        for text in [self.attributetext(a) for a in self.attributes.keys()]:
            if not text:
                continue

            value += ' ' + _(u'{she} has {attribute}.').format(
                she=pronoun, attribute=text)

        return value + ' ' + _(u'{she} is physically {sex}.').format(
            she=pronoun, sex=self.sexdescription())
            
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
            
        self.rest += self.speed()

class Sex(object):
    pass

class Male(Sex):
    description = _(u'male')

class Female(Sex):
    description = _(u'female')

class Gender(object):
    pass

class Woman(Gender):
    objectpronoun = _(u'her')
    subjectpronoun = _(u'she')

class Man(Gender):
    objectpronoun = _(u'him')
    subjectpronoun = _(u'he')

class SexualCreature(Creature):
    __slots__ = 'sex'
    
    def __init__(self, kind, materials, color, location, sex):
        Creature.__init__(self, kind, materials, color, location)
        self.sex = sex

    def sexdescription(self):
        return self.sex.description

class CulturedCreature(SexualCreature):
    __slots__ = 'gender', 'name'

    def __init__(self, kind, materials, color, location, sex, gender):
        SexualCreature.__init__(self, kind, materials, color, location, sex)
        self.name = self.culture[NameSource].generate()
        self.gender = gender

    def propername(self):
        return self.name

    def namecard(self):
        return self.name

    def objectpronoun(self):
        return self.gender.objectpronoun

    def subjectpronoun(self):
        return self.gender.subjectpronoun

class DemographicFigure(object):
    pass

class Maleness(DemographicFigure):
    pass

class MaleWomen(DemographicFigure):
    pass

class FemaleMen(DemographicFigure):
    pass

class NameSource(object):
    pass

class NameGenerator(object):
    def __init__(self, lexicon, count):
        self.count = count
        with openunicode(lexicon, 'r', 'utf_8') as f:
            self.generator = Generator(f.read())
            self.generator.process()
            self.generator.calculate()

    def generate(self):
        return ' '.join([self.generator.generate().capitalize()
                         for i in range(self.count)])

class Human(CulturedCreature):
    __slots__ = ()

    noun = _(u'human')
    race = {
        Strength : 100,
        Speed : 100,
        Sight : 100,
        Hearing : 100,
        Smell : 100,
        Dexterity : 100,
        Toughness : 100
        }
    culture = {
        Maleness : 0.5,
        MaleWomen : 0.01,
        FemaleMen : 0.01,
        NameSource : NameGenerator('fr.txt', 2)
        }
    
class Elf(CulturedCreature):
    __slots__ = ()

    noun = _(u'elf')
    race = {
        Strength : 80,
        Speed : 140,
        Sight : 120,
        Hearing : 120,
        Smell : 100,
        Dexterity : 140,
        Toughness : 80
        }
    culture = {
        Maleness : 0.5,
        MaleWomen : 0.05,
        FemaleMen : 0.05,
        NameSource : NameGenerator('fi.txt', 2)
        }

class Dwarf(CulturedCreature):
    __slots__ = ()

    noun = _(u'dwarf')
    health = 10
    jobs = sorted(Creature.jobs +
                  [JobOption(DigDesignation,
                             lambda c, w: w.digjobs,
                             10),
                   JobOption(StoreInStockpile,
                             lambda c, w: w.stockjobs,
                             90)],
                  key = JobOption.prioritykey)
    thirst = 0.03
    race = {
        Strength : 120,
        Speed : 80,
        Sight : 120,
        Hearing : 60,
        Smell : 80,
        Dexterity : 120,
        Toughness : 120
        }
    culture = {
        Maleness : 0.5,
        MaleWomen : 0.01,
        FemaleMen : 0.01,
        NameSource : NameGenerator('gd.txt', 2)
        }
    
    def __init__(self, location):
        r = randint(80,255)
        
        if random() < self.culture[Maleness]:
            sex = Male
            gender = Woman if random() < self.culture[MaleWomen] else Man
        else:
            sex = Female
            gender = Man if random() < self.culture[FemaleMen] else Woman

        CulturedCreature.__init__(self, 'dwarf', [Material(Meat, 0.075)],
                                  (r, r-40, r-80), location, sex, gender)

    def colordescription(self):
        return _(u'has {hue} skin').format(hue=describecolor(self.color))
        
class Goblin(CulturedCreature):
    __slots__ = ()
    
    noun = _(u'goblin')
    health = 0
    jobs = sorted(Creature.jobs +
                  [JobOption(SeekAndDestroy,
                             lambda c, w: any([isinstance(c, Dwarf)
                                               for c in w.creatures]),
                             10)],
                  key = JobOption.prioritykey)
    thirst = 0.01
    race = {
        Strength : 90,
        Speed : 120,
        Sight : 80,
        Hearing : 120,
        Smell : 120,
        Dexterity : 110,
        Toughness : 80
        }
    culture = {
        Maleness : 0.25,
        MaleWomen : 0,
        FemaleMen : 0.5,
        NameSource : NameGenerator('no.txt', 1)
        }
    
    def __init__(self, location):
        if random() < self.culture[Maleness]:
            sex = Male
            gender = Woman if random() < self.culture[MaleWomen] else Man
        else:
            sex = Female
            gender = Man if random() < self.culture[FemaleMen] else Woman

        CulturedCreature.__init__(self, 'goblin', [Material(Meat, 0.05)],
                                  (32, 64+randint(0,127),64+randint(0,127)),
                                  location, sex, gender)

    def colordescription(self):
        return _(u'has {hue} skin').format(hue=describecolor(self.color))

class Tortoise(SexualCreature):
    __slots__ = ()
    
    health = 10
    noun = _(u'giant tortoise')
    thirst = 0.1
    race = {
        Strength : 120,
        Speed : 20,
        Sight : 20,
        Hearing : 100,
        Smell : 100,
        Dexterity : 20,
        Toughness : 120
        }
    
    def __init__(self, location):
        d = randint(-20,10)
        SexualCreature.__init__(self, 'tortoise', [Material(Meat, 0.3)],
                                (188+d,168+d,138+d), location,
                                choice([Male,Female]))
        
    def colordescription(self):
        return _(u'has a shell tinted {hue}').format(
            hue=describecolor(self.color))
        
class SmallSpider(SexualCreature):
    __slots__ = ()
    
    noun = _(u'spider')
    health = 10
    thirst = 0.0001
    race = {
        Strength : 20,
        Speed : 180,
        Sight : 20,
        Hearing : 20,
        Smell : 20,
        Dexterity : 180,
        Toughness : 20
        }
    
    def __init__(self, location):
        SexualCreature.__init__(self, 'spider-small', [Material(Meat, 0.0001)],
                                (95, randint(0,40), 0), location,
                                choice([Male,Female]))

    def colordescription(self):
        color = describecolor(self.color)
        return _(u'has {a} {hue} body').format(a=indefinitearticle(color),
                                              hue=color)
        
class World(object):
    def __init__(self, space, items):
        self.space = space
        self.items = items
        self.creatures = []
        self.digjobs = deque()
        self.stockpiles = []
        self.stockjobs = {}

    def designatefordigging(self, location):
        tile = self.space[location]
        if isinstance(tile, Earth):
            tile.designated = True
            if (tile.revealed or
                isinstance(self.space[location[0:2] + (location[2]+1,)], Empty)):
                self.digjobs.append(location)
            self.space.changed = True

    def dig(self, location):
        tile = Empty(randint(0,3))
        tile.revealed = True
        for x,y in self.space.pathing.adjacent_xy(location[0:2]):
            nloc = x, y, location[2]
            n = self.space[nloc]
            if not n.revealed:
                n.revealed = True
                if n.designated:
                    self.digjobs.append(nloc)
        if location[2]:
            bloc = location[0:2] + (location[2]-1,)
            b = self.space[bloc]
            if not b.revealed and b.designated:
                self.digjobs.append(bloc)
        self.space[location] = tile

    def addstockpile(self, stockpile):
        for t in stockpile.types:
            try:
                self.stockjobs[t][0].append(stockpile)
            except KeyError:
                self.stockjobs[t] = deque([stockpile]), deque()
                
        self.stockpiles.append(stockpile)

    def additem(self, item, stockpiled = None):
        if item.location is not None:
            self.space[item.location].items.append(item)

        if not stockpiled:
            try:
                self.addtostockjobs(item)
            except KeyError:
                self.stockjobs[item.stocktype] = deque(), deque([item])
            
        self.items.append(item)

    def addtostockjobs(self, item):
        self.stockjobs[item.stocktype][1].append(item)

    def removefromstockjobs(self, item):
        self.stockjobs[item.stocktype][1].remove(item)        

    def removeitem(self, item, stockpiled = None):
        if item.location is not None:
            self.space[item.location].items.remove(item)

        if not stockpiled:
            self.removefromstockjobs(item)
            
        self.items.remove(item)
