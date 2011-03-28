from phonemes import backness, height, vowelpositions
from words import *

def diphthongize(vowel, consonant):
    h = height(vowel)
    b = backness(consonant)
    v = vowelpositions[h][b]
    return v if v != vowel else None

def breakvowels(word):
    ss = []
    for i in range(len(word.syllables)):
        s = word.syllables[i]
        if len(s.nucleus) == 1:
            c = None
            if s.coda:
                c = s.coda[0]
            elif i < len(word.syllables)-1:
                t = word.syllables[i+1]
                if t.onset:
                    c = t.onset[0]
            if c:
                v = s.nucleus[0]
                w = diphthongize(v, c)
                if w:
                    ss.append(Syllable(s.onset, [v, w], s.coda))
                    continue
        ss.append(s)
    return Word(ss)
