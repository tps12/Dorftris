class Skill(object):
    __slots__ = 'name', 'experience', 'subskills'
    
    def __init__(self, name):
        self.name = name
        self.experience = 0
        self.subskills = []

    def exp(self, skillpath):
        exp = self.experience
        if len(skillpath) > 0:
            try:
                exp = max(exp,
                        (skill for skill in self.subskills
                         if skill.name == skillpath[0]).next().exp(skillpath[1:]))
            except StopIteration:
                pass
        return exp

    def train(self, skillpath, exp):
        self.experience += exp / (2 ** len(skillpath))

        if len(skillpath) > 0:
            skill = None
            
            try:
                skill = (skill for skill in self.subskills
                         if skill.name == skillpath[0]).next()
            except StopIteration:
                skill = Skill(skillpath[0])
                self.subskills.append(skill)

            skill.train(skillpath[1:], exp)

class SkillSet(object):
    __slots__ = 'skills'
    
    def __init__(self):
        self.skills = []

    def exp(self, skillpath):
        try:
            return (skill for skill in self.skills
                    if skill.name == skillpath[0]).next().exp(skillpath[1:])
        except StopIteration:
            return 0

    def train(self, skillpath, exp):
        skill = None

        try:
            skill = (skill for skill in self.skills
                     if skill.name == skillpath[0]).next()
        except StopIteration:
            skill = Skill(skillpath[0])
            self.skills.append(skill)

        skill.train(skillpath[1:], exp)
