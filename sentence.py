from random import choice, randint, random

class Word(object):
    def __str__(self):
        return self.root

class Noun(Word):
    def __init__(self, root):
        self.root = root

class Adjective(Word):
    def __init__(self, root):
        self.root = root

class Verb(Word):
    def __init__(self, root, transitive):
        self.root = root
        self.transitive = transitive

class Phrase(object):
    def __init__(self, head):
        self.head = head
        self.complements = []

    def __str__(self):
        return '-'.join([str(w) for w in self.complements + [self.head]])

class NounPhrase(Phrase):
    def __init__(self, head, definite, count):
        Phrase.__init__(self, head)
        self.definite = definite
        self.count = count

    def __str__(self):
        return '-'.join([str(w) for w in self.complements +
                         [('definite' if self.definite else 'indefinite') + ' ' +
                           str(self.head) + ' *' + str(self.count)]])

class Expression(object):
    def __init__(self, subject, verb, tense, obj = None):
        self.subject = subject
        self.verb = verb
        self.tense = tense
        self.obj = obj

    def __str__(self):
        return '\n'.join(('S: ' + str(self.subject),
                          'V: ' + str(self.verb)) +
                         (('O: ' + str(self.obj),) if self.obj else ()) +
                         (self.tense.__name__ + ' tense',))

nouns = [Noun(w) for w in 'dog','meal']

adjectives = [Adjective(w) for w in 'quick','great','hot']

verbs = [Verb(w,t) for (w,t) in ('follow', True),('walk', False)]

class Tense(object):
    pass

class Past(Tense):
    pass

class Present(Tense):
    pass

class Future(Tense):
    pass

tenses = Tense.__subclasses__()

def modify(phrase):
    while random() < 0.25:
        phrase.complements.append(modify(Phrase(choice(adjectives))))
    return phrase

action = choice(verbs)
if action.transitive:
    obj = modify(NounPhrase(choice(nouns), random() < 0.5, randint(1,5)))
else:
    obj = None
subject = modify(NounPhrase(choice(nouns), random() < 0.5, randint(1,5)))
verb = modify(Phrase(action))
tense = choice(tenses)

subject = NounPhrase(Noun('meal'), True, 2)
subject.complements = [Phrase(Adjective('quick'))]
subject.complements[0].complements = [Phrase(Adjective('hot')),
                                      Phrase(Adjective('great'))]
subject.complements[0].complements[1].complements = [Phrase(Adjective('hot'))]

verb = Phrase(Verb('follow', True))

obj = NounPhrase(Noun('dog'), True, 3)

tense = Present

e = Expression(subject, verb, tense, obj)
print e

class English(object):
    @classmethod
    def adverb(cls, phrase):
        return ' '.join([cls.adverb(c) for c in phrase.complements] +
                        [phrase.head.root + 'ly'])
    
    @classmethod
    def adjective(cls, phrase):
        return ' '.join([cls.adverb(c) for c in phrase.complements] +
                        [phrase.head.root])

    @classmethod
    def noun(cls, phrase):
        return ' '.join([cls.adjective(c) for c in phrase.complements] +
                        [phrase.head.root])

    @classmethod
    def decline(cls, phrase):
        plural = phrase.count > 1
        return ' '.join(['the' if phrase.definite else ('' if plural else 'a')] +
                        [cls.noun(phrase) + ('s' if plural else '')])
    
    @classmethod
    def subject(cls, expression):
        return cls.decline(expression.subject)

    @classmethod
    def obj(cls, expression):
        return cls.decline(expression.obj)

    @classmethod
    def conjugate(cls, verb, tense, count):
        return { Past : '{verb}ed',
                 Present : '{verb}s' if count == 1 else '{verb}',
                 Future : 'will {verb}' }[tense].format(verb=verb.head)

    @classmethod
    def verb(cls, expression):
        return ' '.join([cls.adverb(c) for c in expression.verb.complements] +
                        [cls.conjugate(expression.verb,
                                       expression.tense,
                                       expression.subject.count)])
                                
    @classmethod
    def translate(cls, expression):
        result = ' '.join([cls.subject(expression), cls.verb(expression)])
        if expression.verb.head.transitive:
            result += ' ' + cls.obj(expression)
        return result

print English.translate(e)

class Contraction(object):
    def __init__(self, affix, function):
        self.affix = affix
        self.function = function

    def __call__(self, root):
        return self.function(root, self.affix)

class Branch(object):
    @classmethod
    def affixer(cls, affix):
        return Contraction(affix, lambda h, a: cls.fuse(a, [h]))

    @classmethod
    def antifixer(cls, antifix):
        return Contraction(antifix, lambda h, a: cls.fuse(h, [a]))

    @classmethod
    def fuser(cls):
        return lambda h, m: cls.fuse(h, m)

