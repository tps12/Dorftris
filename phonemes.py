from random import randint, sample

vowels = 'i', 'i"', 'u-', 'e', '@', 'o-', 'E', 'V"', 'V', '&', 'a', 'A'

consonants = ('m', 'M', 'n[', 'n', 'n.', 'N',
              'p', 'b', 'p[', 'b[', 't', 'd', 't[', 'd[', 't.', 'd.',
              'c', 'J', 'k', 'g', 'q', 'G', '?',
              'P', 'B', 'f', 'v', 'T', 'D', 's', 'z', 'S', 'Z', 's.', 'z.',
              'C', 'x', 'Q', 'X', 'g"', 'H', 'h',
              'r', '*', '*.',
              'L', 'l', 'l.', 'l^')



def phonemes(nv = None, nd = None, nc = None):
    global vowels, consonants
    
    # subset of possible vowels
    nv = (len(vowels)/2, 3*len(vowels)/5) if nv is None else nv
    vs = sample(vowels, randint(*nv))

    # add some unique diphthongs
    nd = (0, 5) if nd is None else nd
    for i in range(randint(*nd)):
        while True:
            d = ''.join(sample(vowels, 2))
            if d not in vs:
                vs.append(d)
                break

    # subset of possible consonants
    nc = (len(consonants)/5, 3*len(consonants)/5) if nc is None else nc
    cs = sample(consonants, randint(*nc))

    return vs, cs
