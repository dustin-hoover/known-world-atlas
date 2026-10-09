"""Authoring source for the Known World's geography: writes src/geo.js.

Our own generalised drawing of Westeros, Essos and Sothoryos (LAWS I.2: never traced from a published map).
Control points are in miles: X east and Y north of Winterfell. Coasts and areas are smoothed (Chaikin) so the
shapes read as land, not polygons; the terrain engine adds the fine detail. Positions are graded 'inferred'
in src/sources.js until a chapter or a stated distance pins them (docs/otherworldly/got/PLAN.md).
Run: python3 tools/known/author.py && npm run build
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'src', 'geo.js')


def chaikin(pts, n=2, closed=True):
    for _ in range(n):
        out = []
        m = len(pts) if closed else len(pts) - 1
        if not closed: out.append(pts[0])
        for i in range(m):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out.append([round(a[0] * 0.75 + b[0] * 0.25, 1), round(a[1] * 0.75 + b[1] * 0.25, 1)])
            out.append([round(a[0] * 0.25 + b[0] * 0.75, 1), round(a[1] * 0.25 + b[1] * 0.75, 1)])
        if not closed: out.append(pts[-1])
        pts = out
    return pts


# ---------------------------------------------------------------- coasts
WESTEROS = [  # clockwise from the north-west of the Land of Always Winter
    [-420, 1250], [-300, 1330], [-150, 1360], [0, 1340], [150, 1360], [300, 1320], [420, 1250], [470, 1100], [430, 950],
    [380, 820], [300, 700], [330, 640], [250, 560], [195, 500], [154, 470], [148, 452], [160, 438],  # Hardhome, the Bay of Seals at Eastwatch
    [220, 420], [300, 380], [380, 330], [420, 250], [440, 160], [470, 60], [520, -60], [545, -150],  # the east coast, Widow's Watch
    [480, -200], [400, -230], [260, -250], [190, -272],                                            # the Bite's north shore, White Harbor
    [140, -320], [112, -400], [104, -480], [150, -545],                                            # the Neck's east shore
    [220, -560], [320, -545], [430, -520], [560, -500], [585, -560], [500, -605], [565, -655],     # the Fingers
    [560, -720], [580, -800], [525, -858], [470, -900], [400, -885], [330, -925], [300, -960],     # Gulltown, the Bay of Crabs
    [350, -1000], [430, -1040], [462, -1100], [400, -1135], [330, -1160], [272, -1232], [244, -1302],  # Crackclaw Point, Blackwater Bay
    [300, -1332], [420, -1332], [470, -1380], [400, -1420], [352, -1480], [372, -1580],            # Massey's Hook, Shipbreaker Bay
    [500, -1600], [562, -1680], [520, -1760], [400, -1850], [250, -1900], [100, -1930], [-20, -1965],  # Cape Wrath; the Sea of Dorne
    [60, -2045], [200, -2075], [350, -2078], [480, -2068], [640, -2098], [702, -2140], [640, -2190],   # Dorne's north shore, the Broken Arm
    [585, -2238], [560, -2320], [522, -2400], [420, -2480], [250, -2540], [60, -2560], [-120, -2530],  # Sunspear, Planky Town
    [-232, -2420], [-300, -2300], [-380, -2200], [-428, -2128], [-470, -2080], [-522, -2000],      # Starfall, Oldtown
    [-562, -1900], [-562, -1780], [-522, -1702], [-562, -1600], [-522, -1450],                     # the Shield Islands, the Mander
    [-480, -1300], [-402, -1182], [-452, -1100], [-472, -1000], [-442, -900],                      # Lannisport, the Westerlands
    [-360, -830], [-260, -780], [-160, -722], [-110, -690], [-80, -640],                           # Ironman's Bay, Seagard
    [-150, -600], [-260, -560], [-330, -520], [-260, -470], [-90, -450],                           # Cape Kraken
    [-38, -382], [-150, -380], [-260, -330], [-380, -300], [-450, -250], [-420, -150],             # Blazewater Bay, the Stony Shore
    [-520, -40], [-600, 40], [-560, 110], [-440, 120], [-330, 180], [-260, 250], [-220, 320], [-180, 400],  # Sea Dragon Point, the Bay of Ice
    [-150, 425], [-136, 444], [-142, 462], [-220, 520], [-320, 600], [-400, 700], [-470, 850], [-480, 1000],                 # the Wall's west end, the Frozen Shore
]
ESSOS = [
    [720, -420], [800, -380], [950, -360], [1100, -330], [1300, -300], [1600, -260], [1900, -230], [2200, -200],
    [2500, -180], [2800, -160], [3100, -170], [3500, -200], [3900, -260], [4300, -330], [4700, -420], [5100, -560],
    [5500, -760], [5650, -1100], [5600, -1500], [5450, -1900], [5300, -2300], [5150, -2660], [4800, -2800],
    [4600, -2700], [4100, -2620], [3700, -2560], [3420, -2610], [3200, -2500], [2900, -2400], [2800, -2300],
    [2760, -2100], [2700, -1960], [2600, -2010], [2470, -2140], [2350, -2300], [2200, -2350], [2000, -2400],
    [1850, -2550], [1760, -2700], [1650, -2560], [1550, -2350], [1420, -2205], [1300, -2150], [1150, -2100],
    [1000, -1900], [905, -1565], [950, -1450], [880, -1400], [782, -1122], [760, -900], [800, -700], [762, -500],
]
SOTHORYOS = [
    [700, -3150], [1000, -3080], [1400, -3100], [1800, -3050], [2200, -3120], [2600, -3150], [3000, -3250],
    [3400, -3350], [3600, -3600], [3700, -4000], [3600, -4500], [3300, -5000], [2800, -5300], [2200, -5350],
    [1600, -5200], [1100, -4900], [800, -4500], [650, -4000], [600, -3600],
]


def isle(name, cx, cy, rx, ry, k=9, jag=0.18, seed=1):
    import math
    pts = []
    for i in range(k):
        a = i / k * 2 * math.pi
        r = 1 + jag * math.sin(a * 3 + seed) * math.cos(a * 2 - seed)
        pts.append([round(cx + math.cos(a) * rx * r, 1), round(cy + math.sin(a) * ry * r, 1)])
    return {'name': name, 'pts': chaikin(pts, 2)}


ISLANDS = [
    {'name': 'Essos', 'pts': chaikin(ESSOS, 2)},
    {'name': 'Sothoryos', 'pts': chaikin(SOTHORYOS, 2)},
    isle('Bear Island', -300, 262, 32, 22, seed=2), isle('Skagos', 350, 500, 40, 30, seed=3),
    isle('The Three Sisters', 330, -300, 34, 12, seed=4),
    isle('Pyke', -330, -762, 16, 12, seed=5), isle('Great Wyk', -395, -718, 34, 26, seed=6), isle('Old Wyk', -425, -672, 18, 16, seed=7),
    isle('Harlaw', -296, -702, 24, 18, seed=8), isle('Orkmont', -362, -640, 20, 18, seed=9), isle('Blacktyde', -420, -770, 16, 14, seed=10),
    isle('Fair Isle', -480, -1062, 14, 10, seed=11), isle('Dragonstone', 402, -1190, 18, 15, seed=12), isle('Driftmark', 362, -1212, 18, 10, seed=13),
    isle('Claw Isle', 432, -1090, 9, 7, seed=14), isle('Tarth', 565, -1520, 30, 14, seed=15), isle('The Arbor', -570, -2232, 32, 22, seed=16),
    isle('The Shield Islands', -590, -1760, 20, 30, seed=17),
    isle('Tyrosh', 780, -1722, 26, 18, seed=18), isle('Lys', 952, -2030, 28, 16, seed=19),
    isle('The Stepstones', 770, -2100, 34, 10, seed=20), isle('Bloodstone', 860, -2050, 18, 10, seed=21),
    isle('Lorath', 1242, -246, 40, 26, seed=22), isle('Ib', 2800, -40, 220, 120, k=11, seed=23),
    isle('The Summer Isles', -150, -2970, 120, 70, k=11, seed=24), isle('Naath', 2050, -2950, 60, 34, seed=25),
    isle('The Basilisk Isles', 1700, -2880, 70, 30, seed=26), isle('New Ghis', 2240, -2455, 30, 22, seed=27),
]

# ---------------------------------------------------------------- relief
RANGES = [
    {'name': 'The Frostfangs', 'h': 3000, 'w': 50, 'label': True, 'pts': [[-300, 560], [-250, 700], [-210, 850], [-190, 1000]]},
    {'name': 'Mountains of the Moon', 'h': 3400, 'w': 60, 'label': True, 'pts': [[230, -630], [300, -690], [362, -752], [410, -830], [400, -905]]},
    {'name': 'The Red Mountains', 'h': 3000, 'w': 55, 'label': True, 'pts': [[-280, -2250], [-160, -2185], [-40, -2140], [40, -2100]]},
    {'name': 'The Bones', 'alt': 'The Bone Mountains', 'h': 3600, 'w': 80, 'label': True, 'pts': [[3020, -900], [3060, -1300], [3110, -1700], [3160, -2100]]},
    {'name': 'Mountains of the Shadow', 'h': 4200, 'w': 70, 'label': True, 'pts': [[4880, -2250], [5000, -2400], [5120, -2520]]},
    {'name': 'The Velvet Hills', 'h': 900, 'w': 50, 'label': False, 'pts': [[1000, -680], [1060, -880], [1080, -1020]]},
]
HILLS = [
    {'name': 'The Westerlands hills', 'h': 900, 'w': 50, 'pts': [[-360, -900], [-300, -1000], [-270, -1100]]},
    {'name': 'The Barrowlands', 'h': 260, 'w': 30, 'pts': [[-120, -200], [-60, -260]]},
    {'name': 'The Dornish Marches', 'h': 500, 'w': 30, 'pts': [[-200, -2050], [40, -2030]]},
]
PEAKS = [
    {'name': 'Dragonmont', 'alt': 'the smoking mountain of Dragonstone', 'x': 402, 'y': -1186, 'h': 1100, 'r': 9, 'kind': 'volcano'},
    {'name': 'The Giant\'s Lance', 'alt': 'with the Eyrie on its shoulder', 'x': 368, 'y': -752, 'h': 4300, 'r': 14, 'kind': 'mountain'},
    {'name': 'The Mother of Mountains', 'alt': 'above Vaes Dothrak', 'x': 2700, 'y': -985, 'h': 1500, 'r': 12, 'kind': 'mountain'},
    {'name': 'The Fourteen Flames', 'alt': 'the fires of the Doom', 'x': 1790, 'y': -2560, 'h': 2600, 'r': 22, 'kind': 'volcano'},
]

# ---------------------------------------------------------------- water
RIVERS = [
    {'name': 'The White Knife', 'w0': 20, 'w1': 160, 'rank': 3, 'pts': [[60, -80], [100, -150], [150, -230], [190, -272]]},
    {'name': 'The Last River', 'w0': 20, 'w1': 140, 'rank': 3, 'pts': [[60, 280], [160, 330], [300, 380]]},
    {'name': 'The Milkwater', 'w0': 20, 'w1': 140, 'rank': 3, 'pts': [[-200, 950], [-160, 800], [-200, 640], [-250, 560]]},
    {'name': 'The Green Fork', 'w0': 30, 'w1': 220, 'rank': 2, 'pts': [[60, -560], [40, -620], [70, -720], [110, -830], [160, -890]]},
    {'name': 'The Blue Fork', 'w0': 30, 'w1': 200, 'rank': 3, 'pts': [[180, -660], [150, -760], [160, -890]]},
    {'name': 'The Red Fork', 'w0': 30, 'w1': 220, 'rank': 2, 'pts': [[-220, -960], [-120, -920], [-30, -900], [70, -890], [160, -890]]},
    {'name': 'The Trident', 'w0': 220, 'w1': 420, 'rank': 1, 'pts': [[160, -890], [230, -915], [300, -955]]},
    {'name': 'The Blackwater Rush', 'w0': 40, 'w1': 380, 'rank': 1, 'pts': [[-220, -1130], [-60, -1200], [100, -1260], [244, -1302]]},
    {'name': 'The Mander', 'w0': 40, 'w1': 420, 'rank': 1, 'pts': [[120, -1420], [-30, -1450], [-160, -1560], [-280, -1650], [-420, -1690], [-522, -1702]]},
    {'name': 'The Honeywine', 'w0': 20, 'w1': 200, 'rank': 3, 'pts': [[-300, -1950], [-380, -2050], [-428, -2128]]},
    {'name': 'The Torrentine', 'w0': 20, 'w1': 160, 'rank': 3, 'pts': [[-160, -2240], [-200, -2320], [-232, -2400]]},
    {'name': 'The Greenblood', 'w0': 30, 'w1': 260, 'rank': 2, 'pts': [[100, -2250], [300, -2350], [522, -2400]]},
    {'name': 'The Rhoyne', 'alt': 'the Mother Rhoyne', 'w0': 60, 'w1': 900, 'rank': 1, 'pts': [[1150, -650], [1180, -850], [1230, -1050], [1300, -1500], [1360, -1800], [1420, -2205]]},
    {'name': 'The Skahazadhan', 'w0': 40, 'w1': 300, 'rank': 2, 'pts': [[2900, -1650], [2800, -1820], [2700, -1960]]},
]
LAKES = [
    {'name': 'The Gods Eye', 'pts': chaikin([[70, -960], [140, -950], [175, -990], [150, -1035], [90, -1035], [60, -1000]], 2)},
    {'name': 'The Long Lake', 'pts': chaikin([[30, 180], [60, 185], [62, 215], [36, 220]], 2)},
]

# ---------------------------------------------------------------- land cover
def area(name, pts, **kw):
    d = {'name': name, 'pts': chaikin(pts, 2)}; d.update(kw); return d

FORESTS = [
    area('The Haunted Forest', [[-200, 480], [150, 480], [250, 700], [0, 900], [-180, 800]], dens=1, dark=0.6),
    area('The Wolfswood', [[-330, 20], [-120, 60], [-80, -120], [-280, -150]], dens=0.9),
    area('The Kingswood', [[250, -1380], [420, -1420], [400, -1520], [240, -1500]], dens=0.9),
    area('The Rainwood', [[400, -1680], [520, -1700], [480, -1800], [350, -1760]], dens=1, dark=0.3),
    area('The Forest of Qohor', [[1300, -950], [1500, -900], [1550, -1150], [1350, -1200]], dens=1, dark=0.4),
    area('The jungles of Sothoryos', [[700, -3200], [3500, -3400], [3600, -4400], [800, -4400]], dens=1, dark=0.5),
]
MARSHES = [area('The Neck', [[-40, -385], [108, -392], [98, -555], [-78, -556]])]
ARID = [
    area('The Dornish sands', [[-50, -2250], [400, -2150], [500, -2350], [200, -2500], [-100, -2450]], v=0.9),
    area('The Red Waste', [[2800, -1600], [3150, -1600], [3300, -2300], [2950, -2400], [2800, -2100]], v=1),
    area('Lhazar', [[2200, -1600], [2750, -1600], [2700, -1900], [2250, -1900]], v=0.45),
]
FARMS = [
    area('The Riverlands', [[-150, -700], [250, -700], [300, -1100], [-150, -1100]], v=0.8),
    area('The Reach', [[-500, -1450], [100, -1450], [100, -1800], [-450, -2000]], v=1),
    area('The Crownlands', [[120, -1150], [300, -1150], [300, -1350], [120, -1350]], v=0.7),
    area('The Westerlands', [[-430, -1050], [-250, -1050], [-250, -1250], [-430, -1250]], v=0.6),
    area('The Winterfell fields', [[-100, 80], [100, 80], [100, -100], [-100, -100]], v=0.4),
    area('The Rhoyne valley', [[1150, -1500], [1450, -1500], [1450, -2150], [1150, -2150]], v=0.8),
]
GRASS = [area('The Dothraki Sea', [[1500, -700], [2600, -700], [2900, -1000], [2900, -1500], [2400, -1600], [1700, -1500], [1500, -1100]], v=1)]
ASH = [area('The Smoking Sea', [[1650, -2400], [1950, -2400], [1900, -2680], [1700, -2720]], v=1)]
UPLIFT = []
ICE = [area('The Land of Always Winter', [[-420, 1080], [420, 1080], [420, 1360], [-420, 1360]], v=1)]
RELIEF = []

# ---------------------------------------------------------------- places
# [name, kind, X, Y, people, realm, note (ours), opts]
def P(name, kind, x, y, people, realm, note, **o): return [name, kind, x, y, people, realm, note, o]

PLACES = [
    # the North and the Wall
    P('Winterfell', 'fortress', 0, 0, 'north', 'The North', 'Seat of House Stark, warmed by hot springs, with an ancient godswood and the crypts of the Kings of Winter.', rank=1, culture='bree', r=0.35, pop=2000),
    P('Castle Black', 'fortress', 20, 452, 'watch', 'The Wall', 'Chief castle of the Night\'s Watch, at the foot of the Wall.', rank=1),
    P('Eastwatch-by-the-Sea', 'fortress', 157, 458, 'watch', 'The Wall', 'The Watch\'s castle at the Wall\'s eastern end, on the Bay of Seals.', rank=3),
    P('The Shadow Tower', 'fortress', -110, 452, 'watch', 'The Wall', 'The westernmost manned castle of the Watch, by the mountains.', rank=3),
    P('Westwatch-by-the-Bridge', 'ruin', -145, 450, 'watch', 'The Wall', 'An abandoned castle near the Wall\'s western end.', rank=5),
    P('The Nightfort', 'ruin', -40, 452, 'watch', 'The Wall', 'The oldest and largest castle on the Wall, long abandoned.', rank=4),
    P('Mole\'s Town', 'village', 20, 432, 'north', 'The Gift', 'A village south of Castle Black, much of it underground.', rank=5),
    P('Last Hearth', 'fortress', 110, 330, 'north', 'The North', 'Seat of House Umber.', rank=4),
    P('Karhold', 'fortress', 380, 170, 'north', 'The North', 'Seat of House Karstark in the east of the North.', rank=4),
    P('The Dreadfort', 'fortress', 260, 60, 'north', 'The North', 'Seat of House Bolton.', rank=3),
    P('Deepwood Motte', 'fortress', -260, 60, 'north', 'The North', 'Seat of House Glover in the Wolfswood.', rank=3),
    P('Bear Island', 'fortress', -300, 262, 'north', 'The North', 'Island seat of House Mormont.', rank=4),
    P('Torrhen\'s Square', 'fortress', -130, -170, 'north', 'The North', 'Seat of House Tallhart.', rank=4),
    P('Barrowton', 'town', -90, -240, 'north', 'The North', 'Town of the barrowlands beside the First King\'s barrow.', rank=4, culture='bree', r=0.25, pop=2500),
    P('White Harbor', 'port', 185, -275, 'north', 'The North', 'The North\'s great port, seat of House Manderly, at the mouth of the White Knife.', rank=2, culture='gondor', r=0.5, pop=12000),
    P('Widow\'s Watch', 'fortress', 500, -110, 'north', 'The North', 'Seat of House Flint on a peninsula of the east coast.', rank=5),
    P('Moat Cailin', 'ruin', 40, -420, 'north', 'The North', 'A ruined fortress guarding the causeway through the Neck.', rank=3),
    P('Greywater Watch', 'fortress', 30, -500, 'crannog', 'The North', 'The moving castle of House Reed in the swamps of the Neck.', rank=4),
    # beyond the Wall
    P('The Fist of the First Men', 'landmark', -40, 600, 'free', 'Beyond the Wall', 'An ancient ring-fort on a hill in the Haunted Forest.', rank=3),
    P('Craster\'s Keep', 'village', 10, 690, 'free', 'Beyond the Wall', 'A wildling holdfast in the Haunted Forest.', rank=4),
    P('Hardhome', 'ruin', 300, 640, 'free', 'Beyond the Wall', 'A ruined wildling town on the coast north-east of the Wall.', rank=3),
    P('Whitetree', 'village', -60, 520, 'free', 'Beyond the Wall', 'An abandoned wildling village around a great weirwood.', rank=5),
    P('The Skirling Pass', 'landmark', -240, 760, 'free', 'Beyond the Wall', 'A high pass through the Frostfangs.', rank=5),
    # the riverlands
    P('The Twins', 'fortress', 40, -620, 'river', 'The Riverlands', 'Twin castles of House Frey on both banks of the Green Fork, joined by a bridge.', rank=2),
    P('Seagard', 'fortress', -110, -690, 'river', 'The Riverlands', 'Seat of House Mallister on Ironman\'s Bay.', rank=4),
    P('Riverrun', 'fortress', -30, -900, 'river', 'The Riverlands', 'Seat of House Tully where the Tumblestone meets the Red Fork.', rank=2),
    P('Harrenhal', 'fortress', 130, -960, 'river', 'The Riverlands', 'The greatest castle ever raised in Westeros, its towers melted by dragonfire.', rank=2),
    P('The Isle of Faces', 'landmark', 110, -995, 'river', 'The Riverlands', 'An island of weirwoods in the Gods Eye.', rank=4),
    P('The Ruby Ford', 'ford', 160, -890, 'river', 'The Riverlands', 'Where the Kingsroad crosses the Trident.', rank=4),
    P('The Inn at the Crossroads', 'village', 175, -935, 'river', 'The Riverlands', 'An inn where the Kingsroad, the River Road and the High Road meet.', rank=4),
    P('Saltpans', 'town', 324, -927, 'river', 'The Riverlands', 'A small port on the Bay of Crabs.', rank=5),
    P('Maidenpool', 'port', 302, -955, 'river', 'The Riverlands', 'A port town on the Bay of Crabs.', rank=4),
    P('Stoney Sept', 'town', 60, -1080, 'river', 'The Riverlands', 'A walled town in the southern riverlands.', rank=4, culture='bree', r=0.25, pop=3000),
    P('Raventree Hall', 'fortress', 20, -780, 'river', 'The Riverlands', 'Seat of House Blackwood.', rank=5),
    # the Vale
    P('The Eyrie', 'fortress', 362, -756, 'vale', 'The Vale', 'Seat of House Arryn, high on the shoulder of the Giant\'s Lance.', rank=2),
    P('The Bloody Gate', 'fortress', 300, -770, 'vale', 'The Vale', 'The fortified gate at the western entrance of the Vale.', rank=4),
    P('Gulltown', 'port', 522, -860, 'vale', 'The Vale', 'The Vale\'s chief port.', rank=3, culture='gondor', r=0.35, pop=8000),
    P('Runestone', 'fortress', 560, -762, 'vale', 'The Vale', 'Seat of House Royce.', rank=4),
    # the Iron Islands
    P('Pyke', 'fortress', -330, -762, 'iron', 'The Iron Islands', 'Seat of House Greyjoy, its towers on sea stacks joined by bridges.', rank=2),
    P('Lordsport', 'port', -322, -748, 'iron', 'The Iron Islands', 'The chief harbour of Pyke.', rank=4),
    P('Ten Towers', 'fortress', -296, -702, 'iron', 'The Iron Islands', 'Seat of House Harlaw.', rank=5),
    P('Nagga\'s Hill', 'landmark', -425, -672, 'iron', 'The Iron Islands', 'The hill on Old Wyk where kings of the ironborn are chosen.', rank=5),
    # the westerlands
    P('Casterly Rock', 'fortress', -395, -1165, 'west', 'The Westerlands', 'Seat of House Lannister, delved into a great rock above the sea.', rank=2),
    P('Lannisport', 'port', -405, -1185, 'west', 'The Westerlands', 'The great port city below Casterly Rock.', rank=2, culture='gondor', r=0.6, pop=40000),
    P('The Golden Tooth', 'fortress', -230, -980, 'west', 'The Westerlands', 'Castle guarding the pass between the westerlands and the riverlands.', rank=4),
    P('Ashemark', 'fortress', -280, -1060, 'west', 'The Westerlands', 'Seat of House Marbrand.', rank=5),
    P('The Crag', 'fortress', -470, -1000, 'west', 'The Westerlands', 'Seat of House Westerling on the sea.', rank=5),
    # the crownlands
    P('King\'s Landing', 'city', 250, -1300, 'crown', 'The Crownlands', 'The capital of the Seven Kingdoms, on three hills above the Blackwater, crowned by the Red Keep.', rank=1, culture='gondor', r=1.4, pop=500000),
    P('The Red Keep', 'landmark', 250.5, -1299.4, 'crown', 'The Crownlands', 'The royal castle on Aegon\'s High Hill.', rank=4),
    P('The Great Sept of Baelor', 'landmark', 244, -1301, 'crown', 'The Crownlands', 'The great sept on Visenya\'s Hill.', rank=5),
    P('Dragonstone', 'fortress', 400, -1192, 'crown', 'The Crownlands', 'Targaryen island fortress beneath the smoking Dragonmont.', rank=2),
    P('High Tide', 'fortress', 362, -1212, 'crown', 'The Crownlands', 'Seat of House Velaryon on Driftmark.', rank=5),
    P('Duskendale', 'port', 310, -1160, 'crown', 'The Crownlands', 'A port town on the coast north of King\'s Landing.', rank=4),
    P('Rosby', 'fortress', 220, -1250, 'crown', 'The Crownlands', 'A castle on the Kingsroad north of the capital.', rank=5),
    # the stormlands
    P('Storm\'s End', 'fortress', 374, -1576, 'storm', 'The Stormlands', 'Seat of House Baratheon, a great drum tower above Shipbreaker Bay.', rank=2),
    P('Bronzegate', 'fortress', 300, -1500, 'storm', 'The Stormlands', 'Seat of House Buckler.', rank=5),
    P('Evenfall Hall', 'fortress', 562, -1520, 'storm', 'The Stormlands', 'Seat of House Tarth on the island of Tarth.', rank=4),
    P('Griffin\'s Roost', 'fortress', 520, -1680, 'storm', 'The Stormlands', 'Seat of House Connington on Cape Wrath.', rank=5),
    P('Summerhall', 'ruin', 230, -1820, 'storm', 'The Stormlands', 'A ruined Targaryen summer palace in the Dornish Marches.', rank=4),
    P('Nightsong', 'fortress', -120, -2075, 'storm', 'The Stormlands', 'Seat of House Caron in the Dornish Marches.', rank=5),
    # the Reach
    P('Highgarden', 'fortress', -280, -1650, 'reach', 'The Reach', 'Seat of House Tyrell on the Mander, amid fields and gardens.', rank=2, culture='gondor', r=0.3, pop=3000),
    P('Oldtown', 'city', -430, -2120, 'reach', 'The Reach', 'The oldest city of Westeros, home of the Citadel and the Hightower.', rank=2, culture='gondor', r=0.9, pop=100000),
    P('The Hightower', 'tower', -430.8, -2120.6, 'reach', 'The Reach', 'The tallest tower in Westeros, a lighthouse above Oldtown.', rank=3),
    P('The Citadel', 'landmark', -432, -2116, 'reach', 'The Reach', 'The seat of the order of maesters.', rank=4),
    P('Bitterbridge', 'town', -30, -1450, 'reach', 'The Reach', 'A town at the bridge where the Roseroad crosses the Mander.', rank=4),
    P('Goldengrove', 'fortress', -200, -1500, 'reach', 'The Reach', 'Seat of House Rowan.', rank=5),
    P('Horn Hill', 'fortress', -180, -1950, 'reach', 'The Reach', 'Seat of House Tarly.', rank=4),
    P('Tumbleton', 'town', 80, -1440, 'reach', 'The Reach', 'A market town on the Mander.', rank=5),
    P('Brightwater Keep', 'fortress', -420, -1850, 'reach', 'The Reach', 'Seat of House Florent.', rank=5),
    P('Three Towers', 'fortress', -480, -2050, 'reach', 'The Reach', 'Seat of House Costayne.', rank=5),
    P('Ryamsport', 'port', -560, -2215, 'reach', 'The Reach', 'Chief port of the Arbor.', rank=5),
    # Dorne
    P('Sunspear', 'fortress', 585, -2240, 'dorne', 'Dorne', 'Seat of House Martell on the eastern coast of Dorne.', rank=2, culture='harad', r=0.4, pop=10000),
    P('The Water Gardens', 'landmark', 545, -2268, 'dorne', 'Dorne', 'A palace of pools and fountains by the sea.', rank=4),
    P('Planky Town', 'port', 522, -2398, 'dorne', 'Dorne', 'A river port of boats lashed together at the mouth of the Greenblood.', rank=4),
    P('Yronwood', 'fortress', 150, -2200, 'dorne', 'Dorne', 'Seat of House Yronwood.', rank=4),
    P('Starfall', 'fortress', -238, -2380, 'dorne', 'Dorne', 'Seat of House Dayne where the Torrentine meets the sea.', rank=4),
    P('Hellholt', 'fortress', 100, -2400, 'dorne', 'Dorne', 'Seat of House Uller in the sands.', rank=5),
    P('Vaith', 'fortress', 300, -2400, 'dorne', 'Dorne', 'Seat of House Dalt.', rank=5),
    P('Skyreach', 'fortress', -150, -2210, 'dorne', 'Dorne', 'Seat of House Fowler above the Prince\'s Pass.', rank=5),
    # Essos: the Free Cities and the east
    P('Braavos', 'city', 770, -480, 'braavos', 'Braavos', 'City of a hundred islands in a lagoon, guarded by the Titan.', rank=1, culture='lake', r=1.2, pop=400000),
    P('The Titan of Braavos', 'wonder', 766, -505, 'braavos', 'Braavos', 'A giant stone and bronze warrior astride the lagoon\'s entrance.', rank=3),
    P('Lorath', 'city', 1240, -246, 'lorath', 'Lorath', 'The northernmost Free City, on islands in the Shivering Sea.', rank=3),
    P('Pentos', 'city', 794, -1120, 'freecity', 'Pentos', 'A Free City across the narrow sea.', rank=2, culture='gondor', r=0.9, pop=200000),
    P('Norvos', 'city', 1150, -850, 'freecity', 'Norvos', 'A Free City of bells on the upper Rhoyne.', rank=3),
    P('Qohor', 'city', 1450, -1000, 'freecity', 'Qohor', 'A Free City at the edge of its great forest, famed for its smiths.', rank=3),
    P('Myr', 'city', 905, -1565, 'freecity', 'Myr', 'A Free City known for lace, lenses and crossbowmen.', rank=3),
    P('Tyrosh', 'city', 780, -1722, 'freecity', 'Tyrosh', 'A Free City on an island guarding the narrow sea.', rank=3),
    P('Lys', 'city', 952, -2030, 'freecity', 'Lys', 'A Free City on an island in the Summer Sea.', rank=3),
    P('Volantis', 'city', 1420, -2200, 'freecity', 'Volantis', 'The oldest Free City, astride the mouth of the Rhoyne, with its Black Walls.', rank=2, culture='harad', r=1.2, pop=300000),
    P('Selhorys', 'town', 1350, -1760, 'freecity', 'Volantis', 'A Volantene town on the Rhoyne.', rank=5),
    P('Chroyane', 'ruin', 1300, -1500, 'freecity', 'Volantis', 'A ruined Rhoynar city where the Sorrows mists hang on the river.', rank=5),
    P('Valyria', 'ruin', 1800, -2560, 'valyria', 'Valyria', 'The shattered heart of the Freehold, destroyed in the Doom.', rank=2),
    P('Mantarys', 'town', 2000, -2300, 'valyria', 'Valyria', 'A town on the Demon Road.', rank=5),
    P('Vaes Dothrak', 'city', 2700, -1040, 'dothraki', 'The Dothraki Sea', 'The only city of the Dothraki, beneath the Mother of Mountains.', rank=2, culture='east', r=0.8, pop=20000),
    P('Astapor', 'city', 2452, -2150, 'ghiscari', 'Slaver\'s Bay', 'A slave city of red brick on Slaver\'s Bay.', rank=2, culture='harad', r=0.7, pop=50000),
    P('Yunkai', 'city', 2546, -2052, 'ghiscari', 'Slaver\'s Bay', 'A slave city of yellow brick.', rank=3),
    P('Meereen', 'city', 2702, -1965, 'ghiscari', 'Slaver\'s Bay', 'The greatest of the slave cities, crowned by its Great Pyramid.', rank=2, culture='harad', r=0.9, pop=100000),
    P('New Ghis', 'city', 2240, -2455, 'ghiscari', 'Slaver\'s Bay', 'A Ghiscari city on an island.', rank=4),
    P('Vaes Tolorro', 'ruin', 3050, -2000, 'qarth', 'The Red Waste', 'A dead city in the Red Waste.', rank=5),
    P('Qarth', 'city', 3410, -2590, 'qarth', 'Qarth', 'A rich city on the straits between the Summer Sea and the Jade Sea.', rank=2, culture='harad', r=0.9, pop=150000),
    P('Yin', 'city', 4300, -2000, 'yiti', 'Yi Ti', 'The golden capital of Yi Ti.', rank=4),
    P('Asshai', 'city', 5150, -2650, 'shadow', 'Asshai', 'A city of black stone at the edge of the Shadow.', rank=3),
    P('Ib Nefer', 'port', 2800, -60, 'ib', 'Ib', 'The chief port of Ib.', rank=5),
    P('Tall Trees Town', 'port', -150, -2970, 'summer', 'The Summer Isles', 'A port of the Summer Isles.', rank=4),
    P('Naath', 'landmark', 2050, -2950, 'naath', 'Naath', 'The Isle of Butterflies.', rank=4),
    P('Yeen', 'ruin', 1800, -3500, 'sothoryos', 'Sothoryos', 'A ruined city in the jungles of Sothoryos.', rank=5),
    P('Zamettar', 'ruin', 1500, -3600, 'sothoryos', 'Sothoryos', 'A ruined city of Sothoryos.', rank=5),
]

REGION_LABELS = [
    ['WESTEROS', -120, -900, 'realm', 2, 3.6, 1.6], ['ESSOS', 2600, -1300, 'realm', 1.5, 3.6, 2], ['SOTHORYOS', 2100, -4200, 'realm', 1.5, 4, 2],
    ['THE NORTH', -60, 180, 'realm', 3.4, 7.5, 1.1], ['BEYOND THE WALL', 0, 860, 'realm', 3.4, 7.5, 1.0], ['THE RIVERLANDS', 40, -820, 'realm', 3.6, 7.5, 0.9],
    ['THE VALE', 450, -680, 'realm', 3.6, 7.5, 0.9], ['THE IRON ISLANDS', -360, -830, 'realm', 4, 7.5, 0.8], ['THE WESTERLANDS', -320, -1120, 'realm', 3.6, 7.5, 0.9],
    ['THE CROWNLANDS', 200, -1180, 'realm', 3.8, 7.5, 0.8], ['THE REACH', -240, -1800, 'realm', 3.4, 7.5, 1.1], ['THE STORMLANDS', 300, -1650, 'realm', 3.6, 7.5, 0.9],
    ['DORNE', 200, -2320, 'realm', 3.4, 7.5, 1.1], ['THE DOTHRAKI SEA', 2200, -1100, 'region', 3, 7, 1.1], ['THE RED WASTE', 3050, -2150, 'region', 3.6, 7, 0.9],
    ['LHAZAR', 2450, -1750, 'region', 3.8, 7, 0.8], ['SLAVER\'S BAY', 2550, -2280, 'region', 3.8, 7, 0.8], ['YI TI', 4300, -1800, 'region', 3, 7, 1.1],
    ['THE SHADOW', 5100, -2450, 'region', 3.6, 7, 0.9], ['THE LAND OF ALWAYS WINTER', 0, 1200, 'region', 3, 7, 0.9], ['THE NECK', 30, -470, 'region', 4.5, 8, 0.7],
    ['THE DISPUTED LANDS', 1050, -1720, 'region', 4, 7.5, 0.7],
]
SEA_LABELS = [
    ['The Sunset Sea', -1200, -900, 1.6, 0, 6.5], ['The Narrow Sea', 640, -1050, 1.2, 2.5, 7], ['The Summer Sea', 1200, -2750, 1.6, 0, 6.5],
    ['The Shivering Sea', 2400, 250, 1.4, 0, 6.5], ['The Jade Sea', 4300, -3100, 1.4, 0, 6.5], ['Slaver\'s Bay', 2560, -2150, 0.9, 4, 8.5],
    ['The Bite', 300, -330, 0.9, 4, 8.5], ['Blackwater Bay', 320, -1250, 0.8, 5, 9], ['Shipbreaker Bay', 430, -1490, 0.8, 5, 9],
    ['The Sea of Dorne', 250, -2000, 0.9, 4, 8.5], ['Ironman\'s Bay', -250, -720, 0.9, 4, 8.5], ['The Bay of Ice', -320, 380, 0.8, 4, 8.5],
    ['The Bay of Seals', 300, 470, 0.8, 4, 8.5], ['The Smoking Sea', 1800, -2650, 0.9, 4, 8.5], ['The Bay of Crabs', 400, -930, 0.8, 5, 9],
]

# ---------------------------------------------------------------- realms (coarse; tools/borders/borders.py tightens them)
def R(name, color, pts): return {'name': name, 'color': color, 'pts': pts}
REALMS = {'AC298': [
    R('The North', '#c9d1dc', [[-620, 460], [470, 460], [560, -160], [470, -420], [130, -560], [-80, -560], [-350, -520], [-620, -100]]),
    R('Beyond the Wall', '#dfe8ee', [[-520, 460], [480, 460], [480, 1360], [-520, 1360]]),
    R('The Iron Islands', '#4a4a4a', [[-460, -620], [-270, -620], [-270, -800], [-460, -800]]),
    R('The Riverlands', '#7aa0c8', [[-200, -560], [130, -560], [160, -700], [280, -920], [260, -1080], [80, -1150], [-200, -1050], [-260, -800]]),
    R('The Vale', '#9ab8d8', [[130, -500], [600, -480], [620, -900], [420, -930], [250, -850], [160, -650]]),
    R('The Westerlands', '#c84040', [[-500, -850], [-260, -800], [-200, -1050], [-180, -1250], [-480, -1350]]),
    R('The Crownlands', '#b05050', [[260, -1080], [470, -1050], [480, -1350], [260, -1360], [150, -1250]]),
    R('The Reach', '#6aa04a', [[-560, -1350], [-180, -1250], [150, -1360], [160, -1520], [0, -1980], [-300, -2250], [-600, -2050]]),
    R('The Stormlands', '#d0b040', [[160, -1360], [480, -1350], [600, -1650], [450, -1900], [0, -1980], [160, -1520]]),
    R('Dorne', '#e08a3a', [[-300, -2250], [0, -2100], [300, -2070], [720, -2120], [600, -2400], [250, -2580], [-150, -2560]]),
    R('Braavos', '#5a8ab8', [[700, -380], [1000, -380], [1000, -700], [720, -700]]),
    R('Pentos', '#8a7ab8', [[720, -700], [1050, -700], [1050, -1300], [720, -1300]]),
    R('Norvos', '#7a8a6a', [[1050, -700], [1300, -700], [1300, -1000], [1050, -1000]]),
    R('Qohor', '#6a7a5a', [[1300, -800], [1650, -800], [1650, -1250], [1300, -1250]]),
    R('Myr', '#b88a6a', [[850, -1300], [1150, -1300], [1150, -1650], [850, -1650]]),
    R('Volantis', '#b85a7a', [[1150, -1650], [1650, -1650], [1650, -2250], [1150, -2250]]),
    R('The Dothraki Sea', '#c8b878', [[1650, -650], [2950, -650], [2950, -1600], [1650, -1600]]),
    R('Slaver\'s Bay', '#c87a3a', [[2200, -1900], [2900, -1900], [2900, -2400], [2100, -2400]]),
    R('Qarth', '#a85ac8', [[3300, -2300], [3600, -2300], [3600, -2650], [3300, -2650]]),
    R('Yi Ti', '#d8c050', [[3600, -1200], [4800, -1200], [4800, -2500], [3600, -2400]]),
]}
ADMIN = []

PEOPLES = [
    {'name': 'Northmen', 'lang': 'Common Tongue · Old Tongue in the far north', 'color': '#a8c0d8', 'pts': REALMS['AC298'][0]['pts']},
    {'name': 'The Free Folk', 'lang': 'Old Tongue · Common Tongue', 'color': '#e0f0ff', 'pts': [[-520, 460], [480, 460], [480, 1080], [-520, 1080]]},
    {'name': 'The Crannogmen', 'lang': 'Common Tongue', 'color': '#5aa05a', 'pts': [[-40, -385], [108, -392], [98, -555], [-78, -556]]},
    {'name': 'The Ironborn', 'lang': 'Common Tongue', 'color': '#808080', 'pts': REALMS['AC298'][2]['pts']},
    {'name': 'The Andals of the south', 'lang': 'Common Tongue', 'color': '#e8b850', 'pts': [[-560, -560], [600, -480], [620, -1650], [0, -2050], [-600, -2050]]},
    {'name': 'Dornishmen', 'lang': 'Common Tongue', 'color': '#ff8a2a', 'pts': REALMS['AC298'][9]['pts']},
    {'name': 'The Free Cities\' folk', 'lang': 'Bastard Valyrian dialects', 'color': '#b07ae0', 'pts': [[700, -380], [1650, -700], [1650, -2250], [850, -2100], [720, -1300]]},
    {'name': 'Dothraki', 'lang': 'Dothraki', 'color': '#e0c85a', 'pts': REALMS['AC298'][16]['pts']},
    {'name': 'Lhazareen', 'lang': 'Lhazarene', 'color': '#a0d07a', 'pts': [[2200, -1600], [2750, -1600], [2700, -1900], [2250, -1900]]},
    {'name': 'Ghiscari', 'lang': 'Ghiscari · Bastard Valyrian', 'color': '#d0503a', 'pts': REALMS['AC298'][17]['pts']},
    {'name': 'Qartheen', 'lang': 'Qartheen', 'color': '#c070e0', 'pts': REALMS['AC298'][18]['pts']},
    {'name': 'Yi Tish', 'lang': 'Yi Tish', 'color': '#f0e070', 'pts': REALMS['AC298'][19]['pts']},
    {'name': 'Ibbenese', 'lang': 'Ibbenese', 'color': '#7a9aa0', 'pts': [[2580, 80], [3020, 80], [3020, -160], [2580, -160]]},
    {'name': 'Summer Islanders', 'lang': 'Summer Tongue', 'color': '#3ac8a0', 'pts': [[-280, -2900], [-20, -2900], [-20, -3040], [-280, -3040]]},
]

ROADS = [
    {'name': 'The Kingsroad', 'cls': 1, 'pts': [[20, 450], [10, 250], [0, 0], [30, -250], [40, -420], [45, -620], [110, -800], [160, -890], [175, -935], [200, -1100], [220, -1250], [250, -1300], [300, -1450], [374, -1576]]},
    {'name': 'The River Road', 'cls': 2, 'pts': [[-405, -1185], [-300, -1060], [-230, -980], [-30, -900], [80, -910], [175, -935]]},
    {'name': 'The High Road', 'cls': 2, 'pts': [[175, -935], [240, -820], [300, -770], [362, -756]]},
    {'name': 'The Gold Road', 'cls': 2, 'pts': [[250, -1300], [60, -1230], [-150, -1200], [-405, -1185]]},
    {'name': 'The Roseroad', 'cls': 2, 'pts': [[250, -1300], [120, -1400], [-30, -1450], [-280, -1650], [-430, -2120]]},
    {'name': 'The Ocean Road', 'cls': 3, 'pts': [[-280, -1650], [-440, -1500], [-405, -1185]]},
    {'name': 'The Boneway', 'cls': 3, 'pts': [[230, -1820], [150, -2050], [150, -2200]]},
    {'name': 'The Demon Road', 'cls': 3, 'pts': [[1420, -2200], [1700, -2280], [2000, -2300], [2452, -2150]]},
]
WALLS = [{'name': 'The Wall', 'ice': 1, 'pts': [[-145, 449], [-60, 451], [20, 452], [100, 454], [157, 456]]}]

STORIES = {
    'agot': {'title': 'A Game of Thrones', 'start': '298 1 1', 'end': '299 6 1'},
    'acok': {'title': 'A Clash of Kings', 'start': '299 1 1', 'end': '299 13 5'},
    'asos': {'title': 'A Storm of Swords', 'start': '299 6 1', 'end': '300 6 1'},
    'feastdance': {'title': 'A Feast for Crows & A Dance with Dragons', 'start': '300 1 1', 'end': '300 13 5'},
}


def js(v): return json.dumps(v, ensure_ascii=False, separators=(',', ':'))


# castles as the books describe them, modelled in the ground view (src/world3d.js CASTLE); cr: the castle's own ground in miles
CASTLES = {'Winterfell': ('winterfell', 0.16), 'Castle Black': ('castleblack', 0.1), 'The Eyrie': ('eyrie', 0.06), 'Harrenhal': ('harrenhal', 0.35),
           'The Twins': ('twins', 0.15), 'King\'s Landing': ('redkeep', 0.14, 0.5, 0.6), 'Storm\'s End': ('stormsend', 0.09), 'Dragonstone': ('dragonstone', 0.12),
           'Pyke': ('pyke', 0.12), 'Oldtown': ('hightower', 0.06, -0.8, -0.6), 'Riverrun': ('riverrun', 0.12), 'Casterly Rock': ('casterlyrock', 0.3), 'Sunspear': ('sunspear', 0.14)}


def in_poly(x, y, poly):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c


def snap_walls(coast):
    """Run each ice wall's ends out (or back) along its line to meet the sea, ending a mile into the water:
    the Wall goes from the Bay of Ice to the Bay of Seals (AGOT)."""
    import math
    for w in WALLS:
        if not w.get('ice'): continue
        for e, q in ((0, 1), (-1, -2)):
            ex, ey = w['pts'][e]; qx, qy = w['pts'][q]; L = math.hypot(ex - qx, ey - qy); dx, dy = (ex - qx) / L, (ey - qy) / L
            d = -L * 0.6
            while not in_poly(ex + dx * d, ey + dy * d, coast) and d < 0: d += 0.25     # if the end is at sea, come back to land
            while in_poly(ex + dx * d, ey + dy * d, coast) and d < 120: d += 0.25       # then out to the shore
            w['pts'][e] = [round(ex + dx * (d + 1), 1), round(ey + dy * (d + 1), 1)]
    return WALLS


def main():
    coast_s = chaikin(WESTEROS, 2)
    snap_walls(coast_s)
    W0, W1 = WALLS[0]['pts'][0], WALLS[0]['pts'][-1]
    for p in PLACES:
        if p[0] == 'Eastwatch-by-the-Sea': p[2], p[3] = round(W1[0] - 3, 1), round(W1[1] + 2, 1)
        if p[0] == 'Westwatch-by-the-Bridge': p[2], p[3] = round(W0[0] + 3, 1), round(W0[1] - 1, 1)
    for p in PLACES:
        if p[0] in CASTLES:
            o = p[7]; c = CASTLES[p[0]]; o['castle'], o['cr'] = c[0], c[1]
            if len(c) > 2: o['cx'], o['cy'] = c[2], c[3]
            if not o.get('culture'): o['culture'], o['r'] = 'castle', o['cr'] + 0.05
    import cast
    have = {p[0] for p in PLACES}
    for name, kind, x, y, people, realm, note, o in cast.EXTRA_PLACES:
        if name not in have: PLACES.append([name, kind, x, y, people, realm, note, o])
    CAST, JOURNEYS, MODES, EVENTS, BATTLES = cast.build(PLACES, ROADS, STORIES)
    # realm borders fitted to our coasts, ranges, rivers and the Wall; peoples cut to the land
    import realms
    coast = chaikin(WESTEROS, 2)
    claims = REALMS['AC298']
    fitted = realms.fit(claims, PLACES, coast, ISLANDS, RANGES, RIVERS, WALLS, island_realms={'The Iron Islands'})
    byname = {r['name']: r for r in fitted}
    claim_of = {id(c['pts']): c['name'] for c in claims}
    out = []
    for p in PEOPLES:
        if id(p['pts']) in claim_of:
            r = byname.get(claim_of[id(p['pts'])])
            if not r: continue
            q = dict(p, pts=r['pts']); q.pop('parts', None)
            if 'parts' in r: q['parts'] = r['parts']
            out.append(q)
        else: out += realms.clip_peoples([p], coast, ISLANDS)
    PEOPLES[:] = out
    REALMS['AC298'] = fitted
    print('realms fitted:', len(fitted), 'peoples:', len(PEOPLES))
    head = """/* ============================================================================
   THE KNOWN WORLD — geodata (generated by tools/known/author.py; edit there)
   Authoring grid: X = miles east of Winterfell, Y = miles north of Winterfell.
   Our own generalised drawing of Westeros, Essos and Sothoryos; positions are
   inferred from the novels and graded in src/sources.js. The Wall is about 300
   miles long (AGOT). Projected onto the globe with the sinusoidal mapping in gen.js.
   ========================================================================== */
