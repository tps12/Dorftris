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
    noun = _(u'sand')

class Gravel(CoarseSoil):
    noun = _(u'gravel')

class FineSoil(Soil):
    pass

class Silt(FineSoil):
    noun = _(u'silt')
    density = 1525.0

class Clay(FineSoil):
    noun = _(u'clay')
    density = 1625.0

class OrganicSoil(Soil):
    density = 1575.0

class OrganicSilt(OrganicSoil):
    noun = _(u'organic soil')

class OrganicClay(OrganicSoil):
    noun = _(u'organic clay')

class Peat(OrganicSoil):
    noun = _(u'peat')
    density = 800.0

class Leaf(Substance):
    density = 100.0
    noun = _(u'tree leaves')
    color = (0, 128, 0)

class Wood(Substance):
    pass

class Stone(Substance):
    color = (128,128,128)
    density = 1500.0
    noun = _(u'stone')
    sound = Mine

class Oak(Wood):
    adjective = _(u'oaken')
    noun = _(u'oak')
    color = (226,171,99)
    density = 750.0

class Ash(Wood):
    adjective = _(u'ash wooden')
    noun = _(u'ash')
    color = (233,214,146)
    density = 670.0

class Aspen(Wood):
    adjective = _(u'aspen wooden')
    noun = _(u'aspen')
    color = (236,222,184)
    density = 420.0

class Balsa(Wood):
    adjective = _(u'balsa wooden')
    noun = _(u'balsa')
    color = (231,203,183)
    density = 170.0

class Birch(Wood):
    adjective = _(u'birchen')
    noun = _(u'birch')
    color = (213,150,83)
    density = 670.0

class Cedar(Wood):
    adjective = _(u'cedar')
    noun = _(u'cedar')
    color = (213,153,79)
    density = 380.0

class Cypress(Wood):
    adjective = _(u'cypress wooden')
    noun = _(u'cypress')
    color = (219,176,140)
    density = 510.0

class Fir(Wood):
    adjective = _(u'fir')
    noun = _(u'fir')
    color = (249,184,136)
    density = 530.0

class Elm(Wood):
    adjective = _(u'elm wooden')
    noun = _(u'elm')
    color = (201,177,135)
    density = 650.0

class Larch(Wood):
    adjective = _(u'larchen')
    noun = _(u'larch')
    color = (209,161,113)
    density = 590.0

class Mahogany(Wood):
    adjective = _(u'mahogany')
    noun = _(u'mahogany')
    color = (92,47,33)
    density = 600.0

class Maple(Wood):
    adjective = _(u'maple')
    noun = _(u'maple')
    color = (222,166,95)
    density = 755.0

class Pine(Wood):
    adjective = _(u'pine')
    noun = _(u'pine')
    color = (250,206,92)
    density = 475.0

class Redwood(Wood):
    adjective = _(u'redwood')
    noun = _(u'redwood')
    color = (217,115,52)
    density = 475.0

class Spruce(Wood):
    adjective = _(u'spruce')
    noun = _(u'spruce')
    color = (212,182,113)
    density = 450.0

class Teak(Wood):
    adjective = _(u'teak')
    noun = _(u'teak')
    color = (152,104,9)
    density = 675.0

class Willow(Wood):
    adjective = _(u'willow')
    noun = _(u'willow')
    color = (250,212,130)
    density = 420.0

class Metal(Substance):
    pass

class Aluminum(Metal):
    adjective = _(u'aluminum')
    noun = _(u'aluminum')
    color = 222, 220, 224
    density = 2600.0

class Beryllium(Metal):
    adjective = _(u'beryllium')
    noun = _(u'beryllium')
    color = 114, 110, 99
    density = 1840.0

class Brass(Metal):
    adjective = _(u'brass')
    noun = _(u'brass')
    color = 237, 208, 56
    density = 8580.0

class Bronze(Metal):
    adjective = _(u'bronzen')
    noun = _(u'bronze')
    color = 159, 122, 92
    density = 8150.0

