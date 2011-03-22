from random import choice, randint, random

from colordb import match as describecolor
from data import conjunction, indefinitearticle, isvowel, NameGenerator

class Attribute(object):
    def __init__(self, value):
        self.value = value

class Characteristic(object):
    def __init__(self, attributes):
        self.attributes = [a for a in attributes]
        
    def noun(self):
        return _(u'an unknown characteristic')

    def definite(self):
        return self.noun()

    def indefinite(self):
        return self.noun()

    def adjective(self):
        return _(u'with {noun}').format(noun=self.noun())

class Nose(Characteristic):
    def __init__(self, attributes):
        Characteristic.__init__(self, attributes)

    @property
    def width(self):
        return self.attributes[0].value

    @property
    def length(self):
        return self.attributes[1].value

    def noun(self):
        if self.width < 0.33:
            if self.length < 0.33:
                return _(u'button nose')
            elif self.length > 0.67:
                return _(u'pointy nose')
            else:
                return _(u'narrow nose')
        elif self.width > 0.67:
            if self.length < 0.33:
                return _(u'flat nose')
            elif self.length > 0.67:
                return _(u'large nose')
            else:
                return _(u'broad nose')
        else:
            if self.length < 0.33:
                return _(u'short nose')
            elif self.length > 0.67:
                return _(u'long nose')
            else:
                return None

    def definite(self):
        if noun:
            return u' '.join(indefinitearticle(noun), noun)
        else:
            return None

    def indefinite(self):
        noun = self.noun()
        if noun:
            return noun + u's'
        else:
            return None

    def adjective(self):
        noun = self.noun()
        if noun:
            return noun + u'd'
        else:
            return None

class Skin(Characteristic):
    def __init__(self, attributes):
        Characteristic.__init__(self, attributes)

    @property
    def color(self):
        return tuple([c.value for c in self.attributes])

    def noun(self):
        return _(u'{hue} skin').format(hue=describecolor(self.color))

    def adjective(self):
        return self.noun() + u'ned'

class NaturalResource(object):
    def __init__(self, amount):
        self.amount = amount

    def adjective(self):
        if self.amount < 0.125:
            return _(u'scant')
        elif self.amount < 0.25:
            return _(u'some quantity of')
        elif self.amount < 0.75:
            return _(u'a moderate amount of')
        elif self.amount < 0.875:
            return _(u'a considerable amount of')
        else:
            return _(u'bounteous')

class FoodSource(NaturalResource):
    def __init__(self, name, amount):
        NaturalResource.__init__(self, amount)
        self.name = name

    def description(self):
        return _(u'{amountof} {food}').format(amountof=self.adjective(),
                                              food=self.name)

class FreshWater(NaturalResource):
    def __init__(self, name, amount):
        NaturalResource.__init__(self, amount)
        self.name = name

    def description(self):
        return _(u'{amountof} {water}').format(amountof=self.adjective(),
                                               water=self.name)

class TradeGood(NaturalResource):
    def __init__(self, name, amount):
        NaturalResource.__init__(self, amount)
        self.name = name

    def description(self):
        return _(u'{amountof} {good}').format(amountof=self.adjective(),
                                              good=self.name)

class Region(object):
    def __init__(self, size, resources):
        self.size = size
        self.resources = resources

    def sizedescription(self):
        if self.size < 10000:
            return _(u'tiny')
        elif self.size < 50000:
            return None
        else:
            return _(u'sprawling')

    def resourcedescription(self, name):
        land = u''
        for kind, label in [(FoodSource, _(u'food sources')),
                            (FreshWater, _(u'fresh water')),
                            (TradeGood, _(u'trade goods'))]:
            sources = [r for r in self.resources if isinstance(r, kind)]

            if not sources:
                land = u' '.join([land, _(u'{place} has little in the way of {resource}.').format(
                    place=name, resource=label)])
                continue
            
            summary = conjunction([s.description() for s in sources])
            
            amount = sum([s.amount for s in sources])
            if amount < 0.75:
                summary = _(u'With but {sources}, {place} has only limited {resource}.').format(
                    sources=summary, place=name, resource=label)
            elif amount > 2.25:
                summary = _(u'With {sources}, {place} is blessed with an abundance of {resource}.').format(
                    sources=summary, place=name, resource=label)
            else:
                summary = _(u'{place} has {sources}.').format(
                    sources=summary, place=name)

            land = u' '.join([land, summary])

        return land
    
