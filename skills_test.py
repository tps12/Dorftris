from unittest import TestCase, main

from skills import SkillSet

class SkillSetTestCase(TestCase):
    def test_empty(self):
        self.assertEqual(len(SkillSet().skills), 0)

    def test_no_exp(self):
        self.assertEqual(SkillSet().exp(['running']), 0)

    def test_train(self):
        s = SkillSet()
        s.train(['running'], 10)
        self.assertEqual(s.exp(['running']), 10)

    def test_train_parent(self):
        s = SkillSet()
        s.train(['athletics','running'], 10)
        self.assertEqual(s.exp(['athletics']), 5)

    def test_train_sibling(self):
        s = SkillSet()
        s.train(['athletics','jumping'], 10)
        self.assertEqual(s.exp(['athletics','running']), 5)

    def test_train_child(self):
        s = SkillSet()
        s.train(['athletics','running'], 10)
        self.assertEqual(s.exp(['athletics','running']), 10)

    def test_train_twice(self):
        s = SkillSet()
        s.train(['running'], 10)
        s.train(['running'], 20)
        self.assertEqual(s.exp(['running']), 30)

    def test_train_parent_twice(self):
        s = SkillSet()
        s.train(['athletics','running'], 10)
        s.train(['athletics','jumping'], 20)
        self.assertEqual(s.exp(['athletics']), 15)

    def test_train_sibling_twice(self):
        s = SkillSet()
        s.train(['athletics','jumping'], 10)
        s.train(['athletics','vaulting'], 30)
        self.assertEqual(s.exp(['athletics','running']), 20)

    def test_train_child_twice(self):
        s = SkillSet()
        s.train(['athletics','running'], 10)
        s.train(['athletics','running'], 50)
        self.assertEqual(s.exp(['athletics','running']), 60)

if __name__ == '__main__':
    main()
