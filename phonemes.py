from random import randint, sample

vowelpositions = [
  # front   ->   back
    ['i',  'i"', 'u-'], # close
    ['e',  '@',  'o-'], # close-mid
    ['E',  'V"', 'V'],  # open-mid
    ['&',  'a',  'A']]  # open

vowels = [v for p in vowelpositions for v in p]

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
    vs = sample(vowels, randint(max(0, min(len(vowels), nv[0])),
                                max(0, min(len(vowels), nv[1]))))

    # add some unique diphthongs
    nd = (0, 5) if nd is None else nd
    for i in range(randint(max(0, min(len(vowels)*(len(vowels)-1), nd[0])),
                           max(0, min(len(vowels)*(len(vowels)-1), nd[1])))):
        while True:
            d = ''.join(sample(vowels, 2))
            if d not in vs:
                vs.append(d)
                break

    # subset of possible consonants
    nc = (len(consonants)/5, 3*len(consonants)/5) if nc is None else nc
    cs = sample(consonants, randint(max(0, min(len(consonants), nc[0])),
                                    max(0, min(len(consonants), nc[1]))))

    return vs, cs