class AluminumBronze(Bronze):
    adjective = _(u'aluminum bronze')
    noun = _(u'aluminum bronze')
    color = 145, 135, 132
    density = 8200.0

class Cobalt(Metal):
    adjective = _(u'cobalt')
    noun = _(u'cobalt')
    color = 127, 130, 120
    density = 8746.0

class Copper(Metal):
    adjective = _(u'copper')
    noun = _(u'copper')
    color = 221, 172, 134
    density = 8930.0

class BerylliumCopper(Copper):
    adjective = _(u'beryllium copper')
    noun = _(u'beryllium copper')
    density = 8175.0

class Electrum(Metal):
    adjective = _(u'electrum')
    noun = _(u'electrum')
    color = 177, 153, 114
    density = 8650.0

class Gold(Metal):
    adjective = _(u'golden')
    noun = _(u'gold')
    color = 209, 170, 116
    density = 19320.0

class Iron(Metal):
    adjective = _(u'iron')
    noun = _(u'iron')
    color = 110, 115, 117
    density = 7850.0

class CastIron(Iron):
    adjective = _(u'cast iron')
    noun = _(u'cast iron')
    color = 104, 97, 98
    density = 7300.0

class Steel(Iron):
    adjective = _(u'steel')
    noun = _(u'steel')
    color = 198, 190, 188
    density = 7850.0

class Lead(Metal):
    adjective = _(u'leaden')
    noun = _(u'lead')
    color = 106, 100, 108
    density = 11340.0

class Molybdenum(Metal):
    adjective = _(u'molybdenum')
    noun = _(u'molybdenum')
    color = 105, 102, 104
    density = 10188.0

class Nickel(Metal):
    adjective = _(u'nickel')
    noun = _(u'nickel')
    color = 79, 80, 73
    density = 8800.0

class NickelSilver(Metal):
    adjective = _(u'nickel silver')
    noun = _(u'nickel silver')
    color = 173, 177, 180
    density = 8650.0

class Platinum(Metal):
    adjective = _(u'platinum')
    noun = _(u'platinum')
    color = 151, 142, 139
    density = 21400.0

class Plutonium(Metal):
    adjective = _(u'plutonium')
    noun = _(u'plutonium')
    color = 71, 76, 93
    density = 19800.0

class Silver(Metal):
    adjective = _(u'silver')
    noun = _(u'silver')
    color = 197, 197, 197
    density = 10490.0

class Tin(Metal):
    adjective = _(u'tin')
    noun = _(u'tin')
    color = 211, 201, 179
    density = 7280.0

class Titanium(Metal):
    adjective = _(u'titanium')
    noun = _(u'titanium')
    color = 70, 72, 70
    density = 4500.0

class Tungsten(Metal):
    adjective = _(u'tungsten')
    noun = _(u'tungsten')
    color = 111, 130, 138
    density = 19600.0

class Uranium(Metal):
    adjective = _(u'uranium')
    noun = _(u'uranium')
    color = 134, 132, 127
    density = 18900.0

class Vanadium(Metal):
    adjective = _(u'vanadium')
    noun = _(u'vanadium')
    color = 86, 89, 86
    density = 5494.0

class Zinc(Metal):
    adjective = _(u'zinc')
    noun = _(u'zinc')
    color = 166, 164, 161
    density = 7135.0
	
class Meat(Substance):
    color = (63,0,0)
    density = 1000.0

class Water(Substance):
    density = 1000.0
    color = (0,255,255)
    noun = _(u'water')
    adjective = _(u'sodden')

class Blood(Substance):
    density = 1025.0 # thicker than water
    color = 64,0,0
    noun = _(u'blood')
    adjective = _(u'blood-soaked')

class Snow(Substance):
    density = 250,0
    color = (255,255,255)
    noun = _(u'snow')
    adjective = _(u'snowy')

class Grass(Substance):
    color = (0,128,0)
    noun = _(u'grass')
    adjective = _(u'grassy')
