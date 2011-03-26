import unittest

from ipa import ipa
from phonemes import consonants, vowels

class IPATestCase(unittest.TestCase):
    def test_all_vowels(self):
        for v in vowels:
            x = ipa[v]

    def test_all_dips(self):
        for v in vowels:
            for w in vowels:
                if v != w:
                    x = ipa[v+w]
            
    def test_all_cons(self):
        for c in consonants:
            x = ipa[c]

if __name__ == '__main__':
    unittest.main()
