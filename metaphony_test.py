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

if __name__ == '__main__':
    unittest.main()