class RightBranch(Branch):
    @classmethod
    def fuse(cls, head, modifiers):
        return ' '.join([head] + modifiers)

class LeftBranch(Branch):
    @classmethod
    def fuse(cls, head, modifiers):
        return ' '.join(modifiers + [head])

class WordOrder(object):
    pass

class SOV(WordOrder):
    branching = LeftBranch
    
    @classmethod
    def order(cls, subject, verb, obj = None):
        return ' '.join([subject] + ([obj] if obj else []) + [verb])

class SVO(WordOrder):
    branching = RightBranch
    
    @classmethod
    def order(cls, subject, verb, obj = None):
        return ' '.join([subject, verb] + ([obj] if obj else []))

class VSO(WordOrder):
    branching = RightBranch
    
    @classmethod
    def order(cls, subject, verb, obj = None):
        return ' '.join([verb, subject] + ([obj] if obj else []))

class Language(object):
    def __init__(self, order, pluralaffix, adverbaffix, definite, indefinite, tenses):
        self.order = order
        self.branching = self.order.branching

        self.formadj = None
        
        self.definite = definite
        self.indefinite = indefinite
        self.define = None
        self.indefine = None

        self.pluralaffix = pluralaffix
        self.pluralize = None

        self.formnoun = None
        
        self.tenses = tenses
        self.formtense = dict([(k, None) for k in self.tenses.keys()])

        self.advaffix = adverbaffix
        self.formadverb = None

    def adverb(self, phrase):
        formadverb = self.formadverb or self.branching.affixer(self.advaffix)
            
        return self.branching.fuse(formadverb(phrase.head.root),
                                   [self.adverb(c) for c in phrase.complements])
    
    def adjective(self, phrase):
        formadj = self.formadj or self.branching.fuser()
        
        return formadj(phrase.head.root,
                       [self.adverb(c) for c in phrase.complements])

    def noun(self, phrase):
        formnoun = self.formnoun or self.branching.fuser()
        
        return formnoun(phrase.head.root,
                        [self.adjective(c) for c in phrase.complements])

    def decline(self, phrase):
        pluralize = self.pluralize or self.branching.affixer(self.pluralaffix)
        define = self.define or self.branching.antifixer(self.definite)
        indefine = self.indefine or self.branching.antifixer(self.indefinite)
        
        plural = phrase.count > 1
        noun = pluralize(self.noun(phrase)) if plural else self.noun(phrase)
        defined = define(noun) if phrase.definite else indefine(noun)
        return pluralize(defined) if plural else defined
    
    def subject(self, expression):
        return self.decline(expression.subject)

    def obj(self, expression):
        return self.decline(expression.obj)

    def conjugate(self, verb, tense, count):
        formtense = self.formtense[tense] or self.branching.affixer(self.tenses[tense])

        return formtense(verb.head.root)        

    def verb(self, expression):
        return self.branching.fuse(
            self.conjugate(expression.verb,
                           expression.tense,
                           expression.subject.count),
            [self.adverb(c) for c in expression.verb.complements])
                                
    def translate(self, expression):
        return self.order.order(self.subject(expression),
                                self.verb(expression),
                                self.obj(expression)
                                if expression.verb.head.transitive
                                else None)

# pure SOV, auxiliaries used to mark parts of speech
english = Language(SOV,
                   'those',
                   'like',
                   'that',
                   'one',
                   { Past : 'did',  Present : 'is', Future : 'will' })
print 'old:', english.translate(e)

# ossify parts of speech as suffixes
english.formadverb = english.branching.affixer(english.advaffix)
english.pluralize = english.branching.affixer(english.pluralaffix)
english.formtense[Past] = english.branching.affixer(english.tenses[Past])
english.formtense[Present] = english.branching.affixer(english.tenses[Present])
english.formnoun = english.branching.fuser()
english.define = english.branching.antifixer(english.definite)
english.indefine = english.branching.antifixer(english.indefinite)
english.formadj = english.branching.fuser()

print 'middle:', english.translate(e)

# contract
english.formadverb.affix = 'ly'
english.formtense[Past].affix = 'ed'
english.formtense[Present].affix = 's'
english.pluralize.affix = 's'
english.define.affix = 'the'
english.indefine.affix = 'a'

# preserve
preserve = english.formadj, english.define, english.indefine, english.formnoun, english.pluralize, english.formadverb, english.formtense[Past], english.formtense[Present]

# switch to SVO overall
english = Language(SVO,
                   's',
                   'ly',
                   'the',
                   'a',
                   { Past : 'ed',  Present : 's', Future : 'will' })

# preserve some word orders and contractions
english.formadj, english.define, english.indefine, english.formnoun, english.pluralize, english.formadverb, english.formtense[Past], english.formtense[Present] = preserve

print 'modern:', english.translate(e)
