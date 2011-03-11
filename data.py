from codecs import open as openunicode
from collections import deque
from itertools import chain
from math import pi, sin, cos
from pdb import set_trace
from random import betavariate, choice, gauss, randint, random
from re import search
from unicodedata import name as unicodename

from colordb import match as describecolor
from jobs import *
from space import Direction, Earth, Empty, Floor, TreeTrunk
from substances import AEther, Meat, Water, Stone, Wood
from language import Generator
from skills import SkillSet
from sound import Dig, Fall, Fight, Mine, Step
from stocktype import StockpileType

class Material(object):
    __slots__ = 'substance', 'amount'
    
    def __init__(self, substance, amount):
        self.substance = substance
        self.amount = amount

    def mass(self):
        return self.substance.density * self.amount

class Entity(object):
    __slots__ = ()
    
    volatile = False

class Thing(Entity):
    __slots__ = 'materials',

    fluid = False
    
    def __init__(self, materials):
        self.materials = materials

    def volume(self):
        return sum([m.amount for m in self.materials])

    def mass(self):
        return sum([m.mass() for m in self.materials])

class Beverage(Thing):
    __slots__ = ()
    
    fluid = True
    
    def __init__(self, amount):
        Thing.__init__(self, [Material(Water, amount)])

    def description(self):
        return _(u'{drink} ({volume} L)').format(drink=self.noun,
                                                volume=
                                                self.materials[0].amount * 1000)

class Wine(Beverage):
    noun = _(u'wine')
    stocktype = StockpileType(_(u'wine'))

    def __init__(self, amount):
        Beverage.__init__(self, amount)

class Item(Thing):
    __slots__ = 'color', 'location', 'reserved'
   
    def __init__(self, materials, location):
        Thing.__init__(self, materials)
        self.color = self.materials[0].substance.color
        self.location = location
        self.reserved = False

    def description(self):
        return _('{material} {thing}').format(
            material = self.materials[0].substance.adjective,
            thing = self.noun)

class SimpleItem(Item):
    __slots__ = ()

    def __init__(self, material, location):
        Item.__init__(self, [material], location)

    @property
    def material(self):
        return self.materials[0]

    @classmethod
    def substancetest(cls, s):
        return False

class Liquid(SimpleItem):
    __slots__ = ()
    volatile = True

    stocktype = None

    def __init__(self, substance, location):
        SimpleItem.__init__(self, Material(substance, 1.0), location)

    def description(self):
        return self.material.substance.noun

class Workbench(SimpleItem):
    __slots__ = ('jobs')
    
    noun = _(u'workbench')

    stocktype = StockpileType(_(u'Workbench'))

    def __init__(self, location, substance):
        SimpleItem.__init__(self, Material(substance, 0.025), location)
        self.jobs = deque()

    @classmethod
    def substancetest(cls, s):
        return s.rigid

class LooseMaterial(SimpleItem):
    __slots__ = ()

    def __init__(self, substance, location):
        SimpleItem.__init__(self, Material(substance, 0.1), location)

    def description(self):
        return _(u'loose {material}').format(
            material = self.substance.noun)

    @property
    def substance(self):
        return self.materials[0].substance

    @property
    def stocktype(self):
        return self.substance.stocktype

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
    __slots__ = 'storage', 'region', 'types', 'changed', 'player'
    
    color = (255,255,255)
    noun = _(u'stockpile')
    
    def __init__(self, region, types):
        self.storage = Storage(0)
        self.region = [location for location in region]
        self.storage.capacity = float(len(self.region))
        self.types = types
        self.changed = False

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

class Container(Item):
    __slots__ = 'storage',
    
    def __init__(self, materials, location, capacity):
        Item.__init__(self, materials, location)
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

class Corpse(Item):
    __slots__ = 'origins',
    
    stocktype = StockpileType(_(u'Corpse'))
        
    def __init__(self, creature):
        Item.__init__(self, creature.materials, creature.location)
        self.origins = creature

    def description(self):
        return _(u'corpse of {0}').format(self.origins.namecard())

def conjunction(items):
    if len(items) > 2:
        return _(u', ').join(items[:-1]) + _(u', and {last}').format(
            last=items[-1])
    elif len == 2:
        return _(u'{first} and {second}').format(first=items[0], second=items[1])
    else:
        return items[0]

def indefinitearticle(noun):
    m = search('LETTER ([^ ])', unicodename(unicode(noun[0])))
    return _(u'an') if m and all([c in 'AEIOUH' for c in m.group(1)]) else _(u'a')

class CompoundItem(Item):
    __slots__ = 'components',

    assemblyskill = None

    def __init__(self, components, location):
        Item.__init__(self, list(chain(*[c.materials for c in components])),
                      location)
        self.components = components
        for c in self.components:
            if c.location is not None and c.location != self.location:
                raise ValueError()
            c.location = None

    def description(self):
        items = conjunction(self.components)
        return _(u'object made of {an} {itemlist}',
                 an = indefinitearticle(items),
                 itemlist = items)

