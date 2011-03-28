import codecs
from os import remove, system
from random import choice, randint, sample
from tempfile import NamedTemporaryFile

from ipa import ipa
from metaphony import i_mutate, a_mutate
from orthography import getvowelglyph, getconsonantglyph
from phonemes import vowels, consonants, phonemes
from words import *

ESPEAK = '"\Program Files (x86)\eSpeak\command_line\espeak" -f {file} -v {lang}'
CONTENTS = '[[{text}]]'

def speak(word):
    with NamedTemporaryFile(delete=False) as f:
        temp = f.name
        f.write(CONTENTS.format(text=word.phonemes))
    
    system(ESPEAK.format(file=temp, lang='en'))
    remove(temp)

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

        syllables = []
        for s in range(randint(1,2)):
            c = sample(cs, choice((1,) + (2,) * 4))
            if len(c) == 2:
                syllables.append(Syllable([c[0]], [choice(vs)], [c[1]]))
            elif randint(0,1):
                syllables.append(Syllable([c[0]], [choice(vs)], []))
            else:
                syllables.append(Syllable([], [choice(vs)], [c[0]]))

        word = Word(syllables)

        m = i_mutate(word)
        if m == word:
            m = a_mutate(word)
        
        words.append(m)
        f.write(u'{text} /{ipa}/'.format(
            text=''.join([glyphs[p] for p in word.phonemes]),
            ipa=''.join([ipa[p] for p in word.phonemes])))
        if m != word:
            for p in m.phonemes:
                if p not in glyphs:
                    glyphs[p] = getvowelglyph(p)
            f.write(u' \u2192 {text} /{ipa}/'.format(
                text=''.join([glyphs[p] for p in m.phonemes]),
                ipa=''.join([ipa[p] for p in m.phonemes])))
        f.write(u'\r\n')

system('start notepad ' + filename)

for w in words:
    speak(w)

remove(filename)
