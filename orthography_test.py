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

if __name__ == '__main__':
    unittest.main()