class Barrel(Container):
    __slots__ = ()

    noun = _(u'barrel')
    
    containerstocktype = StockpileType(_(u'Empty barrel'))
    
    def __init__(self, location, substance):
        Container.__init__(self,
                           [Material(substance, 0.075)], location, 0.25)
        self.contents.append(Wine(self.capacity))

    @classmethod
    def substancetest(cls, s):
        return s.rigid

class Bag(Container):
    __slots__ = ()

    noun = _(u'bag')

    containerstocktype = StockpileType(_(u'Empty bag'))

    def __init__(self, location, substance):
        Container.__init__(self, [Material(substance, 0.05)], location, 0.1)

    @classmethod
    def substancetest(cls, s):
        return not s.rigid

class Handle(SimpleItem):
    __slots__ = ()

    noun = _(u'ax handle')

    stocktype = StockpileType(_(u'Ax handle'))

    def __init__(self, substance, location):
        SimpleItem.__init__(self, Material(substance, 0.0017), location)

    @classmethod
    def substancetest(cls, s):
        return s.rigid and s.density < 1000

class AxHead(SimpleItem):
    __slots__ = ()

    noun = _(u'ax head')

    stocktype = StockpileType(_(u'Ax head'))

    def __init__(self, substance, location):
        SimpleItem.__init__(self, Material(substance, 0.0005), location)

    @classmethod
    def substancetest(cls, s):
        return s.rigid and s.density > 1000

class PickaxHead(SimpleItem):
    __slots__ = ()

    noun = _(u'pickax head')

    stocktype = StockpileType(_(u'Pickax head'))

    def __init__(self, material, location):
        SimpleItem.__init__(self, material, location)

    @classmethod
    def substancetest(cls, s):
        return s.rigid and s.density > 1000
        
class Ax(CompoundItem):
    __slots__ = ()

    noun = _(u'ax')

    stocktype = StockpileType(_(u'Ax'))

    def __init__(self, location, blade, handle):
        CompoundItem.__init__(self, [blade, handle], location)

    def description(self):
        return _(u'{metal} {ax} with {wooden} handle').format(
            metal = self.materials[0].substance.adjective,
            ax = self.noun,
            wooden = self.materials[1].substance.adjective)

class Pickax(Item):
    __slots__ = ()
    
    noun = _(u'pickax')

    stocktype = StockpileType(_(u'Pickax'))
    
    def __init__(self, location, blade, handle):
        Item.__init__(self, [Material(blade, 0.00025),
                             Material(handle, 0.0017)],
                      location)

    def description(self):
        return _(u'{metal} {pick} with {wooden} handle').format(
            metal = self.materials[0].substance.adjective,
            pick = self.noun,
            wooden = self.materials[1].substance.adjective)

Arms = StockpileType(_(u'Weapons and armor'), [])
BuildingMaterials = StockpileType(_(u'Building materials'), [])
Clothing = StockpileType(_(u'Clothing'), [])
Drinks = StockpileType(_(u'Drink'), [Wine.stocktype])
Food = StockpileType(_(u'Food'), [])
Furnishings = StockpileType(_(u'Furnishings'), [Workbench.stocktype])
Products = StockpileType(_(u'Trade products and supplies'),
                         [Barrel.containerstocktype])
Refuse = StockpileType(_(u'Refuse'), [Corpse.stocktype])
Resources = StockpileType(_(u'Raw materials'), [])
Tools = StockpileType(_(u'Tools and equipment'), [Pickax.stocktype, Ax.stocktype])

StockpileCategories = [
    Arms,
    BuildingMaterials,
    Clothing,
    Drinks,
    Food,
    Furnishings,
    Products,
    Resources,
    Tools
    ]

class PhysicalAttribute(object):
    description = None
    adverbs = _(u'great'), _(u'considerable'), _(u'average'), _(u'unremarkable'), _(u'not much')

class Sense(PhysicalAttribute):
    adverbs = _(u'excellent'), _(u'keen'), _(u'average'), _(u'dull'), _(u'extremely dull')

class Strength(PhysicalAttribute):
    description = _(u'strength')

class Speed(PhysicalAttribute):
    description = _(u'speed')

class Sight(Sense):
    description = _(u'eyesight')

class Hearing(Sense):
    description = _(u'hearing')

class Smell(Sense):
    description = _(u'olfactory powers')

class Dexterity(PhysicalAttribute):
    description = _(u'dexterity')

class Toughness(PhysicalAttribute):
    description = _(u'physical fortitude')

def sampleattributes(attributes):
    return dict((a, gauss(attributes[a], 10)) for a in attributes.keys())

class Labor(object):
    pass

class SkilledLabor(Labor):
    skill = []
    increment = 0

    @classmethod
    def skilldisplayed(cls, creature, boost = None):
        boost = boost if boost is not None else 0
        exp = creature.skills.exp(cls.skill)
        skill = 0.5 - cos(exp * pi)/2
        total = 35 - 30 * sin(exp * pi)
        skill = max(0, min(1, skill + boost)) * 0.9 + 0.05
        alpha = skill * total
        return betavariate(alpha, total - alpha)

    @classmethod
    def trainskill(cls, creature):
        creature.skills.train(cls.skill, cls.increment)

