from random import choice, random

from data import indefinitearticle, isvowel, NameGenerator

class Culture(object):
    def __init__(self):
        name = NameGenerator(choice(['cs','fi','fr','gd','nl','no']) + '.txt',
                             2 if random() < 0.1 else 1).generate()
        
        self.noun = name.title()
        if isvowel(self.noun[-1]):
            self.adjective = (self.noun[:-1]
                              if len(self.noun) > 1
                              else self.noun) + _(u'an')
        else:
            self.adjective = self.noun + _(u'ish')

    def description(self):
        return _(u'The culture of {name}.').format(name=self.noun)
