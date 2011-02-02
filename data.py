from codecs import open as openunicode
from collections import deque
from random import choice, gauss, randint, random
from re import search
from unicodedata import name as unicodename

from colordb import match as describecolor
from space import Earth, Empty
from substances import Meat, Water
from language import Generator
from sound import Dig, Fight, Mine, Step

class Material(object):
    __slots__ = 'substance', 'amount'
    
    def __init__(self, substance, amount):
        self.substance = substance
        self.amount = amount

    def mass(self):
        return self.substance.density * self.amount

class Entity(object):
    pass

class Thing(Entity):
    __slots__ = 'materials',

    fluid = False
    
    def __init__(self, materials):
        self.materials = materials

    def volume(self):
        return sum([m.amount for m in self.materials])

    def mass(self):
        return sum([m.mass() for m in self.materials])

class StockpileType(object):
    def __init__(self, description, subtypes = None):
        self.description = description
        self.subtypes = subtypes if subtypes else []

class Beverage(Thing):
    __slots__ = ()
    
    fluid = True
    
    def __init__(self, amount):
        Thing.__init__(self, [Material(Water, amount)])

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
    
    def __init__(self, materials, location):
        Thing.__init__(self, materials)
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
        Item.__init__(self, creature.materials, creature.location)
        self.origins = creature

    def description(self):
        return _('corpse of {0}').format(self.origins.description())

class Barrel(Container):
    __slots__ = ()

    noun = _('barrel')
    
    containerstocktype = StockpileType(_('Empty barrel'))
    
    def __init__(self, location, substance):
        Container.__init__(self,
                           [Material(substance, 0.075)], location, 0.25)
        self.contents.append(Wine(self.capacity))

Arms = StockpileType(_('Weapons and armor'), [])
BuildingMaterials = StockpileType(_('Building materials'), [])
Clothing = StockpileType(_('Clothing'), [])
Drinks = StockpileType(_('Drink'), [Wine.stocktype])
Food = StockpileType(_('Food'), [])
Furniture = StockpileType(_('Furnishings'), [])
Products = StockpileType(_('Trade products and supplies'),
                         [Barrel.containerstocktype])
Refuse = StockpileType(_('Refuse'), [Corpse.stocktype])
Resources = StockpileType(_('Raw materials'), [])
Tools = StockpileType(_('Tools and equipment'), [])

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

class Appetite(object):
    __slots__ = '_pentup', '_creature', '_threshold'

    stocktype = None
    itemtype = None    

    def __init__(self, creature, threshold):
        self._creature = creature
        self._threshold = threshold
        self._pentup = randint(self._threshold/2, self._threshold)

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

        yield _('looking for {desire}').format(desire=self.requirement)

        for step in self.attempt(world):
            yield step

class SexualRelease(Appetite):
    __slots__ = ()
    
    requirement = _('physical intimacy')

class Socialization(Appetite):
    __slots__ = ()

    requirement = _('fellowship')

class WaterDrinking(Appetite):
    __slots__ = ()

    requirement = _('potable water')

class ItemAppetite(Appetite):
    __slots__ = ()
    
    def attempt(self, world):
        for step in self._creature.acquireitem(world,
                                               self.stocktype,
                                               self.itemtype):
            yield step

        for step in self.consume(world):
            yield step

class BoozeDrinking(ItemAppetite):
    __slots__ = ('_sip')

    requirement = _('alcoholic drinks or {water}').format(
        water = WaterDrinking.requirement)
    sating = _('drinking')
    stocktype = Drinks
    itemtype = Beverage
    fortification = 15 

    def __init__(self, creature, sip):
        Appetite.__init__(self, creature, 3600) # once a month
        self._sip = sip

    def consume(self, world):            
        vessel = self._creature.inventory.find(lambda item:
                                     hasattr(item, 'has') and
                                     item.has(Beverage))

        if vessel:
            bev = vessel.find(lambda item: isinstance(item, Beverage))
            
            while not self.sated:
                yield _('{consuming} {drink}').format(
                    consuming=self.sating, drink=bev.description())

                sip = min(bev.materials[0].amount, self._sip)
                bev.materials[0].amount -= sip
                
                if not bev.materials[0].amount:
                    vessel.remove(bev)
                    break

                self.slake(self.fortification * sip / self._sip *
                           self._creature.speed())

            for step in self._creature.stashitem(world, vessel):
                yield step

