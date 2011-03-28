from random import randint, sample

vowelpositions = [
  # front   ->   back
    ['&',  'a',  'A'],  # open
    ['E',  'V"', 'V'],  # open-mid
    ['e',  '@',  'o-'], # close-mid
    ['i',  'i"', 'u-']] # close

def backness(vowel):
    for i in range(len(vowelpositions)):
        for j in range(len(vowelpositions[i])):
            if vowelpositions[i][j] == vowel:
                return j
    raise ValueError

def height(vowel):
    for i in range(len(vowelpositions)):
        if vowel in vowelpositions[i]:
            return i
    raise ValueError

vowels = [v for p in vowelpositions for v in p]

consonantplaces = [
    ['m', 'p', 'b', 'P', 'B',],                 # bilabial         (close)
    ['M', 'f', 'v'],                            # labiodental
    ['n[', 't[', 'd[', 'T', 'D'],               # dental
    ['n', 't', 'd', 's', 'z', 'r', 'l', '*'],   # alveolar         (close-mid)
    ['n.', 't.', 'd.', 's.', 'z.', 'l.', '*.'], # retroflex
    ['S', 'Z'],                                 # palato-alveolar  (open-mid)
    ['c', 'J', 'C', 'j', 'l^'],                 # palatal
    ['N', 'k', 'g', 'x', 'Q', 'L'],             # velar            (near-open)
    ['q', 'G', 'X', 'g"'],                      # uvular
    ['w'],                                      # labiovelar
    ['H'],                                      # pharyngeal       (open)
    ['?', 'h']]                                 # glottal

consonants = [c for p in consonantplaces for c in p]

def phonemes(nv = None, nc = None):
    global vowels, consonants
    
    # subset of possible vowels
    nv = (len(vowels)/2, 3*len(vowels)/5) if nv is None else nv
    vs = sample(vowels, randint(max(0, min(len(vowels), nv[0])),
                                max(0, min(len(vowels), nv[1]))))

    # subset of possible consonants
    nc = (len(consonants)/5, 3*len(consonants)/5) if nc is None else nc
    cs = sample(consonants, randint(max(0, min(len(consonants), nc[0])),
                                    max(0, min(len(consonants), nc[1]))))

    return vs, cs