const GEO = (() => {
"""
    parts = [
        ('COAST', chaikin(WESTEROS, 2)), ('ISLANDS', ISLANDS), ('RANGES', RANGES), ('HILLS', HILLS), ('PEAKS', PEAKS),
        ('RIVERS', RIVERS), ('LAKES', LAKES), ('FORESTS', FORESTS), ('MARSHES', MARSHES), ('ARID', ARID), ('FARMS', FARMS),
        ('GRASS', GRASS), ('ASH', ASH), ('UPLIFT', UPLIFT), ('ICE', ICE), ('RELIEF', RELIEF), ('NUMENOR', None),
        ('PLACES', PLACES), ('REGION_LABELS', REGION_LABELS), ('SEA_LABELS', SEA_LABELS), ('REALMS', REALMS),
        ('ADMIN', ADMIN), ('PEOPLES', PEOPLES), ('ROADS', ROADS), ('WALLS', WALLS),
        ('PALANTIRI', {'stones': [], 'links': []}), ('BEACONS', []), ('JOURNEYS', JOURNEYS),
        ('MODES', MODES), ('BATTLES', BATTLES), ('STORIES', STORIES), ('FIREWORKS', []), ('LORE_WEATHER', []),
        ('EVENTS', EVENTS), ('CAST', CAST),
    ]
    body = ''.join(f'const {k} = {js(v)};\n' for k, v in parts)
    tail = 'return { ' + ', '.join(k for k, _ in parts) + ' };\n})();\nif (typeof self !== "undefined") self.GEO = GEO;\n'
    open(OUT, 'w').write(head + body + tail)
    print('wrote', OUT, len(PLACES), 'places')


# ---------------------------------------------------------------- the source ledger (src/sources.js)
BOOK_OF = {'Slaver\'s Bay': 'ASOS', 'Qarth': 'ACOK', 'The Red Waste': 'ACOK', 'Volantis': 'ADWD', 'Braavos': 'AFFC', 'Dorne': 'AFFC',
           'Valyria': 'TWOIAF', 'Yi Ti': 'TWOIAF', 'Asshai': 'TWOIAF', 'Ib': 'TWOIAF', 'Sothoryos': 'TWOIAF', 'Naath': 'ASOS',
           'The Summer Isles': 'AFFC', 'Lorath': 'TWOIAF', 'The Iron Islands': 'ACOK', 'Beyond the Wall': 'ACOK'}
PLACE_BOOK = {'Hardhome': 'ADWD', 'Oldtown': 'AFFC', 'The Hightower': 'AFFC', 'The Citadel': 'AFFC', 'Pentos': 'AGOT', 'Vaes Dothrak': 'AGOT',
              'Harrenhal': 'ACOK', 'Riverrun': 'AGOT', 'The Twins': 'AGOT', 'The Eyrie': 'AGOT', 'Winterfell': 'AGOT', 'Castle Black': 'AGOT',
              'King\'s Landing': 'AGOT', 'Dragonstone': 'ACOK', 'Storm\'s End': 'ACOK', 'Meereen': 'ASOS', 'Astapor': 'ASOS', 'Yunkai': 'ASOS'}
STATEMENTS = [
    {'id': 'wall-long', 'src': 'AGOT', 'conf': 'high', 'claim': 'The Wall runs about 300 miles, from the Bay of Ice to the Bay of Seals.', 'test': ['dist', 'Eastwatch-by-the-Sea', 'Westwatch-by-the-Bridge', 300, 0.1]},
    {'id': 'westeros-long', 'src': 'AUTHOR', 'conf': 'medium', 'claim': 'Westeros is about 3,000 miles long from the Wall to Dorne.', 'test': ['south', 'Castle Black', 'Sunspear', 3000, 0.15]},
]


def sources_js():
    led = {}
    for p in PLACES:
        name, realm = p[0], p[5]
        b = PLACE_BOOK.get(name) or BOOK_OF.get(realm) or 'AGOT'
        led[name] = ['inferred', b + ('; TWOIAF' if b != 'TWOIAF' else ''), '', 0]
    bib = {
        'AGOT': {'t': 'A Game of Thrones', 'a': 'George R. R. Martin', 'y': 1996, 'kind': 'primary', 'cite': 'POV chapter (e.g. Bran I)'},
        'ACOK': {'t': 'A Clash of Kings', 'a': 'George R. R. Martin', 'y': 1998, 'kind': 'primary', 'cite': 'POV chapter'},
        'ASOS': {'t': 'A Storm of Swords', 'a': 'George R. R. Martin', 'y': 2000, 'kind': 'primary', 'cite': 'POV chapter'},
        'AFFC': {'t': 'A Feast for Crows', 'a': 'George R. R. Martin', 'y': 2005, 'kind': 'primary', 'cite': 'POV chapter'},
        'ADWD': {'t': 'A Dance with Dragons', 'a': 'George R. R. Martin', 'y': 2011, 'kind': 'primary', 'cite': 'POV chapter'},
        'TWOIAF': {'t': 'The World of Ice & Fire', 'a': 'George R. R. Martin, Elio M. Garcia Jr., Linda Antonsson', 'y': 2014, 'kind': 'primary history', 'cite': 'section'},
        'FB': {'t': 'Fire & Blood', 'a': 'George R. R. Martin', 'y': 2018, 'kind': 'primary history', 'cite': 'section'},
        'AUTHOR': {'t': 'The author, outside the novels', 'a': 'George R. R. Martin', 'y': 0, 'kind': 'author statement', 'note': 'Interviews and letters: usable, graded below the novels.'},
    }
    todo = ['Every place: find the chapter that places it and set chk to 1; pin positions from stated distances and travel times.',
            'Seasons: the dates the Citadel announces autumn and winter (white ravens).',
            'Journeys (Phase 3): an estimated day for every waypoint, synchronised across POV chapters.']
    head = """/* The source ledger for the Known World (generated by tools/known/author.py; edit there).
   Facts only, in our own words (docs/otherworldly/LAWS.md). Grades: text (placed from the novels' words),
   map (position read from a published map; never its line-work), inferred (our placement from the novels'
   descriptions), todo. `chk` is 0 until the cited chapter has been checked. */
const SOURCES = (() => {
"""
    body = f'const BIB = {js(bib)};\nconst PLACES = {js(led)};\nconst STATEMENTS = {js(STATEMENTS)};\nconst TODO = {js(todo)};\n'
    tail = 'return { BIB, PLACES, STATEMENTS, TODO };\n})();\nif (typeof self !== "undefined") self.SOURCES = SOURCES;\n'
    open(os.path.join(HERE, '..', '..', 'src', 'sources.js'), 'w').write(head + body + tail)


if __name__ == '__main__':
    main()
    sources_js()
