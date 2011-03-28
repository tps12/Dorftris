import unittest

from breaking import *
from phonemes import *

class BreakingTestCase(unittest.TestCase):
    def test_fallan(self):
        w = Word([Syllable(*s)
                  for s in [[['f'],['e'],['r']]]])
        wb = breakvowels(w)
        self.assertNotEqual(w, wb)

if __name__ == '__main__':
    unittest.main()