class ToolLabor(SkilledLabor):
    tools = []

    @classmethod
    def toil(cls, creature, world):
        for tool in cls.tools:
            if not creature.inventory.has(tool):
                for step in acquireitem(creature,
                                        world, tool.stocktype, tool):
                    yield step

class Manufacturing(SkilledLabor):
    substance = None

    @classmethod
    def description(cls, substance, item):
        return _(u'make {substance} {item}').format(
            substance=substance.adjective,
            item=item.noun)
    
    @classmethod
    def manufacture(cls, creature, world):
        for loc, bench in creature.player.furniture(Workbench):
            if not bench.reserved and bench.jobs and issubclass(bench.jobs[0][1], cls.substance):
                itemtype, substance = bench.jobs.popleft()
                bench.reserved = True
                break
        else:
            yield True, None

        for step in acquireitem(creature, world, substance.stocktype,
                                                 LooseMaterial):
            yield False, step

        material = creature.inventory.find(
            lambda item: isinstance(item, LooseMaterial) and
            item.stocktype == substance.stocktype)
        if not material:
            bench.reserved = False
            bench.jobs.append((itemtype, substance))
            yield True, None
        material.reserved = True

        for step in goto(creature, world, loc):
            yield False, _(u'{going} to {bench}').format(
                going=step, bench=bench.description)
        if creature.location != loc:
            bench.reserved = False
            bench.jobs.append((itemtype, substance))

            for step in stashitem(creature, world, material):
                yield False, step

            yield True, None

        work = 0
        while work < material.substance.density:
            yield False, _(u'crafting {item}').format(item = itemtype.noun)

            progress = max(1,
                           512 *
                           cls.skilldisplayed(creature))
            
            work += progress

        creature.inventory.remove(material)
        world.additem(itemtype(creature.location, material.substance))
        
        cls.trainskill(creature)

        yield True, None
        
    @classmethod
    def toil(cls, creature, world):
        for done, step in cls.manufacture(creature, world):
            if done:
                return
            else:
                yield step

class Carpentry(Manufacturing):
    substance = Wood
    noun = _(u'carpentry')
    skill = ['crafting', 'woodwork']

class Masonry(Manufacturing):
    substance = Stone
    noun = _(u'masonry')
    skill = ['crafting', 'stonework']
    
class Mining(ToolLabor):
    noun = _(u'mining')
    skill = ['earthwork', 'mining', 'digging']
    increment = 0.0001
    tools = [Pickax]

    @staticmethod
    def adjoin(creature, world, location):
        for (x,y) in world.space.pathing.adjacent_xy(location[0:2]):
            goal = (x,y,location[2])
            adjacent = world.space[goal]
            if (adjacent and adjacent.is_passable() and
                not world.space[(x,y,location[2]-1)].is_passable()):
                for step in goto(creature, world, goal):
                    yield _(u'{going} adjacent to dig site').format(
                        going=step), goal
                if creature.location == goal:
                    yield None, None

    @staticmethod
    def mount(creature, world, location):
        goal = location[0:2] + (location[2]+1,)
        atop = world.space[goal]
        if atop.is_passable():
            for step in goto(creature, world, goal):
                yield _(u'{going} to top of dig site').format(
                    going=step), goal
            if creature.location == goal:
                yield None, None

    @classmethod
    def approach(cls, creature, world, location):
        for step, goal in cls.adjoin(creature, world, location):
            if step:
                yield step, goal
            else:
                break
        else:
            for step, goal in cls.mount(creature, world, location):
                if step:
                    yield step, goal
                else:
                    break                

    @classmethod
    def toil(cls, creature, world):
        for step in super(Mining, cls).toil(creature, world):
            yield step

        pick = creature.inventory.find(lambda item:
                                       isinstance(item, cls.tools[0]))

        if pick is None or not creature.player.digjobs:
            return

        location = creature.player.digjobs.popleft()

        goal = None
        for step, goal in cls.approach(creature, world, location):
            yield step

        if (creature.location != goal):
            return

        tile = world.space[location]

        work = 0
        while isinstance(tile, Earth) and work < tile.substance.density:
            yield _(u'mining {earth}').format(earth=tile.substance.noun)

            progress = max(1,
                           512 *
                           creature.strength() *
                           cls.skilldisplayed(creature))
            
            work += progress
            tile = world.space[location]

        if isinstance(tile, Earth):
            world.dig(location, creature)
            cls.trainskill(creature)
    
class Woodcutting(ToolLabor):
    noun = _(u'woodcutting')
    skill = ['lumberwork', 'woodcutting']
    increment = 0.0001
    tools = [Ax]

    @classmethod
    def toil(cls, creature, world):
        for step in super(Woodcutting, cls).toil(creature, world):
            yield step

        ax = creature.inventory.find(lambda item:
                                     isinstance(item, cls.tools[0]))

        if ax is None or not creature.player.felljobs:
            return

        tree = creature.player.felljobs.popleft()

        goal = Direction.move(tree.location, Direction.opposite[tree.fell])
        if not isinstance(world.space[goal], Floor):
            creature.player.felljobs.append(tree)
            return

        for step in goto(creature, world, goal):
            yield _(u'{going} to fell {tree}').format(
                going=step, tree=tree.description), goal

        if (creature.location != goal):
            return

        work = 0
        while work < tree.wood.density:
            yield _(u'felling {tree}').format(tree=tree.description)

            progress = max(1,
                           512 *
                           creature.strength() *
                           cls.skilldisplayed(creature))
            
            work += progress

            world.makesound(tree.wood.sound, tree.location)

        push = int((1-cls.skilldisplayed(creature, 0.75)) * 6)
        if push != 0:
            push *= choice((-1,1))
        direction = Direction.clockwise[
            Direction.clockwise.index(tree.fell) + push]
        world.collapsetree(creature, tree, direction)

        cls.trainskill(creature)
            
