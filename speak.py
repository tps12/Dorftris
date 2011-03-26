import codecs
from os import remove, system
from random import choice, randint, sample
from tempfile import NamedTemporaryFile

from orthography import getvowelglyph, getconsonantglyph
from phonemes import vowels, consonants, phonemes

ESPEAK = '"\Program Files (x86)\eSpeak\command_line\espeak" -f {file} -v {lang}'
CONTENTS = '[[{text}]]'

def speak(text):
    with NamedTemporaryFile(delete=False) as f:
        temp = f.name
        f.write(CONTENTS.format(text=text))
    
    system(ESPEAK.format(file=temp, lang='en'))
    remove(temp)

ipa = dict([
    ('i', u'\u0069'),
    ('i"', u'\u0268'),
    ('u-', u'\u026f'),
    ('e', u'\u0065'),
    ('@', u'\u0259'),
    ('o-', u'\u0264'),
    ('E', u'\u025b'),
    ('V"', u'\u025c'),
    ('V', u'\u028c'),
    ('&', u'\u00e6'),
    ('a', u'\u0061'),
    ('A', u'\u0251'),
    ('m', u'\u006d'),
    ('M', u'\u0271'),
    ('n[', u'\u006e\u032a'),
    ('n', u'\u006e'),
    ('n.', u'\u0273'),
    ('N', u'\u014b'),
    ('p', u'\u0070'),
    ('b', u'\u0062'),
    ('p[', u'\u0070\u032a'),
    ('b[', u'\u0062\u032a'),
    ('t', u'\u0074'),
    ('d', u'\u0064'),
    ('t[', u'\u0074\u032a'),
    ('d[', u'\u0064\u032a'),
    ('t.', u'\u0288'),
    ('d.', u'\u0256'),
    ('c', u'\u0063'),
    ('J', u'\u025f'),
    ('k', u'\u006b'),
    ('g', u'\u0067'),
    ('q', u'\u0071'),
    ('G', u'\u0262'),
    ('?', u'\u0294'),
    ('P', u'\u03a6'),
    ('B', u'\u03b2'),
    ('f', u'\u0066'),
    ('v', u'\u0076'),
    ('T', u'\u03b8'),
    ('D', u'\u00f0'),
    ('s', u'\u0073'),
    ('z', u'\u007a'),
    ('S', u'\u0283'),
    ('Z', u'\u0292'),
    ('s.', u'\u0282'),
    ('z.', u'\u0290'),
    ('C', u'\u00e7'),
    ('x', u'\u0078'),
    ('Q', u'\u0263'),
    ('X', u'\u03c7'),
    ('g"', u'\u0281'),
    ('H', u'\u0127'),
    ('h', u'\u0068'),
    ('r', u'\u0279'),
    ('*', u'\u027e'),
    ('*.', u'\u027d'),
    ('L', u'\u029f'),
    ('l', u'\u006c'),
    ('l.', u'\u026d'),
    ('l^', u'\u028e')
])

for a in vowels:
    for b in vowels:
        if a != b:
            ipa[a + b] = ipa[a] + ipa[b]

vs, cs = phonemes()

glyphs = dict()

for v in vs:
    glyphs[v] = getvowelglyph(v)

for c in cs:
    glyphs[c] = getconsonantglyph(c)

with NamedTemporaryFile(delete=False) as f:
    filename = f.name

words = []

with codecs.open(filename, 'w', 'utf_8') as f:
    for v in glyphs.keys():
        f.write(u'{glyph}: /{ipa}/\r\n'.format(
            glyph = glyphs[v],
            ipa=ipa[v]))

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
        
        words.append(''.join(phonemes))
        f.write(u'{text} /{ipa}/\r\n'.format(
            text=''.join([glyphs[p] for p in phonemes]),
            ipa=''.join([ipa[p] for p in phonemes])))

system('start notepad ' + filename)

for w in words:
    speak(w)

remove(filename)
