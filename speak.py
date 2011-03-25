import codecs
from os import remove, system
from random import choice, randint, sample
from tempfile import NamedTemporaryFile

ESPEAK = '"\Program Files (x86)\eSpeak\command_line\espeak" -f {file} -v {lang}'
CONTENTS = '[[{text}]]'

def speak(text):
    with NamedTemporaryFile(delete=False) as f:
        temp = f.name
        f.write(CONTENTS.format(text=text))
    
    system(ESPEAK.format(file=temp, lang='en'))
    remove(temp)

vowels = 'i', 'i"', 'u-', 'e', '@', 'o-', 'E', 'V"', 'V', 'A:', 'a', 'A'

consonants = ('m', 'M', 'n[', 'n', 'n.', 'N',
              'p', 'b', 'p[', 'b[', 't', 'd', 't[', 'd[', 't.', 'd.',
              'c', 'J', 'k', 'g', 'q', 'G', '?',
              'P', 'B', 'f', 'v', 'T', 'D', 's', 'z', 'S', 'Z', 's.', 'z.',
              'C', 'x', 'Q', 'X', 'g"', 'H', 'h',
              'r', '*', '*.',
              'L', 'l', 'l.', 'l^')

# subset of possible vowels
vs = sample(vowels, randint(len(vowels)/2, 3*len(vowels)/5))

# add some unique diphthongs
for i in range(randint(0, 5)):
    while True:
        d = ''.join(sample(vowels, 2))
        if d not in vs:
            vs.append(d)
            break

# subset of possible consonants
cs = sample(consonants, randint(len(consonants)/5, 3*len(consonants)/5))

glyphs = dict()

vglyphs = dict([
    ('a', [u'a', u'\u00e1', u'\u00e6', u'\u00e4', u'\u00e0', u'\u00e2', u'\u00e3', u'\u00e5']),
    ('e', [u'e', u'\u00e9', u'\u00eb', u'\u00e8', u'\u00ea', u'\u0119', u'\u0113', u'\u0115']),
    ('i', [u'i', u'\u00ed', u'\u00ec', u'\u00ef', u'\u00ee', u'\u0129']),
    ('o', [u'o', u'\u0153', u'\u00f8', u'\u00f6', u'\u00f3', u'\u00f2']),
    ('u', [u'u', u'\u00fa', u'\u00fc', u'\u00f9', u'\u0169', u'\u016d', u'\u016f', u'\u0171'])
    ])

def getvowelglyph(v):
    global vglyphs

    k = v[0].lower()
    k = 'e' if k == '@' else 'u' if k == 'v' else k
    gs = vglyphs[k]
    return gs.pop(0)

cglyphs = dict([
    ('b', [u'b', u'\u0253', u'\u1e03', u'\u1e07']),
    ('c', [u'c', u'\u00e7']),
    ('d', [u'd', u'\u0111', u'\u018c', u'\u1e11', u'\u1e13']),
    ('f', [u'f']),
    ('g', [u'g', u'\u01e5', u'\u01e7', u'\u01f5', u'\u011d']),
    ('h', [u'h', u'\u0127']),
    ('j', [u'j']),
    ('k', [u'k', u'\u0137']),
    ('l', [u'l', u'\u0142', u'\u013c', u'\u026c', u'\u1e3d']),
    ('m', [u'm', u'\u1e43']),
    ('n', [u'n', u'\u00f1', u'\u0144', u'\u0148']),
    ('p', [u'p', u'\u01a5', u'\u1e55', u'\u1e57']),
    ('q', [u'q', u'\u057b']),
    ('r', [u'r', u'\u0155', u'\u0159']),
    ('s', [u's', u'\u0161', u'\u0283', u'\u0219']),
    ('t', [u't', u'\u0163', u'\u0167', u'\u01ad', u'\u021b']),
    ('v', [u'v']),
    ('x', [u'x', u'\u1e8d']),
    ('z', [u'z', u'\u017e', u'\u0292', u'\u017a'])
    ])

def getconsonantglyph(c):
    global cglyphs

    k = c[0].lower()
    k = 'k' if k == '?' else 'r' if k == '*' else k
    gs = cglyphs[k]
    return gs.pop(0)

for v in vs:
    glyphs[v] = getvowelglyph(v)

for c in cs:
    glyphs[c] = getconsonantglyph(c)

with NamedTemporaryFile(delete=False) as f:
    filename = f.name

words = []

with codecs.open(filename, 'w', 'utf_8') as f:
    for v in glyphs.keys():
        f.write(glyphs[v] + u' = ' + unicode(v) + u'\r\n')

    f.write('\r\n')

    for i in range(10):
        phonemes = []
        
        for s in range(randint(1,2)):
            c = sample(cs, choice((1,) + (2,) * 4))
            if len(c) == 2:
                phonemes += c[0], choice(vs), c[1]
            elif randint(0,1):
                phonemes += c[0], choice(vs)
            else:
                phonemes += choice(vs), c[0]
        
        word = ''.join([glyphs[p] for p in phonemes])
        words.append(''.join(phonemes))
        f.write(word + '\r\n')

system('start notepad ' + filename)

for w in words:
    speak(w)

remove(filename)