class Stockpiling(Labor):
    noun = _(u'stockpiling')

    @classmethod
    def stockpileitem(cls, creature, world):
        jobs = creature.player.stockjobs
        for stocktype, (stockpiles, items) in jobs.iteritems():
            if stockpiles and items:
                pile, item = stockpiles.popleft(), items.popleft()
                stockpiles.append(pile)
                for step in takeitem(creature, world, item):
                    yield False, step
                if not creature.inventory.find(lambda i: i is item):
                    items.append(item)
                    return

                for step in goto(creature, world, pile.region[0]):
                    yield False, step
                if creature.location not in pile.region:
                    items.append(item)
                    return

                creature.inventory.remove(item)
                pile.add(item)

        yield True, None

    @classmethod
    def toil(cls, creature, world):
        for done, step in cls.stockpileitem(creature, world):
            if done:
                return
            else:
                yield step

class Furnishing(Labor):
    noun = _(u'furnishing')

    @classmethod
    def furnishlocation(cls, creature, world):
        jobs = creature.player.furnishjobs
        if jobs:
            location, item = jobs.popleft()
            for step in takeitem(creature, world, item):
                yield False, step
            if not creature.inventory.find(lambda i: i is item):
                creature.player.furnish(location, item)
                return

            for step in goto(creature, world, location):
                yield False, step
            if creature.location != location:
                creature.player.furnish(location, item)
                return

            creature.inventory.remove(item)
            world.setfurnishing(location, item, creature.player)

        yield True, None

    @classmethod
    def toil(cls, creature, world):
        for done, step in cls.furnishlocation(creature, world):
            if done:
                return
            else:
                yield step

LaborOptions = [
    (u'crafts', [Carpentry,Masonry]),
    (u'physical labor', [Mining,Woodcutting]),
    (u'hauling', [Stockpiling,Furnishing])]
        
class Appetite(object):
    __slots__ = '_pentup', '_creature', '_threshold'

    stocktype = None
    itemtype = None    

    def __init__(self, creature, threshold):
        self._creature = creature
        self._threshold = threshold
        self._pentup = randint(0, self._threshold/2)

    def step(self, dt):
        self._pentup += dt

    def slake(self, amount):
        self._pentup -= amount

    @property
    def sated(self):
        return self._pentup <= 0

    def pursue(self, world):
        if self._pentup < self._threshold:
            return

        yield _(u'looking for {desire}').format(desire=self.requirement)

        for step in self.attempt(world):
            yield step

    def status(self):
        if self._pentup < 200:
            return _(u'has recently enjoyed {desire}').format(
                desire = self.requirement)
        elif self._pentup > 1800:
            prev = _(u'has not partaken of {desire} in some time').format(
                desire = self.requirement)
            if self._threshold - self._pentup < 200:
                prev += _(u' and will soon need to seek it out')
            return prev
        else:
            return None

class SexualRelease(Appetite):
    __slots__ = ()
    
    requirement = _(u'physical intimacy')

class Socialization(Appetite):
    __slots__ = ()

    requirement = _(u'social fellowship')

class WaterDrinking(Appetite):
    __slots__ = ()

    requirement = _(u'potable water')

class ItemAppetite(Appetite):
    __slots__ = ()
    
    def attempt(self, world):
        for step in acquireitem(self._creature, world,
                                               self.stocktype,
                                               self.itemtype):
            yield step

        for step in self.consume(world):
            yield step

class BoozeDrinking(ItemAppetite):
    __slots__ = ('_sip', '_speed')

    requirement = _(u'alcoholic drinks or {water}').format(
        water = WaterDrinking.requirement)
    sating = _(u'drinking')
    stocktype = Drinks
    itemtype = Beverage
    fortification = 15 

    def __init__(self, creature, sip):
        Appetite.__init__(self, creature, 3600) # once a month
        self._sip = sip
        
        self._speed = creature.speed
        creature.speed = self.speed

    def speed(self):
        return self._speed() + (1 if self._pentup > self._threshold else 0)

    def consume(self, world):            
        vessel = self._creature.inventory.find(lambda item:
                                     hasattr(item, 'has') and
                                     item.has(Beverage))

        if vessel:
            bev = vessel.find(lambda item: isinstance(item, Beverage))
            
            while not self.sated:
                yield _(u'{consuming} {drink}').format(
                    consuming=self.sating, drink=bev.description())

                sip = min(bev.materials[0].amount, self._sip)
                bev.materials[0].amount -= sip
                
                if not bev.materials[0].amount:
                    vessel.remove(bev)
                    break

                self.slake(self.fortification * sip / self._sip *
                           self._creature.speed())

            for step in stashitem(self._creature, world, vessel):
                yield step