class Creature(Thing):
    __slots__ = (
        'activity',
        'attributes',
        'color',
        'location',
        'inventory',
        'rest',
        '_remove',
        '_work',
        'appetites'
        )
    
    def __init__(self, materials, color, location):
        Thing.__init__(self, materials)
        self.activity = _('revelling in the miracle of creation')
        self.attributes = sampleattributes(self.race)
        self.color = color
        self.location = location
        self.inventory = Storage(1.0)
        self.rest = random() * self.speed()
        self._remove = False
        self._work = None
        self.appetites = []

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

    def _checkhealth(self, world):
        if self.health <= 0:
            self._die(world)

    def pathto(self, world, goal):
        steps = 256
        
        p1 = world.space.pathing.path_op(self.location, goal)
        p2 = world.space.pathing.path_op(goal, self.location)

        path = None
        while True:
            yield _('plotting course'), path
            
            if not p1.done and not p2.done:
                p1.iterate(steps)
                p2.iterate(steps)
                continue

            if p1.done:
                path = p1.path
            elif p2.path is not None:
                path = p2.path[::-1][1:] + [goal]

    def goto(self, world, goal):
        for step, path in self.pathto(world, goal):
            yield step
            if path:
                for location in path:
                    yield _('travelling')
                    world.movecreature(self, location)
                break

    def takeitem(self, world, item):
        item.reserved = True
        for step in self.goto(world, item.location):
            yield _('{going} to {item}').format(
                going=step, item=item.description())

        if self.location != item.location:
            return
        
        yield _('picking up {item}').format(item=item.description())
        item.reserved = False
        world.removeitem(item)
        self.inventory.add(item)

    def acquireitem(self, world, stocktype, itemtype):
        for pile in world.getstockpiles(stocktype):
            if pile.has(itemtype):
                for step in self.takefromstockpile(world, pile, itemtype):
                    yield step
                if self.inventory.has(itemtype):
                    break
        else:
            for item in world.unstockpileditems(stocktype):
                if not item.reserved:
                    for step in self.takeitem(world, item):
                        yield step
                if self.inventory.has(itemtype):
                    break

    def discarditem(self, world, item):
        yield _('discarding {item}').format(item=item.description())
        self.inventory.remove(item)
        world.additem(item)

    def stashitem(self, world, item):
        for pile in world.getstockpiles(item.stocktype):
            if pile.space():
                for step in self.storeinstockpile(world, pile, item):
                    yield step
                break
        else:
            for step in self.discarditem(world, item):
                yield step

    def feedappetites(self, world):
        for appetite in self.appetites:
            for step in appetite.pursue(world):
                yield step

    def meander(self, world):
        adjacent = world.space.pathing.open_adjacent(self.location)
        if len(adjacent) > 0:
            world.movecreature(self, choice([a for a in adjacent]))
        
        return _('idling')

    def work(self, world):
        while True:
            for step in self.feedappetites(world):
                yield step

            yield self.meander(world)
            
    def step(self, world, dt):
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
    
    def __init__(self, materials, color, location, sex):
        Creature.__init__(self, materials, color, location)
        self.sex = sex

    def sexdescription(self):
        return self.sex.description

class CulturedCreature(SexualCreature):
    __slots__ = 'gender', 'name'

    def __init__(self, materials, color, location):
        self.name = self.culture[NameSource].generate()
        
        if random() < self.culture[Maleness]:
            sex = Male
            self.gender = Woman if random() < self.culture[MaleWomen] else Man
        else:
            sex = Female
            self.gender = Man if random() < self.culture[FemaleMen] else Woman

        SexualCreature.__init__(self, materials, color, location, sex)

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
    
    def __init__(self, location):
        r = randint(80,255)
        CulturedCreature.__init__(self, [Material(Meat, 0.075)],
                                  (r, r-40, r-80), location)

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
    
    def __init__(self, location):
        CulturedCreature.__init__(self, [Material(Meat, 0.05)],
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
    
    def __init__(self, location):
        d = randint(-20,10)
        SexualCreature.__init__(self, [Material(Meat, 0.3)],
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
    
    def __init__(self, location):
        SexualCreature.__init__(self, [Material(Meat, 0.0001)],
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
        self._listener = None

    def addsoundlistener(self, listener):
        self._listener = listener

    def designatefordigging(self, location):
        tile = self.space[location]
        if isinstance(tile, Earth):
            tile.designated = True
            if (tile.revealed or
                isinstance(self.space[location[0:2] + (location[2]+1,)], Empty)):
                self.digjobs.append(location)
            self.space.changed = True

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

    def dig(self, location):
        self.makesound(self.space[location].substance.sound, location)
            
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

    def getstockpiles(self, itemtype):
        if itemtype.subtypes:
            for subtype in itemtype.subtypes:
                for pile in self.getstockpiles(subtype):
                    yield pile
        else:
            try:
                piles = self.stockjobs[itemtype][0]
            except KeyError:
                return
            
            for pile in piles:
                yield pile
            
    def additem(self, item, stockpiled = None):
        if item.location is not None:
            self.space[item.location].items.append(item)

        if not stockpiled:
            try:
                self.addtostockjobs(item)
            except KeyError:
                self.stockjobs[item.stocktype] = deque(), deque([item])
            
        self.items.append(item)

    def unstockpileditems(self, itemtype):
        if itemtype.subtypes:
            for subtype in itemtype.subtypes:
                for item in self.unstockpileditems(subtype):
                    yield item
        else:
            try:
                jobs = self.stockjobs[itemtype]
            except KeyError:
                return
            
            if not jobs[0]:
                for item in jobs[1]:
                    yield item
                
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
