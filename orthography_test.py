import unittest

from orthography import *
from phonemes import consonants, vowels

class OrthographyTestCase(unittest.TestCase):
    def test_every_consonant(self):
        for c in consonants:
            getconsonantglyph(c)

    def test_every_vowel(self):
        for v in vowels:
            getvowelglyph(v)

    def test_every_diphthong(self):
        ds = []
        for v in vowels:
            for w in vowels:
                if v != w:
                    ds.append(v + w)
        for d in ds:
            getvowelglyph(d)

if __name__ == '__main__':
    unittest.main()