class Creature(Thing):
    __slots__ = (
        'activity',
        'attributes',
        'color',
        'debug',
        'location',
        'inventory',
        'rest',
        '_remove',
        '_work',
        'appetites',
        'player',
        'labors',
        'speed',
        'strength',
        'skills'
        )
    
    def __init__(self, player, materials, color, location):
        Thing.__init__(self, materials)
        self.speed = self._speed
        self.strength = self._strength

        self.activity = _(u'revelling in the miracle of creation')
        self.attributes = sampleattributes(self.race)
        self.color = color
        self.location = location
        self.inventory = Storage(1.0)
        self.rest = random() * self.speed()
        self._remove = False
        self._work = None
        self.appetites = []
        self.player = player
        self.skills = SkillSet()
        self.labors = []

        if self.player:
            self.player.creaturecreated(self)

        self.debug = False

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

    def _die(self, world):
        self._remove = True
        world.additem(Corpse(self))

    def eyesight(self):
        return gauss(self.attributes[Sight],10) / 10

    def _speed(self): 
        return 2 - gauss(self.attributes[Speed],10) / 100

    def _strength(self):
        return gauss(self.attributes[Strength],10) / 100

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

    def appetitereport(self):
        stati = [status for status in
                 [appetite.status() for appetite in self.appetites]
                 if status]
        if stati:
            pronoun = self.subjectpronoun().capitalize()
            return ' '.join([_(u'{she} {hankers}.').format(she=pronoun,
                                                           hankers=status)
                             for status in stati])
        else:
            return None

    def inventoryreport(self):
        required = {}
        for labor in self.labors:
            if issubclass(labor, ToolLabor):
                for tool in labor.tools:
                    name, job = tool.noun, labor.noun
                    if name in required:
                        required[name].append(job)
                    else:
                        required[name] = [job]

        pronoun = self.subjectpronoun().capitalize()

        lines = []
        for item in self.inventory.contents:
            name = item.noun
            value = _(u'{he} is carrying {an} {item}').format(
                he=pronoun, an=indefinitearticle(name), item=name)
            if name in required:
                value += _(u' for {jobs}').format(
                    jobs=conjunction(required[name]))
                del required[name]
            value += '.'

            lines.append(value)

        for missing, jobs in required.iteritems():
            lines.append(_(u'{he} needs {a} {tool} for {jobs}.').format(
                he=pronoun, a=indefinitearticle(missing), tool=missing,
                jobs=conjunction(jobs)))

        return ' '.join(lines) if lines else None

    def _checkhealth(self, world):
        if self.health <= 0:
            self._die(world)

    def feedappetites(self, world):
        for appetite in self.appetites:
            for step in appetite.pursue(world):
                yield step

    def performassignments(self, world):
        if not self.player:
            return

        for labor in self.labors:
            for step in labor.toil(self, world):
                yield step

    def work(self, world):
        while True:
            for step in self.feedappetites(world):
                yield step

            for step in self.performassignments(world):
                yield step

            yield meander(self, world)
            
    def step(self, world, dt):
        if self.debug:
            set_trace()
        
        for app in self.appetites:
            app.step(dt)
        
        self._checkhealth(world)

        if not self._work:
            self._work = self.work(world)
            
        self.activity = next(self._work)
            
        self.rest += self.speed()

        return self._remove

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
    
    def __init__(self, player, materials, color, location, sex):
        Creature.__init__(self, player, materials, color, location)
        self.sex = sex

    def sexdescription(self):
        return self.sex.description

class CulturedCreature(SexualCreature):
    __slots__ = 'gender', 'name'

    def __init__(self, player, materials, color, location):
        self.name = self.culture[NameSource].generate()
        
        if random() < self.culture[Maleness]:
            sex = Male
            self.gender = Woman if random() < self.culture[MaleWomen] else Man
        else:
            sex = Female
            self.gender = Man if random() < self.culture[FemaleMen] else Woman

        SexualCreature.__init__(self, player, materials, color, location, sex)

        for p, appetite in self.culture[Appetites]:
            if random() < p:
                self.appetites.append(appetite(self))

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

class Appetites(object):
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
        NameSource : NameGenerator('fr.txt', 2),
        Appetites : []
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
        NameSource : NameGenerator('fi.txt', 2),
        Appetites : []
        }

class Dwarf(CulturedCreature):
    __slots__ = ()

    noun = _(u'dwarf')
    health = 10
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
        NameSource : NameGenerator('gd.txt', 2),
        Appetites : [(1.0, lambda c: BoozeDrinking(c, 0.0001))]
        }
    
    def __init__(self, player, location):
        r = randint(80,255)
        CulturedCreature.__init__(self, player, [Material(Meat, 0.075)],
                                  (r, r-40, r-80), location)
        self.labors = [Mining, Woodcutting, Stockpiling, Furnishing, Carpentry, Masonry]

    def colordescription(self):
        return _(u'has {hue} skin').format(hue=describecolor(self.color))
        
