class Syllable(object):
    def __init__(self, onset, nucleus, coda):
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda

    @property
    def phonemes(self):
        return self.onset + self.nucleus + self.coda

class Word(object):
    def __init__(self, syllables):
        self.syllables = syllables

    @property
    def phonemes(self):
        return [p for s in self.syllables for p in s.phonemes]