class Ethnicity(object):
    def __init__(self, lang):
        name = NameGenerator(lang, 2 if random() < 0.1 else 1).generate()

        self.noun = name.title()
        if isvowel(self.noun[-1]):
            self.adjective = (self.noun[:-1]
                              if len(self.noun) > 1
                              else self.noun) + _(u'an')
            self.plural = self.adjective + _(u's')
        else:
            self.adjective = self.noun + _(u'ish')
            self.plural = self.adjective
        
        r = randint(80,225)
        self.characteristics = [Skin([Attribute(r),
                                      Attribute(r-40),
                                      Attribute(r-80)]),
                                Nose([Attribute(random()),
                                      Attribute(random())])]

        water = random() > 0.25
        resources = [FoodSource(_(u'food crops'), random()),
                     FoodSource(_(u'grazable land'), random()),
                     FreshWater(_(u'rainfall'), random()),
                     FreshWater(_(u'natural spring water'), random())]

        if water:
            source = FreshWater(_(u'rivers and lakes'), random())
            resources.append(source)
            resources.append(FoodSource(_(u'seafood'), source.amount * random()))

        for t in _(u'spice crops'), _(u'timber'), _(u'precious metals'):
            if random() > 0.5:
                resources.append(TradeGood(t, random()))

        self.region = (NameGenerator(lang, 2 if random() < 0.1 else 1).generate(),
                       Region(75000*random(), resources))

    def description(self, fraction = None):
        people = _(u'The {culture} people').format(culture=self.adjective)
        if fraction is not None:
            people += _(u' constitute {proportion}% of the population and').format(
                proportion = int(100 * fraction))
        
        land = _(u'land')
        size = self.region[1].sizedescription()
        if size:
            land = u' '.join([size, land])
        land = _(u'{People} originated in the {land} known to them as {name}.').format(
            People=people, land=land, name=self.region[0])

        land = land + self.region[1].resourcedescription(self.region[0])
        
        desc = []
        
        for c in self.characteristics:
            noun = c.indefinite()
            if noun:
                desc.append(noun)

        physical = _(u'Physically, the {members} have {characteristics}.').format(
            members = self.plural,
            characteristics = conjunction(desc))

        return u'\n\n'.join([land, physical])

class Culture(object):
    def __init__(self):
        lang = choice(['cs','fi','fr','gd','nl','no']) + '.txt'
        
        self.ethnicities = []

        remaining = 1.0
        while remaining:
            prop = remaining/2 + random() * remaining/2
            if prop < 0.1 or prop > 0.85 * remaining:
                prop = remaining
            if self.ethnicities:
                ethnicity = prop, Ethnicity(choice(['cs','fi','fr','gd','nl','no']) + '.txt')
            else:
                ethnicity = prop, Ethnicity(lang)
            self.ethnicities.append(ethnicity)
            remaining -= prop

        if len(self.ethnicities) == 1:
            self.noun = self.ethnicities[0][1].noun
            self.adjective = self.ethnicities[0][1].adjective
            self.plural = self.ethnicities[0][1].plural
        else:
            name = NameGenerator(lang, 2 if random() < 0.1 else 1).generate()

            self.noun = name.title()
            if isvowel(self.noun[-1]):
                self.adjective = (self.noun[:-1]
                                  if len(self.noun) > 1
                                  else self.noun) + _(u'an')
                self.plural = self.adjective + _(u's')
            else:
                self.adjective = self.noun + _(u'ish')
                self.plural = self.adjective

    def description(self):
        name = _(u'The culture of {name}.').format(name=self.noun)

        if len(self.ethnicities) == 1:
            ethnicity = '\n\n'.join(
                [_(u'The {people} are ethnically homogeneous.').format(
                    people=self.plural),
                 self.ethnicities[0][1].description()])
        else:
            ethnicity = '\n\n'.join(
                [_(u'The {cultural} population is made up of people of the {ethnic} ethnicities.').format(
                    cultural=self.adjective,
                    ethnic=conjunction([e[1].adjective for e in self.ethnicities]))] +
                [e[1].description(e[0]) for e in self.ethnicities])

        return '\n\n'.join([name, ethnicity])