class Goblin(CulturedCreature):
    __slots__ = ()
    
    noun = _(u'goblin')
    health = 0
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
        NameSource : NameGenerator('no.txt', 1),
        Appetites : []
        }
    
    def __init__(self, player, location):
        CulturedCreature.__init__(self, player, [Material(Meat, 0.05)],
                                  (32, 64+randint(0,127),64+randint(0,127)),
                                  location)

    def colordescription(self):
        return _(u'has {hue} skin').format(hue=describecolor(self.color))

class Tortoise(SexualCreature):
    __slots__ = ()
    
    health = 10
    noun = _(u'giant tortoise')
    race = {
        Strength : 120,
        Speed : 20,
        Sight : 20,
        Hearing : 100,
        Smell : 100,
        Dexterity : 20,
        Toughness : 120
        }
    
    def __init__(self, player, location):
        d = randint(-20,10)
        SexualCreature.__init__(self, player, [Material(Meat, 0.3)],
                                (188+d,168+d,138+d), location,
                                choice([Male,Female]))
        
    def colordescription(self):
        return _(u'has a shell tinted {hue}').format(
            hue=describecolor(self.color))
        
class SmallSpider(SexualCreature):
    __slots__ = ()
    
    noun = _(u'spider')
    health = 10
    race = {
        Strength : 20,
        Speed : 180,
        Sight : 20,
        Hearing : 20,
        Smell : 20,
        Dexterity : 180,
        Toughness : 20
        }
    
    def __init__(self, player, location):
        SexualCreature.__init__(self, player, [Material(Meat, 0.0001)],
                                (95, randint(0,40), 0), location,
                                choice([Male,Female]))

    def colordescription(self):
        color = describecolor(self.color)
        return _(u'has {a} {hue} body').format(a=indefinitearticle(color),
                                              hue=color)

class HistoricalEvent(object):
    def __init__(self, event, location):
        self.event = event
        self.location = location

    @property
    def description(self):
        return self.event

class PerpetratedEvent(HistoricalEvent):
    def __init__(self, perpetrators, event, location):
        HistoricalEvent.__init__(self, event, location)
        self.perpetrators = perpetrators

    @property
    def description(self):
        return _(u'{people} {acted}').format(
            people=conjunction([p.namecard() for p in self.perpetrators]),
            acted=super(PerpetratedEvent, self).description)

class ObjectEvent(PerpetratedEvent):
    def __init__(self, perpetrators, objects, event, location):
        PerpetratedEvent.__init__(self, perpetrators, event, location)
        self.objects = objects

    @property
    def description(self):
        return _(u'{acted} the {objects}',
                 acted = super(ObjectEvent, self).description,
                 objects = conjunction(self.objects))

## {{{ http://code.activestate.com/recipes/576888/ (r10)
def ordinal(value):

    if value % 100//10 != 1:
        if value % 10 == 1:
            ordval = u"%d%s" % (value, "st")
        elif value % 10 == 2:
            ordval = u"%d%s" % (value, "nd")
        elif value % 10 == 3:
            ordval = u"%d%s" % (value, "rd")
        else:
            ordval = u"%d%s" % (value, "th")
    else:
        ordval = u"%d%s" % (value, "th")

    return ordval

class MilestoneEvent(ObjectEvent):
    def __init__(self, perpetrators, objects, number, event, location):
        ObjectEvent.__init__(self, perpetrators, objects, event, location)
        self.number = number

    @property
    def description(self):
        return _(u'{acted} the {nth} {objects}').format(
            acted = super(ObjectEvent, self).description,
            nth = ordinal(self.number),
            objects = conjunction(self.objects))

class History(object):
    def __init__(self, world):
        self._world = world
        self._crier = None
        self.events = []

    def record(self, event):
        self.events.append((self._world.time, event))
        if self._crier:
            self._crier(event)

    def setcrier(self, crier):
        self._crier = crier

