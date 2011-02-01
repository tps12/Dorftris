from sound import Dig, Mine

class Substance(object):
    color = None
    density = None

class AEther(Substance):
    color = (255,255,255)
    density = 0

class Soil(Substance):
    color = (200,150,0)
    sound = Dig

class CoarseSoil(Soil):
    density = 1500.0

class Sand(CoarseSoil):
    noun = _('sand')

class Gravel(CoarseSoil):
    noun = _('gravel')

class FineSoil(Soil):
    pass

class Silt(FineSoil):
    noun = _('silt')
    density = 1525.0

class Clay(FineSoil):
    noun = _('clay')
    density = 1625.0

class OrganicSoil(Soil):
    density = 1575.0

class OrganicSilt(OrganicSoil):
    noun = _('organic soil')

class OrganicClay(OrganicSoil):
    noun = _('organic clay')

class Peat(OrganicSoil):
    noun = _('peat')
    density = 800.0

class Leaf(Substance):
    density = 100.0
    noun = _('tree leaves')
    color = (0, 128, 0)

class Wood(Substance):
    pass

class Stone(Substance):
    color = (128,128,128)
    density = 1500.0
    noun = _('stone')
    sound = Mine

class Oak(Wood):
    adjective = _('oaken')
    noun = _('oak')
    color = (226,171,99)
    density = 750.0

class Ash(Wood):
    adjective = _('ash wooden')
    noun = _('ash')
    color = (233,214,146)
    density = 670.0

class Aspen(Wood):
    adjective = _('aspen wooden')
    noun = _('aspen')
    color = (236,222,184)
    density = 420.0

class Balsa(Wood):
    adjective = _('balsa wooden')
    noun = _('balsa')
    color = (231,203,183)
    density = 170.0

class Birch(Wood):
    adjective = _('birchen')
    noun = _('birch')
    color = (213,150,83)
    density = 670.0

class Cedar(Wood):
    adjective = _('cedar')
    noun = _('cedar')
    color = (213,153,79)
    density = 380.0

class Cypress(Wood):
    adjective = _('cypress wooden')
    noun = _('cypress')
    color = (219,176,140)
    density = 510.0

class Fir(Wood):
    adjective = _('fir')
    noun = _('fir')
    color = (249,184,136)
    density = 530.0

class Elm(Wood):
    adjective = _('elm wooden')
    noun = _('elm')
    color = (201,177,135)
    density = 650.0

class Larch(Wood):
    adjective = _('larchen')
    noun = _('larch')
    color = (209,161,113)
    density = 590.0

class Mahogany(Wood):
    adjective = _('mahogany')
    noun = _('mahogany')
    color = (92,47,33)
    density = 600.0

class Maple(Wood):
    adjective = _('maple')
    noun = _('maple')
    color = (222,166,95)
    density = 755.0

class Pine(Wood):
    adjective = _('pine')
    noun = _('pine')
    color = (250,206,92)
    density = 475.0

class Redwood(Wood):
    adjective = _('redwood')
    noun = _('redwood')
    color = (217,115,52)
    density = 475.0

class Spruce(Wood):
    adjective = _('spruce')
    noun = _('spruce')
    color = (212,182,113)
    density = 450.0

class Teak(Wood):
    adjective = _('teak')
    noun = _('teak')
    color = (152,104,9)
    density = 675.0

class Willow(Wood):
    adjective = _('willow')
    noun = _('willow')
    color = (250,212,130)
    density = 420.0

class Meat(Substance):
    color = (63,0,0)
    density = 1000.0

class Water(Substance):
    density = 1000.0
    color = (0,255,255)
    noun = _('water')
    adjective = _('sodden')

class Blood(Substance):
    density = 1025.0 # thicker than water
    color = 64,0,0
    noun = _('blood')
    adjective = _('blood-soaked')

class Snow(Substance):
    density = 250,0
    color = (255,255,255)
    noun = _('snow')
    adjective = _('snowy')

class Grass(Substance):
    color = (0,128,0)
    noun = _('grass')
    adjective = _('grassy')
