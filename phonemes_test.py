import unittest

from phonemes import *

class PhonemeTestCase(unittest.TestCase):
    def test_defaults(self):
        phonemes()

    def test_defaults_not_empty(self):
        vcs = phonemes()
        self.assertTrue(all([ps for ps in vcs]))

    def test_hard_limits(self):
        nv = 3
        nd = 2
        nc = 10
        vs, cs = phonemes((nv,nv), (nd,nd), (nc,nc))
        self.assertEqual(len(vs), nv + nd)
        self.assertEqual(len(cs), nc)

    def test_no_vowels(self):
        nv = 0
        nd = 2
        nc = 10
        vs, cs = phonemes((nv,nv), (nd,nd), (nc,nc))
        self.assertEqual(len(vs), nd)

    def test_too_many_vowels(self):
        nv = 100
        nd = 2
        nc = 10
        vs, cs = phonemes((nv,nv), (nd,nd), (nc,nc))
        self.assertTrue(len(vs) < nv)

    def test_no_dips(self):
        nv = 4
        nd = 0
        nc = 10
        vs, cs = phonemes((nv,nv), (nd,nd), (nc,nc))
        self.assertEqual(len(vs), nv)

    def test_too_many_dips(self):
        nv = 4
        nd = 200
        nc = 10
        vs, cs = phonemes((nv,nv), (nd,nd), (nc,nc))
        self.assertTrue(len(vs) < nd)

    def test_no_cons(self):
        nv = 4
        nd = 3
        nc = 0
        vs, cs = phonemes((nv,nv), (nd,nd), (nc,nc))
        self.assertEqual(len(cs), 0)

    def test_too_many_cons(self):
        nv = 4
        nd = 3
        nc = 400
        vs, cs = phonemes((nv,nv), (nd,nd), (nc,nc))
        self.assertTrue(len(cs) < nc)

if __name__ == '__main__':
    unittest.main()