class Player(object):
    def __init__(self, world):
        self._world = world
        self.creatures = []
        self.digjobs = deque()
        self.felljobs = deque()
        self.stockjobs = {}
        self.furnishjobs = deque()
        self.mined = 0
        self.felled = 0
        self.history = History(self._world)
        self.settlement = None
        self._furniturelocations = {}
        self._furnituretypes = {}

        self._world.registerplayer(self)

    def creaturecreated(self, creature):
        self.creatures.append(creature)

    def foundsettlement(self, name):
        self.settlement = name

        self.history.record(PerpetratedEvent([c for c in self.creatures],
                                             _(u'established the settlement'),
                                             None))

    def recordmined(self, location, miner, substance):
        if self.mined == 0:
            self.history.record(MilestoneEvent([miner],
                                               [Stone.noun],
                                               1,
                                               _(u'mined'),
                                               location))
        self.mined += 1

    def recordfelled(self, tree, feller):
        if self.felled == 0:
            self.history.record(MilestoneEvent([feller],
                                               [tree.description],
                                               1,
                                               _(u'felled'),
                                               tree.location))
        self.felled += 1

    def describesettlement(self, time):
        return _(u'the fledgling {settlement}').format(settlement=settlement)
                                 
    def designatefordigging(self, location):
        tile = self._world.space[location]
        if isinstance(tile, Earth):
            tile.designation = self
            if (tile.revealed or
                isinstance(self._world.space[location[0:2] + (location[2]+1,)],
                           Floor)):
                self.digjobs.append(location)
            self._world.space.changed = True

    def felltree(self, location, direction):
        trunk = self._world.space[location]
        if isinstance(trunk, TreeTrunk):
            trunk.tree.fell = direction
            self.felljobs.append(trunk.tree)

    def unstockpileditems(self, itemtype):
        if itemtype.subtypes:
            return [item
                    for subtype in itemtype.subtypes
                    for item in self.unstockpileditems(subtype)]
        else:
            try:
                jobs = self.stockjobs[itemtype]
            except KeyError:
                return []
            
            if not jobs[0]:
                return [item for item in jobs[1]]
        return []

    def addstockpile(self, stockpile):
        for t in stockpile.types:
            try:
                self.stockjobs[t][0].append(stockpile)
            except KeyError:
                self.stockjobs[t] = deque([stockpile]), deque()

        for location in stockpile.region:
            self._world.space[location].addstockpile(self, stockpile)
                
        self._world.stockpiles.append(stockpile)

        self._world.space.changed = True

    def getstockpiles(self, itemtype):
        if itemtype.subtypes:
            return [pile
                    for subtype in itemtype.subtypes
                    for pile in self.getstockpiles(subtype)]
        else:
            try:
                piles = self.stockjobs[itemtype][0]
            except KeyError:
                return []
            
            return [pile for pile in piles]

    def addtostockjobs(self, item):
        try:
            self.stockjobs[item.stocktype][1].append(item)
        except KeyError:
            self.stockjobs[item.stocktype] = deque(), deque([item])

    def removefromstockjobs(self, item):
        try:
            self.stockjobs[item.stocktype][1].remove(item)
        except ValueError, KeyError:
            pass

    def furnish(self, location, item):
        self.furnishjobs.append((location, item))

    def furnished(self, location):
        furnishing = self._world.space[location].furnishing
        self._furniturelocations[location] = furnishing
        if not furnishing.__class__ in self._furnituretypes:
            self._furnituretypes[furnishing.__class__] = [location]
        else:
            self._furnituretypes[furnishing.__class__].append(location)

    def furniture(self, furnituretype):
        locations = (self._furnituretypes[furnituretype]
                     if furnituretype in self._furnituretypes
                     else [])
        return [(loc, self._world.space[loc].furnishing)
                for loc in locations]

class FallingObject(object):
    def __init__(self, item, speed):
        self.item = item
        self.position = 0
        self.speed = speed
        self.rest = 0

    def step(self, world, dt):
        self.position += self.speed
        self.speed += 0.1
        dz = int(self.position)
        if dz:
            world.removeitem(self.item)
            done = False
            for z in range(dz):
                if isinstance(world.space[self.item.location[0:2] +
                                          (self.item.location[2]-z,)], Floor):
                    done = True
                    break
            else:
                z = dz
            self.item.location = (self.item.location[0:2] +
                                  (self.item.location[2]-z,))
            world.additem(self.item)
            if done:
                world.makesound(Fall, self.item.location)
                return True

            self.position -= dz

        self.rest = 0
        return False

class FallingTree(object):
    def __init__(self, tree, direction):
        self.tree = tree
        self.direction = direction
        self.rest = 0
        self.angle = 0
        self.speed = pi/180

    def _trunkoffset(self, i):
        offset = [int(i * f(self.angle) + 0.5) for f in sin, cos]
        loc = self.tree.location[0:2] + (self.tree.location[2]+offset[1],)
        return reduce(Direction.move, (self.direction,) * offset[0], loc)

    def _placewood(self, world, location):
        while not world.space[location].is_passable():
            if location[2] == world.space.dim[2]-1:
                return

            location = location[0:2] + (location[2]+1,)

        material = LooseMaterial(self.tree.wood, location)
        world.additem(material)

        if not isinstance(world.space[location], Floor):
            world.schedule(FallingObject(material, 0))

    def _clear(self, world, location):
        if location[2] and not isinstance(world.space[location[0:2] + (location[2]-1,)],
                                          Earth):
            tile = Empty()
        else:
            tile = Floor(randint(0,3))
        world.space[location] = tile

    def _advanceangle(self, world):        
        self.angle += self.speed
        self.speed += sin(self.angle)/10

        if self.angle > pi/2:
            for i in range(len(self.tree.trunk)):
                if self.tree.trunk[i] is None:
                    continue

                self._clear(world, self.tree.trunk[i])
                self._placewood(world, self.tree.trunk[i])
            return True
        
        return False

    def _nextlocs(self, world):
        locs = [None for i in self.tree.trunk]
        for i in range(len(self.tree.trunk)):
            if self.tree.trunk[i] is None:
                continue

            loc = self._trunkoffset(i)

            if loc != self.tree.trunk[i] and not world.space[loc].is_passable():
                self._placewood(world, loc)
                locs[i] = None
            else:
                locs[i] = loc
        return locs

    def _movetrunks(self, world, locs):
        for i in range(len(self.tree.trunk)):
            if self.tree.trunk[i] is None:
                continue

            self._clear(world, self.tree.trunk[i])
            self.tree.trunk[i] = locs[i]
            
            if self.tree.trunk[i] is not None:
                world.space[self.tree.trunk[i]] = TreeTrunk(self.tree)

        world.space.changed = True

    def step(self, world, dt):
        if not self.angle:
            for loc in self.tree.branches + self.tree.leaves:
                world.space[loc] = Empty()

        if self._advanceangle(world):
            return True

        locs = self._nextlocs(world)

        self._movetrunks(world, locs)

        self.rest = 0
        return all([t is None for t in self.tree.trunk])

