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
    ('a', ['a', 'á', 'æ', 'ä', 'à', 'â', 'ã', 'å']),
    ('e', ['e', 'é', 'ë', 'è', 'ê', 'ę', 'ē', 'ĕ']),
    ('i', ['i', 'í', 'ì', 'ï', 'î', 'ĩ']),
    ('o', ['o', 'œ', 'ø', 'ö', 'ó', 'ò']),
    ('u', ['u', 'ú', 'ü', 'ù', 'ũ', 'ŭ', 'ů', 'ű'])
    ])

def getvowelglyph(v):
    global vglyphs

    k = v[0].lower()
    k = 'e' if k == '@' else 'u' if k == 'v' else k
    gs = vglyphs[k]
    return gs.pop(0)

cglyphs = dict([
    ('m', ['m', 'ṃ']),
    ('n', ['n', 'ñ', 'ń', 'ň']),
    ('p', ['p', 'ƥ', 'ṕ', 'ṗ']),
    ('b', ['b', 'ɓ', 'ḃ', 'ḇ']),
    ('t', ['t', 'ţ', 'ŧ', 'ƭ', 'ț']),
    ('d', ['d', 'đ', 'ƌ', 'ḑ', 'ḓ']),
    ('c', ['c', 'ç']),
    ('j', ['j']),
    ('k', ['k', 'ķ']),
    ('g', ['g', 'ǥ', 'ǧ', 'ǵ', 'ĝ']),
    ('q', ['q', 'ջ']),
    ('f', ['f']),
    ('v', ['v']),
    ('s', ['s', 'š', 'ʃ', 'ș']),
    ('z', ['z', 'ž', 'ʒ', 'ź']),
    ('x', ['x', 'ẍ']),
    ('h', ['h', 'ħ']),
    ('r', ['r', 'ŕ', 'ř']),
    ('l', ['l', 'ł', 'ļ', 'ɬ', 'ḽ'])
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

    for v in glyphs.keys():
        f.write(glyphs[v] + ' = ' + v + '\r\n')

    f.write('\r\n')

    for i in range(10):
        phonemes = (sample(cs, randint(0,3)) +
                    [choice(vs)] +
                    sample(cs, randint(0,3)))
        
        word = ''.join([glyphs[p] for p in phonemes])
        speak(''.join(phonemes))
        f.write(word + '\r\n')

system('notepad ' + filename)
remove(filename)
