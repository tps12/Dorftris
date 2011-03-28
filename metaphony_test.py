import unittest

from metaphony import *
from phonemes import *

class MetaphonyTestCase(unittest.TestCase):
    def test_feeties(self):
        w = Word([Syllable(*s)
                  for s in [[['f'],['e'],['t']],
                            [[],['i'],['z']]]])
        wm = i_mutate(w)
        self.assertNotEqual(w, wm)

    def test_feeties_fities(self):
        w = Word([Syllable(*s)
                  for s in [[['f'],['e'],['t']],
                            [[],['i'],['z']]]])
        wm = i_mutate(w)
        self.assertEqual(wm.syllables[0].nucleus[0], 'i')

    def test_defeeties(self):
        w = Word([Syllable(*s)
                  for s in [[['d'],['e'],[]],
                            [['f'],['e'],['t']],
                            [[],['i'],['z']]]])
        wm = i_mutate(w)
        self.assertNotEqual(w, wm)

    def test_feetieso(self):
        w = Word([Syllable(*s)
                  for s in [[['f'],['e'],['t']],
                            [[],['i'],['z']],
                            [[],['o'],[]]]])
        wm = i_mutate(w)
        self.assertNotEqual(w, wm)

    def test_feetoes(self):
        w = Word([Syllable(*s)
                  for s in [[['f'],['e'],['t']],
                            [[],['o'],['z']]]])
        wm = i_mutate(w)
        self.assertEqual(w, wm)

    def test_futies(self):
        w = Word([Syllable(*s)
                  for s in [[['f'],['V'],['t']],
                            [[],['i'],['z']]]])
        wm = i_mutate(w)
        self.assertNotEqual(w, wm)

if __name__ == '__main__':
    unittest.main()