class LiquidPhysics(object):
    def __init__(self, world):
        self._world = world
        self._items = []

    def add(self, item):
        self._items.append(item)

    def remove(self, item):
        self._items.remove(item)

    def step(self):
        static = []
        for liquid in self._items:
            tile = self._world.space[liquid.location]
            if tile.downhill is None:
                down = [a for a in
                        self._world.space.pathing.open_adjacent(liquid.location)
                        if a[2] < liquid.location[2]]
                if not down:
                    tile.downhill = 0, None
                else:
                    downhill = sorted(down, key=lambda loc: loc[2])[0]
                    tile.downhill = liquid.location[2] - downhill[2], downhill

            if tile.downhill[0]:
                downhill = self._world.space[tile.downhill[1]]

                if downhill.liquid:
                    tile.liquid = liquid.materials[0].substance
                    self._world.space.changed = True
                    static.append(liquid)
                else:
                    tile.items.remove(liquid)
                    liquid.location = tile.downhill[1]
                    downhill.items.append(liquid)
            else:
                tile.liquid = liquid.materials[0].substance
                self._world.space.changed = True
                static.append(liquid)

        for liquid in static:
            self._world.removeitem(liquid)
        
class World(object):
    def __init__(self, space, schedule):
        self.space = space
        self.schedule = schedule
        self.items = []
        self.creatures = []
        self.stockpiles = []
        self._liquids = LiquidPhysics(self)
        self._listener = None
        self._players = []
        self.time = 0

    def liquids(self):
        self._liquids.step()

    def registerplayer(self, player):
        self._players.append(player)

    def forgetplayer(self, player):
        self._players.remove(player)

    def addsoundlistener(self, listener):
        self._listener = listener

    def makesound(self, sound, location):
        if self._listener:
            self._listener.play(sound, location)

    def movecreature(self, creature, location):
        sound = bool(location[2]-creature.location[2])
        self.space[creature.location].creatures.remove(creature)
        creature.location = location
        self.space[creature.location].creatures.append(creature)
        if sound:
            self.makesound(Step, creature.location)

    def dig(self, location, miner):
        tile = self.space[location]
        designation = tile.designation
        substance = tile.substance
        self.makesound(substance.sound, location)

        if (location[2] and
            self.space[location[0:2] + (location[2]-1,)].is_passable()):
            tile = Empty()
        else:
            tile = Floor(randint(0,3))

            abovelocation = location[0:2] + (location[2]+1,)
            above = self.space[abovelocation]
            if isinstance(above, Floor):
                tile.items = above.items
                tile.creatures = above.creatures
                for item in tile.items:
                    item.location = location
                for creature in tile.creatures:
                    creature.location = location
                    
                self.space[abovelocation] = Empty()
        tile.revealed = True
        for x,y in self.space.pathing.adjacent_xy(location[0:2]):
            nloc = x, y, location[2]
            n = self.space[nloc]
            if not n.revealed:
                n.revealed = True
                if n.designation and n.designation == designation:
                    n.designation.digjobs.append(nloc)
        if location[2]:
            bloc = location[0:2] + (location[2]-1,)
            b = self.space[bloc]
            if not b.revealed and b.designation and b.designation == designation:
                b.designation.digjobs.append(bloc)

        self.space[location] = tile
        self.additem(LooseMaterial(substance, location))

        if miner.player and issubclass(substance, Stone):
            miner.player.recordmined(location, miner, substance)

    def collapsetree(self, feller, tree, direction):
        self.schedule(FallingTree(tree, direction))

        if feller and feller.player:
            feller.player.recordfelled(tree, feller)
                            
    def additem(self, item, stockpiled = None):
        if item.location is not None:
            self.space[item.location].items.append(item)

        if isinstance(item, Liquid):
            self._liquids.add(item)

        for player in self._players:
            player.addtostockjobs(item)
            
        self.items.append(item)

    def removeitem(self, item, stockpiled = None):
        if item.location is not None:
            self.space[item.location].items.remove(item)

        if isinstance(item, Liquid):
            self._liquids.remove(item)

        if not stockpiled:
            for player in self._players:
                player.removefromstockjobs(item)
            
        self.items.remove(item)

    def setfurnishing(self, location, item, player):
        tile = self.space[location]
        if not hasattr(tile, 'furnishing') or tile.furnishing:
            raise ValueError

        item.location = location
        tile.furnishing = item

        player.furnished(location)

        self.space.changed = True
