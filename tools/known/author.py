"""Authoring source for the Known World's geography: writes src/geo.js.

Our own generalised drawing of Westeros, Essos and Sothoryos (LAWS I.2: never traced from a published map).
Control points are in miles: X east and Y north of Winterfell. Coasts and areas are smoothed (Chaikin) so the
shapes read as land, not polygons; the terrain engine adds the fine detail. Positions are graded 'inferred'
in src/sources.js until a chapter or a stated distance pins them (docs/geodyssey/got/PLAN.md).
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
    [479, -203], [393, -251], [242, -296], [180, -293],                                            # the Bite's north shore, White Harbor
    [141, -325], [124, -398], [120, -480], [166, -556],                                            # the Neck's east shore
    [230, -592], [315, -596], [417, -580], [553, -526], [578, -584], [492, -639], [561, -665],     # the Fingers
    [558, -719], [580, -793], [526, -858], [475, -900], [400, -895], [327, -941], [297, -975],     # Gulltown, the Bay of Crabs
    [359, -998], [467, -1001], [525, -1028], [469, -1058], [370, -1119], [275, -1216], [227, -1299],  # Crackclaw Point, Blackwater Bay
    [309, -1310], [472, -1270], [509, -1335], [427, -1396], [371, -1478], [388, -1595],            # Massey's Hook, Shipbreaker Bay
    [497, -1613], [554, -1691], [514, -1766], [393, -1842], [242, -1874], [100, -1902], [-15, -1928],  # Cape Wrath; the Sea of Dorne
    [83, -1999], [210, -2062], [351, -2075], [479, -2068], [641, -2101], [704, -2143], [642, -2193],   # Dorne's north shore, the Broken Arm
    [587, -2240], [560, -2318], [518, -2393], [411, -2469], [238, -2541], [53, -2578], [-113, -2555],  # Sunspear, Planky Town
    [-218, -2432], [-293, -2325], [-375, -2247], [-426, -2153], [-472, -2079], [-503, -1977],      # Starfall, Oldtown
    [-486, -1866], [-430, -1739], [-392, -1705], [-408, -1596], [-483, -1458],                     # the Shield Islands, the Mander
    [-424, -1309], [-398, -1179], [-385, -1063], [-343, -945], [-323, -866],                      # Lannisport, the Westerlands
    [-323, -834], [-305, -854], [-307, -854], [-278, -829], [-216, -750],                           # Ironman's Bay, Seagard
    [-282, -716], [-336, -648], [-362, -579], [-291, -506], [-130, -480],                           # Cape Kraken
    [-45, -378], [-183, -408], [-284, -358], [-382, -305], [-450, -250], [-420, -150],             # Blazewater Bay, the Stony Shore
    [-520, -40], [-600, 40], [-560, 110], [-440, 120], [-330, 180], [-260, 250], [-220, 320], [-180, 400],  # Sea Dragon Point, the Bay of Ice
    [-150, 425], [-136, 444], [-142, 462], [-220, 520], [-320, 600], [-400, 700], [-470, 850], [-480, 1000],                 # the Wall's west end, the Frozen Shore
]
def shores():
    """Essos and Sothoryos laid with real shores, and Westeros with real detail on its straight edges, by
    tools/known/shores.py (coast_shores.json), when it exists."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'coast_shores.json')
    return json.load(open(path)) if os.path.exists(path) else {}


SHORES = shores()
SHORE_ISLES = [{'name': i['name'] or 'isle', 'pts': i['pts']} for k in ('Essos', 'Sothoryos') for i in SHORES.get(k, {}).get('islands', [])]

def westeros_coast():
    """Westeros's coast: built from Britain and Ireland by tools/known/donor.py when coast_donor.json exists,
    else the hand-drawn outline above."""
    if 'Westeros' in SHORES: return SHORES['Westeros']['coast']       # with real detail on its straight edges (shores.py)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'coast_donor.json')
    if os.path.exists(path): return json.load(open(path))['coast']
    return chaikin(WESTEROS, 2)


def donor_islands():
    if 'Westeros' in SHORES: return [{'name': i['name'] or 'isle', 'pts': i['pts']} for i in SHORES['Westeros']['islands']]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'coast_donor.json')
    if not os.path.exists(path): return []
    return [{'name': i['name'] or 'isle', 'pts': i['pts']} for i in json.load(open(path))['islands']]


ESSOS = [
    [720, -420], [800, -380], [950, -360], [1100, -330], [1300, -300], [1600, -260], [1900, -230], [2200, -200],
    [2500, -180], [2800, -160], [3100, -170], [3500, -200], [3900, -260], [4300, -330], [4700, -420], [5100, -560],
    [5500, -760], [5650, -1100], [5600, -1500], [5450, -1900], [5300, -2300], [5150, -2660], [4800, -2800],
    [4600, -2700], [4100, -2620], [3700, -2560], [3420, -2610], [3200, -2500], [2900, -2400], [2800, -2300],
    [2760, -2100], [2700, -1960], [2600, -2010], [2470, -2140], [2350, -2300], [2200, -2350], [2000, -2400],
    [1860, -2425], [1760, -2397], [1690, -2398], [1610, -2335], [1520, -2305], [1460, -2262], [1420, -2205], [1300, -2150], [1150, -2100],
    [1000, -1900], [905, -1565], [950, -1450], [880, -1400], [782, -1122], [760, -900], [800, -700], [762, -500],
]
SOTHORYOS = [
    [700, -3150], [1000, -3080], [1400, -3100], [1800, -3050], [2200, -3120], [2600, -3150], [3000, -3250],
    [3400, -3350], [3600, -3600], [3700, -4000], [3600, -4500], [3300, -5000], [2800, -5300], [2200, -5350],
    [1600, -5200], [1100, -4900], [800, -4500], [650, -4000], [600, -3600],
]


SHORE_MADE = {i['name'] for i in SHORE_ISLES if i['name'] != 'isle'}      # hand-drawn islands that real ones replace


def isle(name, cx, cy, rx, ry, k=9, jag=0.18, seed=1):
    import math
    pts = []
    for i in range(k):
        a = i / k * 2 * math.pi
        r = 1 + jag * math.sin(a * 3 + seed) * math.cos(a * 2 - seed)
        pts.append([round(cx + math.cos(a) * rx * r, 1), round(cy + math.sin(a) * ry * r, 1)])
    return {'name': name, 'pts': chaikin(pts, 2)}


ISLANDS = [
    {'name': 'Essos', 'pts': SHORES['Essos']['coast'] if SHORES else chaikin(ESSOS, 2)},
    {'name': 'Sothoryos', 'pts': SHORES['Sothoryos']['coast'] if SHORES else chaikin(SOTHORYOS, 2)},
    isle('The Three Sisters', 286, -434, 34, 12, seed=4),
    isle('Fair Isle', -375, -1011, 14, 10, seed=11), isle('Dragonstone', 488, -1090, 18, 15, seed=12), isle('Driftmark', 434, -1134, 18, 10, seed=13),
    isle('Claw Isle', 489, -1027, 9, 7, seed=14), isle('Tarth', 558, -1522, 30, 14, seed=15), isle('The Arbor', -526, -2496, 32, 22, seed=16),
    isle('The Shield Islands', -434, -1705, 20, 30, seed=17),
    isle('Tyrosh', 780, -1722, 26, 18, seed=18), isle('Lys', 952, -2030, 28, 16, seed=19),
    isle('The Stepstones', 770, -2100, 34, 10, seed=20), isle('Bloodstone', 860, -2050, 18, 10, seed=21),
    isle('Lorath', 1242, -246, 40, 26, seed=22), isle('Ib', 2800, -40, 220, 120, k=11, seed=23),
    isle('The Summer Isles', -150, -2970, 120, 70, k=11, seed=24), isle('Naath', 2050, -2950, 60, 34, seed=25),
    isle('The Basilisk Isles', 1700, -2880, 70, 30, seed=26), isle('New Ghis', 2240, -2455, 30, 22, seed=27),
] + (DONOR := donor_islands()) + SHORE_ISLES    # Bear Island (the Isle of Man), Skagos (Shetland), the Iron Islands (Orkney),
                                                # the Hebrides and the rest; Ib (Iceland), Valyria's isles (the Cyclades)...
ISLANDS[:] = [i for i in ISLANDS if i['name'] not in SHORE_MADE or i in SHORE_ISLES]

# ---------------------------------------------------------------- the character of the shore
# Each stretch of coast gets a kind, which the terrain turns into its own detail (gen.js coastDetail):
#   fjord - long steep inlets and skerries, as on the coasts of the far north
#   rocky - headlands, coves and sea stacks, cliffs where the land is high
#   beach - smooth sandy shores with barrier islands and spits
#   marsh - low, muddy, wandering shores and tidal flats
# Shores not inside any zone are mixed. Our own reading of how the books describe each coast.
def zone(kind, pts): return {'kind': kind, 'pts': pts}


COAST_ZONES = [
    # beyond the Wall the coast is Scotland's own (sea lochs, skerries); only the Lands of Always Winter, drawn by us,
    # get made-up fjords
    zone('fjord', [[-900, 1150], [900, 1150], [900, 1600], [-900, 1600]]),                # the Lands of Always Winter
    zone('rocky', [[-900, 470], [900, 470], [900, 1150], [-900, 1150]]),                  # beyond the Wall: the Frozen Shore, Hardhome
    zone('rocky', [[-420, 160], [-120, 160], [-120, 470], [-420, 470]]),                  # the Bay of Ice and Bear Island
    zone('rocky', [[-650, -470], [-385, -498], [-380, 160], [-650, 160]]),                # the Stony Shore, Sea Dragon Point
    zone('rocky', [[297, -208], [600, -201], [600, 420], [300, 420]]),                    # the North's east coast, Widow's Watch
    zone('rocky', [[-372, -778], [-276, -887], [-332, -706], [-432, -596]]),              # the Iron Islands
    zone('rocky', [[-337, -680], [-325, -740], [-247, -465], [-382, -428]]),              # Cape Kraken
    zone('rocky', [[-458, -1219], [-381, -1273], [-337, -826], [-395, -768]]),            # the Westerlands' cliffs, the Crag, Fair Isle
    zone('rocky', [[400, -891], [644, -872], [638, -486], [378, -573]]),                  # the Fingers
    zone('rocky', [[436, -1060], [548, -1039], [515, -983], [401, -1003]]),              # Crackclaw Point
    zone('rocky', [[350, -1650], [609, -1649], [644, -1323], [364, -1329]]),              # Shipbreaker Bay, Storm's End, Tarth, Cape Wrath
    zone('rocky', [[459, -1131], [517, -1117], [515, -1070], [456, -1087]]),              # Dragonstone
    zone('beach', [[-571, -2640], [-363, -2397], [-344, -1472], [-622, -1396]]),          # the Reach's coast, the Shield Islands, the Arbor
    zone('beach', [[-276, -2723], [600, -2620], [602, -2252], [-299, -2262]]),            # Dorne's south coast
    zone('beach', [[34, -2058], [721, -2122], [720, -1991], [14, -1943]]),                  # Dorne's north shore on the Sea of Dorne
    zone('marsh', [[-262, -740], [174, -629], [156, -312], [-135, -311]]),                # the Neck, Blazewater Bay
    zone('marsh', [[269, -993], [344, -985], [338, -916], [270, -917]]),                  # the Trident's mouth, Saltpans
    zone('marsh', [[1285, -2140], [1305, -2100], [1365, -2092], [1412, -2140], [1440, -2222], [1395, -2222]]),  # the delta of the Rhoyne
]

# ---------------------------------------------------------------- the style of each mountain range
# measured against its Earth analogue (docs/geodyssey/got/EARTH_ANALOGUES.md, tools/refs/analogues.py):
#   dry    - rises sharply from flat, low plains, few foothills (the Hajar, the Sierra Nevada's east face, Yemen)
#   alpine - sharp, glaciated, deeply cut (the Bernese Alps)
TERRAIN_STYLE = {'The Red Mountains': 'dry', 'The Bones': 'dry', 'Mountains of the Shadow': 'dry',
                 'Mountains of the Moon': 'alpine', 'The Frostfangs': 'alpine'}


def terrain_zones():
    from shapely.geometry import LineString
    out = []
    for r in RANGES:
        k = TERRAIN_STYLE.get(r['name'])
        if not k: continue
        g = LineString(r['pts']).buffer(r.get('w', 60) / 2 + 40)
        out.append({'kind': k, 'pts': [[round(x, 1), round(y, 1)] for x, y in list(g.exterior.coords)[:-1]]})
    return out


# ---------------------------------------------------------------- relief
RANGES = [
    {'name': 'The Frostfangs', 'h': 3000, 'w': 50, 'label': True, 'pts': [[-300, 560], [-250, 700], [-210, 850], [-190, 1000]]},
    {'name': 'Mountains of the Moon', 'h': 3400, 'w': 60, 'label': True, 'pts': [[241, -653], [303, -705], [362, -773], [408, -843], [402, -913]]},
    {'name': 'The Red Mountains', 'h': 3000, 'w': 55, 'label': True, 'pts': [[-281, -2250], [-159, -2132], [-7, -2069], [70, -2050]]},
    {'name': 'The Bones', 'alt': 'The Bone Mountains', 'h': 3600, 'w': 80, 'label': True, 'pts': [[3020, -900], [3060, -1300], [3110, -1700], [3160, -2100]]},
    {'name': 'Mountains of the Shadow', 'h': 4200, 'w': 70, 'label': True, 'pts': [[4880, -2250], [5000, -2400], [5120, -2520]]},
    {'name': 'The Velvet Hills', 'h': 1500, 'w': 50, 'label': False, 'pts': [[915, -800], [945, -900], [960, -990]]},
]
HILLS = [
    {'name': 'The Westerlands hills', 'h': 2700, 'w': 50, 'pts': [[-293, -895], [-266, -995], [-271, -1100]]},
    {'name': 'The Barrowlands', 'h': 260, 'w': 30, 'pts': [[-121, -201], [-64, -260]]},
    {'name': 'The Dornish Marches', 'h': 2200, 'w': 30, 'pts': [[-208, -1994], [63, -1980]]},
]
PEAKS = [
    {'name': 'Dragonmont', 'alt': 'the smoking mountain of Dragonstone', 'x': 488, 'y': -1087, 'h': 1100, 'r': 9, 'kind': 'volcano'},
    {'name': 'The Giant\'s Lance', 'alt': 'with the Eyrie on its shoulder', 'x': 368, 'y': -773, 'h': 4300, 'r': 14, 'kind': 'mountain'},
    {'name': 'The Mother of Mountains', 'alt': 'above Vaes Dothrak', 'x': 2700, 'y': -985, 'h': 1500, 'r': 12, 'kind': 'mountain'},
    {'name': 'The Fourteen Flames', 'alt': 'the fires of the Doom', 'x': 1790, 'y': -2560, 'h': 2600, 'r': 14, 'kind': 'volcano'},
]

# ---------------------------------------------------------------- water
RIVERS = [
    {'name': 'The White Knife', 'w0': 20, 'w1': 160, 'rank': 3, 'pts': [[60, -80], [100, -150], [148, -230], [180, -293]]},
    {'name': 'The Last River', 'w0': 20, 'w1': 140, 'rank': 3, 'pts': [[60, 280], [160, 330], [300, 380]]},
    {'name': 'The Milkwater', 'w0': 20, 'w1': 140, 'rank': 3, 'pts': [[-172, 940], [-160, 800], [-200, 640], [-250, 560]]},
    {'name': 'The Green Fork', 'w0': 30, 'w1': 220, 'rank': 2, 'pts': [[62, -565], [21, -635], [46, -740], [112, -835], [173, -892]]},
    {'name': 'The Blue Fork', 'w0': 30, 'w1': 200, 'rank': 3, 'pts': [[192, -671], [154, -768], [173, -892]]},
    {'name': 'The Red Fork', 'w0': 30, 'w1': 220, 'rank': 2, 'pts': [[-212, -974], [-140, -938], [-41, -901], [76, -886], [173, -892]]},
    {'name': 'The Trident', 'w0': 220, 'w1': 420, 'rank': 1, 'pts': [[173, -892], [225, -930]]},
    {'name': 'The Blackwater Rush', 'w0': 40, 'w1': 380, 'rank': 1, 'pts': [[-233, -1137], [-86, -1210], [72, -1266], [227, -1299]]},
    {'name': 'The Mander', 'w0': 40, 'w1': 420, 'rank': 1, 'pts': [[130, -1411], [-24, -1479], [-140, -1694], [-236, -1841], [-342, -1787], [-392, -1705]]},
    {'name': 'The Honeywine', 'w0': 20, 'w1': 200, 'rank': 3, 'pts': [[-348, -1967], [-403, -2024], [-426, -2153]]},
    {'name': 'The Torrentine', 'w0': 20, 'w1': 160, 'rank': 3, 'pts': [[-168, -2205], [-201, -2300], [-219, -2404]]},
    {'name': 'The Greenblood', 'w0': 30, 'w1': 260, 'rank': 2, 'pts': [[109, -2250], [294, -2346], [518, -2393]]},
    # the Rhoyne begins where the Upper and the Little Rhoyne meet, south-east of Ghoyan Drohe; the Noyne joins it above
    # Ny Sar, the Qhoyne at Dagger Lake, the Lhorulu at the Sorrows (Chroyane), the Selhoru at Selhorys and the Volaena
    # just above Volantis, and it reaches the Summer Sea by four mouths, Volantis on the easternmost (ADWD, TWOIAF).
    # Our own courses through the towns' positions; `to` names the river a tributary joins, `of` the river a delta
    # channel leaves (join_tree() ends each on its parent's final course).
    {'name': 'The Rhoyne', 'alt': 'the Mother Rhoyne', 'w0': 320, 'w1': 900, 'rank': 1,
     'pts': [[1170, -1095], [1195, -1125], [1240, -1195], [1290, -1250], [1302, -1300], [1305, -1345], [1300, -1420],
             [1300, -1500], [1325, -1630], [1350, -1760], [1352, -1860], [1353, -1939], [1361, -2010], [1356, -2075],
             [1365, -2115], [1392, -2150], [1412, -2178], [1420, -2205]]},
    {'name': 'The Upper Rhoyne', 'w0': 30, 'w1': 260, 'rank': 2, 'to': 'The Rhoyne',
     'pts': [[832, -613], [900, -660], [1000, -720], [1080, -830], [1120, -960], [1170, -1095]]},
    {'name': 'The Little Rhoyne', 'w0': 20, 'w1': 150, 'rank': 3, 'to': 'The Rhoyne',
     'pts': [[974, -952], [978, -1000], [985, -1040], [1060, -1080], [1170, -1095]]},
    {'name': 'The Noyne', 'w0': 30, 'w1': 230, 'rank': 2, 'to': 'The Rhoyne',
     'pts': [[1185, -720], [1150, -850], [1170, -960], [1190, -1060], [1195, -1125]]},
    {'name': 'The Qhoyne', 'w0': 30, 'w1': 260, 'rank': 2, 'to': 'The Rhoyne',
     'pts': [[1500, -930], [1450, -1000], [1420, -1080], [1385, -1140], [1375, -1160], [1340, -1210], [1292, -1255]]},
    {'name': 'The Darkwash', 'w0': 20, 'w1': 140, 'rank': 3, 'to': 'The Qhoyne',
     'pts': [[1352, -726], [1360, -850], [1370, -1000], [1385, -1140]]},
    {'name': 'The Lhorulu', 'w0': 30, 'w1': 230, 'rank': 2, 'to': 'The Rhoyne',
     'pts': [[1110, -1300], [1180, -1380], [1250, -1450], [1300, -1500]]},
    {'name': 'The Selhoru', 'w0': 20, 'w1': 200, 'rank': 2, 'to': 'The Rhoyne',
     'pts': [[1520, -1300], [1500, -1450], [1450, -1600], [1400, -1700], [1350, -1760]]},
    {'name': 'The Volaena', 'w0': 20, 'w1': 170, 'rank': 3, 'to': 'The Rhoyne',
     'pts': [[1560, -1950], [1500, -2040], [1440, -2120], [1404, -2166]]},
    {'name': 'The Skahazadhan', 'w0': 40, 'w1': 300, 'rank': 2, 'pts': [[2900, -1650], [2800, -1820], [2700, -1960]]},
    # Astapor stands where the Worm reaches Slaver's Bay (ASOS)
    {'name': 'The Worm', 'w0': 20, 'w1': 180, 'rank': 3, 'pts': [[2330, -1990], [2390, -2070], [2456, -2161]]},
]
# the delta of the Rhoyne: three more mouths west of Volantis's (the books name none of them; Sarhoy stood on one)
DISTRIBUTARIES = [
    {'name': 'The Rhoyne, the Sarhoy mouth', 'of': 'The Rhoyne', 'label': False, 'w0': 300, 'w1': 380, 'rank': 2,
     'pts': [[1365, -2115], [1330, -2130], [1298, -2145]]},
    {'name': 'The Rhoyne, the middle mouth', 'of': 'The Rhoyne', 'label': False, 'w0': 260, 'w1': 340, 'rank': 2,
     'pts': [[1365, -2115], [1352, -2140], [1340, -2165]]},
    {'name': 'The Rhoyne, the east mouth', 'of': 'The Rhoyne', 'label': False, 'w0': 260, 'w1': 340, 'rank': 2,
     'pts': [[1365, -2115], [1372, -2150], [1376, -2181]]},
]
RIVERS += DISTRIBUTARIES
# the rivers of the south reach the sea at the coast's named anchors (tools/known/coast_fixed.py)
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coast_fixed import SOUTH as COAST_FIXED
FIXED_AT = {n: list(xy) for n, xy, _, why in COAST_FIXED if why != 'join'}
RIVER_MOUTHS = {'The White Knife': 'White Harbor', 'The Trident': 'The Trident, mouth', 'The Blackwater Rush': 'King\'s Landing',
                'The Mander': 'The Mander, mouth', 'The Honeywine': 'Oldtown', 'The Torrentine': 'Starfall',
                'The Greenblood': 'The Greenblood, mouth'}
for r in RIVERS:
    if r['name'] in RIVER_MOUTHS: r['pts'][-1] = FIXED_AT[RIVER_MOUTHS[r['name']]]
# our own courses, before shores.py gives each river the bends of its Earth analogue (the Rhoyne the Danube's...)
RIVERS_DRAWN_LIST = [{'name': r['name'], 'pts': [list(p) for p in r['pts']]} for r in RIVERS]
for r in RIVERS:
    if r['name'] in SHORES.get('rivers', {}): r['pts'] = SHORES['rivers'][r['name']]
JOIN_RAMP = 40.0      # miles: how much of a tributary's course is drawn over to where its parent's real bends put it


def join_tree():
    """Each tributary ends on the river it joins (`to`) and each delta channel leaves its river (`of`), wherever the
    real bends laid on the larger river put it: the last (or first) JOIN_RAMP miles are drawn over to the nearest point
    of the parent's course, the pull fading to nothing upstream."""
    import numpy as np
    from shapely.geometry import LineString, Point
    by = {r['name']: r for r in RIVERS}
    depth = lambda r: 0 if not (r.get('to') or r.get('of')) else 1 + depth(by[r.get('to') or r.get('of')])
    for r in sorted(RIVERS, key=depth):
        parent = r.get('to') or r.get('of')
        if not parent: continue
        P = np.asarray(r['pts'], float)[::-1 if r.get('of') else 1]
        line = LineString(by[parent]['pts'])
        q = line.interpolate(line.project(Point(*P[-1]))); d = np.array([q.x, q.y]) - P[-1]
        s = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]; ramp = min(JOIN_RAMP, 0.5 * s[-1])
        u = np.clip((s - (s[-1] - ramp)) / ramp, 0, 1)
        P = P + (u * u * (3 - 2 * u))[:, None] * d
        # a tributary ends where it first meets its river, a delta channel starts where it last leaves it
        own = LineString(P); x = own.intersection(line)
        hits = [g for g in ([x] if x.geom_type == 'Point' else getattr(x, 'geoms', [])) if g.geom_type == 'Point']
        first = min((own.project(g) for g in hits), default=own.length)
        if first < own.length - 0.5:
            from shapely.ops import substring
            P = np.asarray(substring(own, 0, first).coords)
        P = P[::-1 if r.get('of') else 1]
        r['pts'] = [[round(x, 2), round(y, 2)] for x, y in P]


join_tree()


def lake_on(name, river, a, b, half):
    """A lake the river runs through, from near a to near b (X, Y), at most `half` miles from its course either side,
    narrowing to the river at both ends."""
    import math
    from shapely.geometry import LineString, Point
    from shapely.ops import substring, unary_union
    line = LineString(next(r['pts'] for r in RIVERS if r['name'] == river))
    s0, s1 = sorted((line.project(Point(*a)), line.project(Point(*b))))
    n = max(8, int((s1 - s0) / 1.0))
    discs = [line.interpolate(s0 + (s1 - s0) * k / n).buffer(max(0.6, half * math.sin(math.pi * k / n) ** 0.7), 16) for k in range(n + 1)]
    g = unary_union(discs).simplify(0.2)
    return {'name': name, 'pts': [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]}


LAKES = [
    {'name': 'The Gods Eye', 'pts': chaikin([[80, -950], [156, -947], [182, -994], [147, -1038], [84, -1033], [62, -992]], 2)},
    {'name': 'The Long Lake', 'pts': chaikin([[30, 180], [60, 185], [62, 215], [36, 220]], 2)},
    lake_on('Dagger Lake', 'The Rhoyne', (1286, -1240), (1306, -1350), 8.0),     # where the Qhoyne joins the Rhoyne (ADWD)
    # the sacred lake below the Mother of Mountains, beside Vaes Dothrak (AGOT); its size and shape are ours
    {'name': 'The Womb of the World', 'pts': chaikin([[2712, -1004], [2731, -1001], [2738, -1012], [2726, -1021], [2709, -1017]], 2)},
]

# ---------------------------------------------------------------- land cover
def area(name, pts, **kw):
    d = {'name': name, 'pts': chaikin(pts, 2)}; d.update(kw); return d

FORESTS = [
    area('The Haunted Forest', [[-200, 480], [150, 480], [250, 700], [0, 900], [-180, 800]], dens=1, dark=0.6),
    area('The Wolfswood', [[-330, 20], [-120, 60], [-80, -120], [-280, -150]], dens=0.9),
    area('The Kingswood', [[248, -1373], [448, -1394], [417, -1526], [255, -1499]], dens=0.9),
    area('The Rainwood', [[403, -1690], [514, -1711], [475, -1802], [346, -1754]], dens=1, dark=0.3),
    area('The Forest of Qohor', [[1300, -950], [1500, -900], [1550, -1150], [1350, -1200]], dens=1, dark=0.4),
    area('The jungles of Sothoryos', [[700, -3200], [3500, -3400], [3600, -4400], [800, -4400]], dens=1, dark=0.5),
]
MARSHES = [area('The Neck', [[-48, -382], [120, -388], [111, -557], [-163, -625]])]
ARID = [
    area('The Dornish sands', [[-45, -2214], [401, -2151], [498, -2345], [188, -2504], [-99, -2449]], v=0.9),
    area('The Red Waste', [[2800, -1600], [3150, -1600], [3300, -2300], [2950, -2400], [2800, -2100]], v=1),
    area('Lhazar', [[2200, -1600], [2750, -1600], [2700, -1900], [2250, -1900]], v=0.45),
]
FARMS = [
    area('The Riverlands', [[-310, -840], [258, -717], [313, -1089], [-163, -1104]], v=0.8),
    area('The Reach', [[-456, -1465], [118, -1441], [90, -1798], [-461, -1966]], v=1),
    area('The Crownlands', [[91, -1158], [317, -1132], [309, -1330], [110, -1347]], v=0.7),
    area('The Westerlands', [[-349, -1010], [-241, -1050], [-271, -1284], [-410, -1261]], v=0.6),
    area('The Winterfell fields', [[-100, 80], [100, 80], [100, -100], [-100, -100]], v=0.4),
    area('The Rhoyne valley', [[1150, -1500], [1450, -1500], [1450, -2150], [1150, -2150]], v=0.8),
]
GRASS = [area('The Dothraki Sea', [[1500, -700], [2600, -700], [2900, -1000], [2900, -1500], [2400, -1600], [1700, -1500], [1500, -1100]], v=1)]
ASH = [area('The Smoking Sea', [[1850, -2560], [2160, -2560], [2160, -2820], [1850, -2820]], v=1)]   # the isles moved from the Cyclades
UPLIFT = []
ICE = [area('The Land of Always Winter', [[-420, 1080], [420, 1080], [420, 1360], [-420, 1360]], v=1)]
RELIEF = []

# ---------------------------------------------------------------- places
# [name, kind, X, Y, people, realm, note (ours), opts]
def P(name, kind, x, y, people, realm, note, **o): return [name, kind, x, y, people, realm, note, o]

PLACES = [
    # the North and the Wall
    P('Winterfell', 'fortress', 0, 0, 'north', 'The North', 'Seat of House Stark, warmed by hot springs, with an ancient godswood and the crypts of the Kings of Winter.', rank=1, culture='northern', r=0.35, pop=2000),
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
    P('Bear Island', 'fortress', -318, 400, 'north', 'The North', 'Island seat of House Mormont.', rank=4),
    P('Torrhen\'s Square', 'fortress', -130, -170, 'north', 'The North', 'Seat of House Tallhart.', rank=4),
    P('Barrowton', 'town', -99, -248, 'north', 'The North', 'Town of the barrowlands beside the First King\'s barrow.', rank=4, culture='northern', r=0.25, pop=2500),
    P('White Harbor', 'port', 177, -286, 'north', 'The North', 'The North\'s great port, seat of House Manderly, at the mouth of the White Knife.', rank=2, culture='stone', r=0.5, pop=12000),
    P('Widow\'s Watch', 'fortress', 500, -110, 'north', 'The North', 'Seat of House Flint on a peninsula of the east coast.', rank=5),
    P('Moat Cailin', 'ruin', 56, -394, 'north', 'The North', 'A ruined fortress guarding the causeway through the Neck.', rank=3),
    P('Greywater Watch', 'fortress', 31, -507, 'crannog', 'The North', 'The moving castle of House Reed in the swamps of the Neck.', rank=4),
    # beyond the Wall
    P('The Fist of the First Men', 'landmark', -40, 600, 'free', 'Beyond the Wall', 'An ancient ring-fort on a hill in the Haunted Forest.', rank=3),
    P('Craster\'s Keep', 'village', 10, 690, 'free', 'Beyond the Wall', 'A wildling holdfast in the Haunted Forest.', rank=4),
    P('Hardhome', 'ruin', 300, 640, 'free', 'Beyond the Wall', 'A ruined wildling town on the coast north-east of the Wall.', rank=3),
    P('Whitetree', 'village', -60, 520, 'free', 'Beyond the Wall', 'An abandoned wildling village around a great weirwood.', rank=5),
    P('The Skirling Pass', 'landmark', -240, 760, 'free', 'Beyond the Wall', 'A high pass through the Frostfangs.', rank=5),
    # the riverlands
    P('The Twins', 'fortress', 32, -623, 'river', 'The Riverlands', 'Twin castles of House Frey on both banks of the Green Fork, joined by a bridge.', rank=2),
    P('Seagard', 'fortress', -304, -849, 'river', 'The Riverlands', 'Seat of House Mallister on Ironman\'s Bay.', rank=4),
    P('Riverrun', 'fortress', -34, -893, 'river', 'The Riverlands', 'Seat of House Tully where the Tumblestone meets the Red Fork.', rank=2),
    P('Harrenhal', 'fortress', 152, -953, 'river', 'The Riverlands', 'The greatest castle ever raised in Westeros, its towers melted by dragonfire.', rank=2),
    P('The Isle of Faces', 'landmark', 117, -990, 'river', 'The Riverlands', 'An island of weirwoods in the Gods Eye.', rank=4),
    P('The Ruby Ford', 'ford', 173, -892, 'river', 'The Riverlands', 'Where the Kingsroad crosses the Trident.', rank=4),
    P('The Inn at the Crossroads', 'village', 187, -938, 'river', 'The Riverlands', 'An inn where the Kingsroad, the River Road and the High Road meet.', rank=4),
    P('Saltpans', 'port', 321, -943, 'river', 'The Riverlands', 'A small port on the Bay of Crabs.', rank=5),
    P('Maidenpool', 'port', 294, -976, 'river', 'The Riverlands', 'A port town on the Bay of Crabs.', rank=4),
    P('Stoney Sept', 'town', 35, -1082, 'river', 'The Riverlands', 'A walled town in the southern riverlands.', rank=4, culture='northern', r=0.25, pop=3000),
    P('Raventree Hall', 'fortress', -26, -814, 'river', 'The Riverlands', 'Seat of House Blackwood.', rank=5),
    # the Vale
    P('The Eyrie', 'fortress', 362, -777, 'vale', 'The Vale', 'Seat of House Arryn, high on the shoulder of the Giant\'s Lance.', rank=2),
    P('The Bloody Gate', 'fortress', 304, -789, 'vale', 'The Vale', 'The fortified gate at the western entrance of the Vale.', rank=4),
    P('Gulltown', 'port', 522, -863, 'vale', 'The Vale', 'The Vale\'s chief port.', rank=3, culture='stone', r=0.35, pop=8000),
    P('Runestone', 'fortress', 560, -751, 'vale', 'The Vale', 'Seat of House Royce.', rank=4),
    # the Iron Islands
    P('Pyke', 'fortress', -301, -784, 'iron', 'The Iron Islands', 'Seat of House Greyjoy, its towers on sea stacks joined by bridges.', rank=2),
    P('Lordsport', 'port', -295, -773, 'iron', 'The Iron Islands', 'The chief harbour of Pyke.', rank=4),
    P('Ten Towers', 'fortress', -276, -740, 'iron', 'The Iron Islands', 'Seat of House Harlaw.', rank=5),
    P('Nagga\'s Hill', 'landmark', -370, -718, 'iron', 'The Iron Islands', 'The hill on Old Wyk where kings of the ironborn are chosen.', rank=5),
    # the westerlands
    P('Casterly Rock', 'fortress', -399, -1154, 'west', 'The Westerlands', 'Seat of House Lannister, delved into a great rock above the sea.', rank=2),
    P('Lannisport', 'port', -402, -1188, 'west', 'The Westerlands', 'The great port city below Casterly Rock.', rank=2, culture='stone', r=0.6, pop=40000),
    P('The Golden Tooth', 'fortress', -214, -989, 'west', 'The Westerlands', 'Castle guarding the pass between the westerlands and the riverlands.', rank=4),
    P('Ashemark', 'fortress', -267, -1056, 'west', 'The Westerlands', 'Seat of House Marbrand.', rank=5),
    P('The Crag', 'fortress', -335, -942, 'west', 'The Westerlands', 'Seat of House Westerling on the sea.', rank=5),
    # the crownlands
    P('King\'s Landing', 'city', 224, -1302, 'crown', 'The Crownlands', 'The capital of the Seven Kingdoms, on three hills above the Blackwater, crowned by the Red Keep.', rank=1, culture='stone', r=1.4, pop=500000),
    P('The Red Keep', 'landmark', 235.5, -1294.3, 'crown', 'The Crownlands', 'The royal castle on Aegon\'s High Hill.', rank=4),
    P('The Great Sept of Baelor', 'landmark', 227, -1298, 'crown', 'The Crownlands', 'The great sept on Visenya\'s Hill.', rank=5),
    P('Dragonstone', 'fortress', 486, -1093, 'crown', 'The Crownlands', 'Targaryen island fortress beneath the smoking Dragonmont.', rank=2),
    P('High Tide', 'fortress', 434, -1134, 'crown', 'The Crownlands', 'Seat of House Velaryon on Driftmark.', rank=5),
    P('Duskendale', 'port', 320, -1149, 'crown', 'The Crownlands', 'A port town on the coast north of King\'s Landing.', rank=4),
    P('Rosby', 'fortress', 199, -1252, 'crown', 'The Crownlands', 'A castle on the Kingsroad north of the capital.', rank=5),
    # the stormlands
    P('Storm\'s End', 'fortress', 393, -1595, 'storm', 'The Stormlands', 'Seat of House Baratheon, a great drum tower above Shipbreaker Bay.', rank=2),
    P('Bronzegate', 'fortress', 317, -1501, 'storm', 'The Stormlands', 'Seat of House Buckler.', rank=5),
    P('Evenfall Hall', 'fortress', 551, -1518, 'storm', 'The Stormlands', 'Seat of House Tarth on the island of Tarth.', rank=4),
    P('Griffin\'s Roost', 'fortress', 482, -1784, 'storm', 'The Stormlands', 'Seat of House Connington on Cape Wrath.', rank=5),
    P('Summerhall', 'ruin', 216, -1792, 'storm', 'The Stormlands', 'A ruined Targaryen summer palace in the Dornish Marches.', rank=4),
    P('Nightsong', 'fortress', -60, -1960, 'storm', 'The Stormlands', 'Seat of House Caron in the Dornish Marches.', rank=5),
    # the Reach
    P('Highgarden', 'fortress', -231, -1853, 'reach', 'The Reach', 'Seat of House Tyrell on the Mander, amid fields and gardens.', rank=2, culture='stone', r=0.3, pop=3000),
    P('Oldtown', 'city', -425, -2141, 'reach', 'The Reach', 'The oldest city of Westeros, home of the Citadel and the Hightower.', rank=2, culture='stone', r=0.9, pop=100000),
    P('The Hightower', 'tower', -430.2, -2140.9, 'reach', 'The Reach', 'The tallest tower in Westeros, a lighthouse above Oldtown.', rank=3),
    P('The Citadel', 'landmark', -432, -2133, 'reach', 'The Reach', 'The seat of the order of maesters.', rank=4),
    P('Bitterbridge', 'town', -26, -1477, 'reach', 'The Reach', 'A town at the bridge where the Roseroad crosses the Mander.', rank=4),
    P('Goldengrove', 'fortress', -179, -1627, 'reach', 'The Reach', 'Seat of House Rowan.', rank=5),
    P('Horn Hill', 'fortress', -249, -1975, 'reach', 'The Reach', 'Seat of House Tarly.', rank=4),
    P('Tumbleton', 'town', 104, -1427, 'reach', 'The Reach', 'A market town on the Mander.', rank=5),
    P('Brightwater Keep', 'fortress', -412, -1897, 'reach', 'The Reach', 'Seat of House Florent.', rank=5),
    P('Three Towers', 'fortress', -490, -2010, 'reach', 'The Reach', 'Seat of House Costayne.', rank=5),
    P('Ryamsport', 'port', -520, -2453, 'reach', 'The Reach', 'Chief port of the Arbor.', rank=5),
    # Dorne
    P('Sunspear', 'fortress', 588, -2243, 'dorne', 'Dorne', 'Seat of House Martell on the eastern coast of Dorne.', rank=2, culture='sunbaked', r=0.4, pop=10000),
    P('The Water Gardens', 'landmark', 546, -2268, 'dorne', 'Dorne', 'A palace of pools and fountains by the sea.', rank=4),
    P('Planky Town', 'port', 518, -2391, 'dorne', 'Dorne', 'A river port of boats lashed together at the mouth of the Greenblood.', rank=4),
    P('Yronwood', 'fortress', 163, -2212, 'dorne', 'Dorne', 'Seat of House Yronwood.', rank=4),
    P('Starfall', 'fortress', -224, -2372, 'dorne', 'Dorne', 'Seat of House Dayne where the Torrentine meets the sea.', rank=4),
    P('Hellholt', 'fortress', 92, -2411, 'dorne', 'Dorne', 'Seat of House Uller in the sands.', rank=5),
    P('Vaith', 'fortress', 291, -2389, 'dorne', 'Dorne', 'Seat of House Dalt.', rank=5),
    P('Skyreach', 'fortress', -165, -2176, 'dorne', 'Dorne', 'Seat of House Fowler above the Prince\'s Pass.', rank=5),
    # Essos: the Free Cities and the east
    P('Braavos', 'city', 770, -480, 'braavos', 'Braavos', 'City of a hundred islands in a lagoon, guarded by the Titan.', rank=1, culture='lakeside', r=1.2, pop=400000),
    P('The Titan of Braavos', 'wonder', 766, -505, 'braavos', 'Braavos', 'A giant stone and bronze warrior astride the lagoon\'s entrance.', rank=3),
    P('Lorath', 'city', 1240, -246, 'lorath', 'Lorath', 'The northernmost Free City, on islands in the Shivering Sea.', rank=3),
    P('Pentos', 'city', 794, -1120, 'freecity', 'Pentos', 'A Free City across the narrow sea.', rank=2, culture='stone', r=0.9, pop=200000),
    P('Norvos', 'city', 1150, -850, 'freecity', 'Norvos', 'A Free City of bells on the upper Rhoyne.', rank=3),
    P('Qohor', 'city', 1450, -1000, 'freecity', 'Qohor', 'A Free City at the edge of its great forest, famed for its smiths.', rank=3),
    P('Myr', 'city', 905, -1565, 'freecity', 'Myr', 'A Free City known for lace, lenses and crossbowmen.', rank=3),
    P('Tyrosh', 'city', 780, -1722, 'freecity', 'Tyrosh', 'A Free City on an island guarding the narrow sea.', rank=3),
    P('Lys', 'city', 952, -2030, 'freecity', 'Lys', 'A Free City on an island in the Summer Sea.', rank=3),
    P('Volantis', 'city', 1420, -2200, 'freecity', 'Volantis', 'The oldest Free City, astride the mouth of the Rhoyne, with its Black Walls.', rank=2, culture='sunbaked', r=1.2, pop=300000),
    P('Selhorys', 'town', 1350, -1760, 'freecity', 'Volantis', 'A Volantene town on the Rhoyne.', rank=5),
    P('Chroyane', 'ruin', 1300, -1500, 'freecity', 'Volantis', 'A ruined Rhoynar city where the Sorrows mists hang on the river.', rank=5),
    P('Valyria', 'ruin', 1800, -2560, 'valyria', 'Valyria', 'The shattered heart of the Freehold, destroyed in the Doom.', rank=2),
    P('Mantarys', 'town', 2000, -2300, 'valyria', 'Valyria', 'A town on the Demon Road.', rank=5),
    P('Vaes Dothrak', 'city', 2700, -1040, 'dothraki', 'The Dothraki Sea', 'The only city of the Dothraki, beneath the Mother of Mountains.', rank=2, culture='roundhut', r=0.8, pop=20000),
    P('Astapor', 'city', 2452, -2150, 'ghiscari', 'Slaver\'s Bay', 'A slave city of red brick on Slaver\'s Bay.', rank=2, culture='sunbaked', r=0.7, pop=50000),
    P('Yunkai', 'city', 2546, -2052, 'ghiscari', 'Slaver\'s Bay', 'A slave city of yellow brick.', rank=3),
    P('Meereen', 'city', 2702, -1965, 'ghiscari', 'Slaver\'s Bay', 'The greatest of the slave cities, crowned by its Great Pyramid.', rank=2, culture='sunbaked', r=0.9, pop=100000),
    P('New Ghis', 'city', 2240, -2455, 'ghiscari', 'Slaver\'s Bay', 'A Ghiscari city on an island.', rank=4),
    P('Vaes Tolorro', 'ruin', 3050, -2000, 'qarth', 'The Red Waste', 'A dead city in the Red Waste.', rank=5),
    P('Qarth', 'city', 3410, -2590, 'qarth', 'Qarth', 'A rich city on the straits between the Summer Sea and the Jade Sea.', rank=2, culture='sunbaked', r=0.9, pop=150000),
    P('Yin', 'city', 4300, -2000, 'yiti', 'Yi Ti', 'The golden capital of Yi Ti.', rank=4),
    P('Asshai', 'city', 5150, -2650, 'shadow', 'Asshai', 'A city of black stone at the edge of the Shadow.', rank=3),
    P('Ib Nefer', 'port', 2800, -60, 'ib', 'Ib', 'The chief port of Ib.', rank=5),
    P('Tall Trees Town', 'port', -150, -2970, 'summer', 'The Summer Isles', 'A port of the Summer Isles.', rank=4),
    P('Naath', 'landmark', 2050, -2950, 'naath', 'Naath', 'The Isle of Butterflies.', rank=4),
    P('Yeen', 'ruin', 1800, -3500, 'sothoryos', 'Sothoryos', 'A ruined city in the jungles of Sothoryos.', rank=5),
    P('Zamettar', 'ruin', 1500, -3600, 'sothoryos', 'Sothoryos', 'A ruined city of Sothoryos.', rank=5),
]

REGION_LABELS = [
    ['WESTEROS', -149, -926, 'realm', 2, 3.6, 1.6], ['ESSOS', 2600, -1300, 'realm', 1.5, 3.6, 2], ['SOTHORYOS', 2100, -4200, 'realm', 1.5, 4, 2],
    ['THE NORTH', -60, 180, 'realm', 3.4, 7.5, 1.1], ['BEYOND THE WALL', 0, 860, 'realm', 3.4, 7.5, 1.0], ['THE RIVERLANDS', 18, -836, 'realm', 3.6, 7.5, 0.9],
    ['THE VALE', 446, -704, 'realm', 3.6, 7.5, 0.9], ['THE IRON ISLANDS', -323, -834, 'realm', 4, 7.5, 0.8], ['THE WESTERLANDS', -319, -1116, 'realm', 3.6, 7.5, 0.9],
    ['THE CROWNLANDS', 178, -1187, 'realm', 3.8, 7.5, 0.8], ['THE REACH', -265, -1926, 'realm', 3.4, 7.5, 1.1], ['THE STORMLANDS', 309, -1655, 'realm', 3.6, 7.5, 0.9],
    ['DORNE', 198, -2328, 'realm', 3.4, 7.5, 1.1], ['THE DOTHRAKI SEA', 2200, -1100, 'region', 3, 7, 1.1], ['THE RED WASTE', 3050, -2150, 'region', 3.6, 7, 0.9],
    ['LHAZAR', 2450, -1750, 'region', 3.8, 7, 0.8], ['SLAVER\'S BAY', 2550, -2280, 'region', 3.8, 7, 0.8], ['YI TI', 4300, -1800, 'region', 3, 7, 1.1],
    ['THE SHADOW', 5100, -2450, 'region', 3.6, 7, 0.9], ['THE LAND OF ALWAYS WINTER', 0, 1200, 'region', 3, 7, 0.9], ['THE NECK', 34, -466, 'region', 4.5, 8, 0.7],
    ['THE DISPUTED LANDS', 1050, -1720, 'region', 4, 7.5, 0.7],
]
SEA_LABELS = [
    ['The Sunset Sea', -1200, -900, 1.6, 0, 6.5], ['The Narrow Sea', 663, -1022, 1.2, 2.5, 7], ['The Summer Sea', 1200, -2750, 1.6, 0, 6.5],
    ['The Shivering Sea', 2400, 250, 1.4, 0, 6.5], ['The Jade Sea', 4300, -3100, 1.4, 0, 6.5], ['Slaver\'s Bay', 2560, -2150, 0.9, 4, 8.5],
    ['The Bite', 260, -459, 0.9, 4, 8.5], ['Blackwater Bay', 355, -1205, 0.8, 5, 9], ['Shipbreaker Bay', 447, -1487, 0.8, 5, 9],
    ['The Sea of Dorne', 251, -1981, 0.9, 4, 8.5], ['Ironman\'s Bay', -330, -819, 0.9, 4, 8.5], ['The Bay of Ice', -238, 400, 0.8, 4, 8.5],
    ['The Bay of Seals', 300, 470, 0.8, 4, 8.5], ['The Smoking Sea', 1850, -2610, 0.9, 4, 8.5], ['The Bay of Crabs', 405, -934, 0.8, 5, 9],
]

# ---------------------------------------------------------------- realms (coarse; tools/borders/borders.py tightens them)
def R(name, color, pts): return {'name': name, 'color': color, 'pts': pts}
REALMS = {'AC298': [
    R('The North', '#c9d1dc', [[-620, 460], [470, 460], [560, -160], [445, -507], [146, -566], [-169, -632], [-371, -574], [-620, -100]]),
    R('Beyond the Wall', '#dfe8ee', [[-520, 460], [480, 460], [480, 1360], [-520, 1360]]),
    R('The Iron Islands', '#4a4a4a', [[-396, -680], [-257, -680], [-257, -812], [-396, -812]]),
    R('The Riverlands', '#7aa0c8', [[-302, -658], [146, -566], [167, -709], [278, -937], [259, -1083], [50, -1157], [-200, -1053], [-296, -866]]),
    R('The Vale', '#9ab8d8', [[146, -508], [596, -492], [626, -890], [427, -930], [254, -865], [172, -658]]),
    R('The Westerlands', '#c84040', [[-356, -808], [-296, -866], [-200, -1053], [-200, -1277], [-414, -1372]]),
    R('The Crownlands', '#b05050', [[259, -1083], [514, -1001], [528, -1292], [256, -1351], [120, -1257]]),
    R('The Reach', '#6aa04a', [[-459, -1340], [-200, -1277], [141, -1357], [178, -1517], [11, -1937], [-299, -2262], [-547, -2105]]),
    R('The Stormlands', '#d0b040', [[150, -1357], [528, -1292], [590, -1660], [445, -1896], [11, -1937], [178, -1517]]),
    R('Dorne', '#e08a3a', [[-299, -2262], [35, -2035], [302, -2063], [721, -2122], [598, -2395], [238, -2584], [-139, -2602]]),
    R('Braavos', '#5a8ab8', [[700, -380], [1000, -380], [1000, -700], [720, -698]]),
    R('Pentos', '#8a7ab8', [[720, -698], [1050, -700], [1050, -1300], [728, -1288]]),
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
    {'name': 'The Crannogmen', 'lang': 'Common Tongue', 'color': '#5aa05a', 'pts': [[-48, -382], [120, -388], [111, -557], [-163, -625]]},
    {'name': 'The Ironborn', 'lang': 'Common Tongue', 'color': '#808080', 'pts': REALMS['AC298'][2]['pts']},
    {'name': 'The Andals of the south', 'lang': 'Common Tongue', 'color': '#e8b850', 'pts': [[-490, -552], [596, -492], [610, -1659], [30, -1986], [-547, -2105]]},
    {'name': 'Dornishmen', 'lang': 'Common Tongue', 'color': '#ff8a2a', 'pts': REALMS['AC298'][9]['pts']},
    {'name': 'The Free Cities\' folk', 'lang': 'Bastard Valyrian dialects', 'color': '#b07ae0', 'pts': [[700, -380], [1650, -700], [1650, -2250], [850, -2100], [728, -1288]]},
    {'name': 'Dothraki', 'lang': 'Dothraki', 'color': '#e0c85a', 'pts': REALMS['AC298'][16]['pts']},
    {'name': 'Lhazareen', 'lang': 'Lhazarene', 'color': '#a0d07a', 'pts': [[2200, -1600], [2750, -1600], [2700, -1900], [2250, -1900]]},
    {'name': 'Ghiscari', 'lang': 'Ghiscari · Bastard Valyrian', 'color': '#d0503a', 'pts': REALMS['AC298'][17]['pts']},
    {'name': 'Qartheen', 'lang': 'Qartheen', 'color': '#c070e0', 'pts': REALMS['AC298'][18]['pts']},
    {'name': 'Yi Tish', 'lang': 'Yi Tish', 'color': '#f0e070', 'pts': REALMS['AC298'][19]['pts']},
    {'name': 'Ibbenese', 'lang': 'Ibbenese', 'color': '#7a9aa0', 'pts': [[2580, 80], [3020, 80], [3020, -160], [2580, -160]]},
    {'name': 'Summer Islanders', 'lang': 'Summer Tongue', 'color': '#3ac8a0', 'pts': [[-280, -2900], [-20, -2900], [-20, -3040], [-280, -3040]]},
]

ROADS = [
    {'name': 'The Kingsroad', 'cls': 1, 'pts': [[20, 450], [10, 250], [0, 0], [32, -241], [52, -403], [29, -633], [108, -808], [173, -892], [187, -938], [187, -1108], [199, -1252], [235, -1295], [314, -1444], [390, -1591]]},
    {'name': 'The River Road', 'cls': 2, 'pts': [[-400, -1183], [-282, -1053], [-217, -989], [-41, -901], [91, -903], [187, -938]]},
    {'name': 'The High Road', 'cls': 2, 'pts': [[187, -938], [246, -834], [304, -789], [362, -777]]},
    {'name': 'The Gold Road', 'cls': 2, 'pts': [[235, -1295], [30, -1237], [-170, -1215], [-400, -1183]]},
    {'name': 'The Roseroad', 'cls': 2, 'pts': [[235, -1295], [125, -1392], [-24, -1479], [-236, -1841], [-430, -2139]]},
    {'name': 'The Ocean Road', 'cls': 3, 'pts': [[-236, -1841], [-358, -1575], [-400, -1183]]},
    {'name': 'The Boneway', 'cls': 3, 'pts': [[218, -1795], [163, -2026], [162, -2206]]},
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
    """Run each ice wall's ends out (or back) along its line to meet the sea, ending on the shore itself (no gap, no
    overhang): the Wall goes from the Bay of Ice to the Bay of Seals (AGOT)."""
    import math
    for w in WALLS:
        if not w.get('ice'): continue
        for e, q in ((0, 1), (-1, -2)):
            ex, ey = w['pts'][e]; qx, qy = w['pts'][q]; L = math.hypot(ex - qx, ey - qy); dx, dy = (ex - qx) / L, (ey - qy) / L
            d = -L * 0.6
            while not in_poly(ex + dx * d, ey + dy * d, coast) and d < 0: d += 0.25     # if the end is at sea, come back to land
            while in_poly(ex + dx * d, ey + dy * d, coast) and d < 120: d += 0.25       # then out to the shore
            d -= 0.25
            while in_poly(ex + dx * (d + 0.02), ey + dy * (d + 0.02), coast): d += 0.02  # to within a few yards of it
            w['pts'][e] = [round(ex + dx * d, 2), round(ey + dy * d, 2)]
    return WALLS


def settle(places, coast):
    """Put every place on our land: a place out at sea comes ashore at the nearest point of land, a port sits on its own
    waterline, and a place inside a moved city moves with it. Prints each move."""
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union, nearest_points
    land = unary_union([Polygon(coast).buffer(0)] + [Polygon(i['pts']).buffer(0) for i in ISLANDS])
    edge = land.boundary
    def inward(P, depth):
        q = nearest_points(edge, P)[0]
        for k in range(1, 40):                     # step inland from the shore until we are `depth` miles in
            for a in range(0, 360, 15):
                import math
                c = Point(q.x + math.cos(math.radians(a)) * depth * k / 4, q.y + math.sin(math.radians(a)) * depth * k / 4)
                if land.contains(c) and edge.distance(c) >= depth * 0.8: return c
        return q
    moved = {}
    sub = lambda p: p[1] in ('landmark', 'tower') and any(q is not p and q[1] not in ('landmark', 'tower') and
                                                          math_hypot(q[2] - p[2], q[3] - p[3]) < 8 for q in places)
    for p in places:
        if sub(p) or p[1] == 'wonder': continue  # landmarks in a city wait for the city; the Titan stands in the water
        P = Point(p[2], p[3]); d = edge.distance(P); inside = land.contains(P)
        if (p[1] == 'port' or p[0] in ON_SEA) and (not inside or d > 0.8): Q = inward(P, 0.5)
        elif not inside: Q = inward(P, 2.0)
        else: continue
        moved[p[0]] = (Q.x - p[2], Q.y - p[3])
    for p in places:                               # a castle or sept within a moved city goes with it
        if p[0] in moved or not sub(p): continue
        near = sorted((math_hypot(q[2] - p[2], q[3] - p[3]), v) for n, v in moved.items() for q in places if q[0] == n and q[1] not in ('landmark', 'tower'))
        if near and near[0][0] < 8: moved[p[0]] = near[0][1]
    for p in places:
        if p[0] in moved:
            dx, dy = moved[p[0]]; p[2], p[3] = round(p[2] + dx, 1), round(p[3] + dy, 1)
            print(f'  settled {p[0]}: moved {math_hypot(dx, dy):.1f} mi')


# cities the books set on the sea itself, which sit on the waterline like ports
ON_SEA = {'Braavos', 'Pentos', 'Myr', 'Tyrosh', 'Lys', 'Lorath', 'Astapor', 'Yunkai', 'Qarth', 'New Ghis', 'Asshai'}


def math_hypot(a, b):
    import math
    return math.hypot(a, b)


SEA_RIVERS = {'The White Knife', 'The Last River', 'The Milkwater', 'The Trident', 'The Blackwater Rush', 'The Mander',
              'The Honeywine', 'The Torrentine', 'The Greenblood', 'The Rhoyne', 'The Skahazadhan', 'The Worm'}


def river_mouths(coast_s):
    """Every river that reaches the sea ends on the shore: it is trimmed where it first leaves the land, or carried on
    to the nearest shore. The land is never cut (no estuary slits: the coast stays one valid ring and no river runs
    over the sea). Returns the coast unchanged."""
    from shapely.geometry import Polygon, LineString, Point
    from shapely.ops import nearest_points
    main = Polygon(coast_s).buffer(0)
    essos = next(i for i in ISLANDS if i['name'] == 'Essos'); ess = Polygon(essos['pts']).buffer(0)
    for r in RIVERS:
        pts = [tuple(p) for p in r['pts']]; E = Point(pts[-1])
        land = main if main.distance(E) <= ess.distance(E) else ess
        edge = land.boundary
        if r.get('to') or (r['name'] not in SEA_RIVERS and not r.get('of') and edge.distance(E) > 30): continue   # it ends in a lake or another river
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            if land.contains(Point(b)): out.append(b); continue
            x = LineString([a, b]).intersection(edge)
            xs = [x] if x.geom_type == 'Point' else list(getattr(x, 'geoms', []))
            if xs: q = min(xs, key=lambda g: g.distance(Point(a))); out.append((q.x, q.y))
            break
        else:
            q = nearest_points(edge, Point(out[-1]))[0]
            if q.distance(Point(out[-1])) > 0.01: out.append((q.x, q.y))
        r['pts'] = [[round(x, 2), round(y, 2)] for x, y in out]
    return coast_s


def colours(fitted):
    """Each region's ground colour, as a factor on our own colours: its Earth analogue's colour in Blue Marble
    (tools/known/colours.py) relative to the average of all regions, softened. Realms first, then the deserts over them."""
    import math
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'colours.json')
    if not os.path.exists(path): return []
    c = json.load(open(path))
    gm = [math.exp(sum(math.log(max(4, v['rgb'][i])) for v in c.values()) / len(c)) for i in range(3)]
    fac = lambda rgb: [round(min(1.6, max(0.72, (max(4, rgb[i]) / gm[i]) ** 0.35)), 3) for i in range(3)]
    out = []
    for r in fitted:
        if r['name'] in c:
            for part in [r['pts']] + [q for q in r.get('parts', [])]:
                out.append({'name': r['name'], 'f': fac(c[r['name']]['rgb']), 'pts': part})
    for a in ARID:
        if a['name'] in c: out.append({'name': a['name'], 'f': fac(c[a['name']]['rgb']), 'pts': a['pts']})
    return out


def river_towns():
    """A place that stood on one of our drawn rivers stands on its real-shaped course, its landmarks with it."""
    import math
    from shapely.geometry import LineString, Point
    drawn = {r['name']: r['pts'] for r in RIVERS_DRAWN_LIST}
    for r in RIVERS:
        if r['pts'] == drawn.get(r['name']): continue
        old, new = LineString(drawn[r['name']]), LineString(r['pts'])
        for t in PLACES:
            P = Point(t[2], t[3])
            if t[1] in ('landmark', 'tower') or old.distance(P) > 3 or new.distance(P) < 0.5: continue
            q = new.interpolate(new.project(P)); dx, dy = q.x - t[2], q.y - t[3]
            group = [p for p in PLACES if p is t or (p[1] in ('landmark', 'tower') and math.hypot(p[2] - t[2], p[3] - t[3]) < 8)]
            for p in group: p[2], p[3] = round(p[2] + dx, 1), round(p[3] + dy, 1)
            print(f'  {t[0]} stays on {r["name"]} (moved {math.hypot(dx, dy):.1f} mi)')


def on_fixed(places, every=None):
    """A coastal place that is one of the coast's fixed points stands on it, the landmarks within 12 miles with it."""
    import math
    every = every or places
    for t in places:
        if t[0] not in FIXED_AT or t[1] in ('landmark', 'tower', 'region'): continue
        dx, dy = FIXED_AT[t[0]][0] - t[2], FIXED_AT[t[0]][1] - t[3]
        group = [p for p in every if p is t or (p[1] in ('landmark', 'tower') and math.hypot(p[2] - t[2], p[3] - t[3]) < 12)]
        for p in group: p[2], p[3] = round(p[2] + dx, 1), round(p[3] + dy, 1)
        if math.hypot(dx, dy) > 3: print(f'  {t[0]} stands on its fixed point of the coast (moved {math.hypot(dx, dy):.1f} mi)')


# castles the books set over a town: (the town, miles east, miles north)
BESIDE = {'Casterly Rock': ('Lannisport', 2.0, 5.0)}


def prepare():
    """Everything that settles the geography before the cast is built; returns the coast. Used by main() and the checks."""
    river_towns()
    coast_s = river_mouths(westeros_coast())
    snap_walls(coast_s)
    W0, W1 = WALLS[0]['pts'][0], WALLS[0]['pts'][-1]
    from shapely.geometry import LineString as _L, Point as _Pt
    wall = _L(WALLS[0]['pts'])
    for p in PLACES:                                   # the Watch's castles stand on the Wall's line; the end castles a mile in
        if p[0] == 'Eastwatch-by-the-Sea': q = wall.interpolate(wall.length - 0.8)
        elif p[0] == 'Westwatch-by-the-Bridge': q = wall.interpolate(0.8)
        elif p[5] == 'The Wall' and p[4] == 'watch': q = wall.interpolate(wall.project(_Pt(p[2], p[3])))
        else: continue
        p[2], p[3] = round(q.x, 2), round(q.y, 2)
    for p in PLACES:
        if p[0] in CASTLES:
            o = p[7]; c = CASTLES[p[0]]; o['castle'], o['cr'] = c[0], c[1]
            if len(c) > 2: o['cx'], o['cy'] = c[2], c[3]
            if not o.get('culture'): o['culture'], o['r'] = 'castle', o['cr'] + 0.05
    import cast
    have = {p[0] for p in PLACES}
    for name, kind, x, y, people, realm, note, o in cast.EXTRA_PLACES:
        if name not in have: PLACES.append([name, kind, x, y, people, realm, note, o])
    # places that stand on land moved from Earth, or on a real shore's lagoon (tools/known/shores.py)
    pins = {k: v for land in SHORES.values() for k, v in land.get('pins', {}).items()}
    for p in PLACES:
        if p[0] in pins: p[2], p[3] = round(pins[p[0]][0], 1), round(pins[p[0]][1], 1)
    for k in PEAKS:
        if k['name'] in pins: k['x'], k['y'] = round(pins[k['name']][0], 1), round(pins[k['name']][1], 1)
    on_fixed(PLACES)
    # hand-drawn islands give way to the new mainland, then every place settles onto the land
    from shapely.geometry import Polygon
    main_poly = Polygon(coast_s).buffer(0)
    for i in ISLANDS:
        if i['name'] in ('Essos', 'Sothoryos') or i in DONOR: continue
        g = Polygon(i['pts']).buffer(0).difference(main_poly)
        if g.is_empty: i['pts'] = []; continue
        g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
        i['pts'] = [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]
    ISLANDS[:] = [i for i in ISLANDS if len(i['pts']) > 2]
    name_islands()
    settle(PLACES, coast_s)
    from shapely.geometry import Polygon as _P
    from shapely.ops import unary_union as _U
    mouth_towns(_U([_P(coast_s).buffer(0)] + [_P(i['pts']).buffer(0) for i in ISLANDS if i['name'] in ('Essos', 'Sothoryos')]))
    # the gazetteer's places, set against the settled map, then settled themselves
    import gazetteer
    new, moved = gazetteer.resolve(PLACES, RIVERS, WALLS)
    for p in new + [q for q in PLACES if q[0] in moved]:
        if p[7].get('coast'): ON_SEA.add(p[0])
    PLACES.extend(new)
    for p in new + [q for q in PLACES if q[0] in moved]:               # the gazetteer's island castles stand on their islands
        if p[0] in pins: p[2], p[3] = round(pins[p[0]][0], 1), round(pins[p[0]][1], 1)
    on_fixed(new + [q for q in PLACES if q[0] in moved], PLACES)
    settle(new + [q for q in PLACES if q[0] in moved], coast_s)
    for name, (by, dx, dy) in BESIDE.items():                           # a castle the books set over a town
        a = next(p for p in PLACES if p[0] == name); b = next(p for p in PLACES if p[0] == by)
        a[2], a[3] = round(b[2] + dx, 1), round(b[3] + dy, 1)
    settle([p for p in PLACES if p[0] in BESIDE], coast_s)
    the_neck(coast_s)
    seas_on_water(coast_s)
    return coast_s


# the seven Iron Islands, each ring from Orkney named by where it lies (our arrangement; the castles on each follow it)
IRON_ISLANDS = {'Great Wyk': (-364, -771), 'Saltcliffe': (-383, -810), 'Orkmont': (-278, -712), 'Blacktyde': (-337, -702),
                'Old Wyk': (-349, -735), 'Harlaw': (-282, -746), 'Pyke': (-309, -726)}
ONE_POLYGON = ('Skagos', 'Bear Island', 'Tarth', 'Dragonstone', 'Driftmark', 'Estermont', 'The Arbor', 'Fair Isle', 'Bloodstone')
ISLE_OF_CEDARS = (2292, -2364)          # the island at the mouth of Slaver's Bay, on the Gulf of Grief (ADWD)
ISLET_MAX = 10.0                        # sq mi: smaller unnamed islands stay as islets, larger ones go


def name_islands():
    """Every island is named or small (gate rule G5): the Iron Islands one by one, Skagos, Bear Island and the other
    named islands each one polygon, the Isle of Cedars named, and unnamed land of ISLET_MAX sq mi or more removed."""
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    ring = lambda g: [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]
    keep = []
    iron = [i for i in ISLANDS if i['name'] == 'The Iron Islands']
    for i in iron:                                                     # nearest name, one ring each
        c = Polygon(i['pts']).representative_point()
        i['name'] = min(IRON_ISLANDS, key=lambda n: math_hypot(IRON_ISLANDS[n][0] - c.x, IRON_ISLANDS[n][1] - c.y))
    cedars = min((i for i in ISLANDS if i['name'] in (None, 'isle') and Polygon(i['pts']).area >= ISLET_MAX),
                 key=lambda i: Polygon(i['pts']).centroid.distance(Point(*ISLE_OF_CEDARS)), default=None)
    if cedars is not None and Polygon(cedars['pts']).centroid.distance(Point(*ISLE_OF_CEDARS)) < 60: cedars['name'] = 'The Isle of Cedars'
    for name in ONE_POLYGON:
        parts = [i for i in ISLANDS if i['name'] == name]
        if len(parts) < 2: continue
        g = unary_union([Polygon(i['pts']).buffer(0) for i in parts]).buffer(4, join_style=1).buffer(-4, join_style=1)
        gs = sorted(getattr(g, 'geoms', [g]), key=lambda q: -q.area)
        for i in parts: ISLANDS.remove(i)
        ISLANDS.append({'name': name, 'pts': ring(gs[0])})
        ISLANDS.extend({'name': 'islet', 'pts': ring(q)} for q in gs[1:] if q.area < ISLET_MAX)
    for i in list(ISLANDS):
        if i['name'] not in (None, 'isle'): continue
        if Polygon(i['pts']).area >= ISLET_MAX: ISLANDS.remove(i)          # a large leftover the books do not name
        else: i['name'] = 'islet'


def the_neck(coast):
    """The Neck is a wetland on the land, never the sea; Moat Cailin stands on the causeway where the Kingsroad leaves
    the marsh's northern edge (AGOT)."""
    from shapely.geometry import Polygon, LineString, Point
    from shapely.ops import nearest_points
    land = Polygon(coast).buffer(0)
    m = next(x for x in MARSHES if x['name'] == 'The Neck')
    g = Polygon(m['pts']).buffer(0).intersection(land.buffer(-0.3))
    g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
    m['pts'] = [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]
    kr = next(r for r in ROADS if r['name'] == 'The Kingsroad'); road = LineString(kr['pts'])
    x = road.intersection(g.exterior)
    pts = [x] if x.geom_type == 'Point' else list(getattr(x, 'geoms', []))
    if not pts: return
    q = max(pts, key=lambda p: p.y)                                    # the northern edge, where the causeway begins
    mc = next(p for p in PLACES if p[0] == 'Moat Cailin')
    group = [p for p in PLACES if p is mc or (p[1] in ('landmark', 'tower') and math_hypot(p[2] - mc[2], p[3] - mc[3]) < 6)]
    dx, dy = q.x - mc[2], q.y - mc[3]
    for p in group: p[2], p[3] = round(p[2] + dx, 2), round(p[3] + dy, 2)


def seas_on_water(coast):
    """A sea's label sits on its own water, well out from the shore: a label on the land or hard by it moves to the
    point nearby farthest from any shore."""
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    land = unary_union([Polygon(coast).buffer(0)] + [Polygon(i['pts']).buffer(0) for i in ISLANDS if len(i['pts']) > 2])
    for s in SEA_LABELS:
        P = Point(s[1], s[2])
        if not land.contains(P) and land.distance(P) >= 8: continue
        best = None
        for r in range(4, 160, 4):
            for k in range(0, 360, 10):
                import math
                q = Point(s[1] + r * math.cos(math.radians(k)), s[2] + r * math.sin(math.radians(k)))
                if land.contains(q): continue
                d = land.distance(q) - r * 0.08                        # far from the shore, not far from where it was
                if best is None or d > best[0]: best = (d, q)
            if best and best[0] > 12: break
        if best: s[1], s[2] = round(best[1].x), round(best[1].y)


# towns the books put at a river's mouth: each stands on its river's last mile, its landmarks moving with it, and on
# the bank the books give ('left' or 'right' of the stream looking downriver, 'near' for the nearer bank, 'mid' for a
# town that spans the river or floats on it)
MOUTH_TOWNS = {'Planky Town': ('The Greenblood', 'mid'), 'White Harbor': ('The White Knife', 'near'),
               'Oldtown': ('The Honeywine', 'mid'), "King's Landing": ('The Blackwater Rush', 'left'),
               'Volantis': ('The Rhoyne', 'mid'), 'Meereen': ('The Skahazadhan', 'near'), 'Astapor': ('The Worm', 'near')}


def mouth_towns(land=None):
    import math
    from shapely.geometry import Point
    riv = {r['name']: r['pts'] for r in RIVERS}
    for town, (river, bank) in MOUTH_TOWNS.items():
        t = next((p for p in PLACES if p[0] == town), None); pts = riv.get(river)
        if not t or not pts or len(pts) < 2: continue
        (ax, ay), (bx, by) = pts[-2], pts[-1]; L = math.hypot(bx - ax, by - ay) or 1
        X, Y = bx - (bx - ax) / L * 0.8, by - (by - ay) / L * 0.8          # just inside the mouth
        if land is not None and bank != 'mid':                             # then up onto its bank
            nx, ny = -(by - ay) / L, (bx - ax) / L                          # the left bank's side
            def ashore(sgn):
                for k in range(1, 120):
                    q = Point(X + nx * sgn * k * 0.25, Y + ny * sgn * k * 0.25)
                    if land.contains(q) and land.boundary.distance(q) >= 0.6: return k * 0.25, q
                return 1e9, None
            sides = {'left': [1], 'right': [-1], 'near': [1, -1]}[bank]
            d, q = min((ashore(g) for g in sides), key=lambda r: r[0])
            if q is not None: X, Y = q.x, q.y
        dx, dy = X - t[2], Y - t[3]
        if math.hypot(dx, dy) > 80: continue
        group = [p for p in PLACES if p is t or (p[1] in ('landmark', 'tower') and math.hypot(p[2] - t[2], p[3] - t[3]) < 8)]
        for p in group: p[2], p[3] = round(p[2] + dx, 1), round(p[3] + dy, 1)
        print(f'  {town} stands at the mouth of {river} (moved {math.hypot(dx, dy):.1f} mi)')


def main():
    import cast
    coast_s = prepare()
    CAST, JOURNEYS, MODES, EVENTS, BATTLES = cast.build(PLACES, ROADS, STORIES, [coast_s] + [i['pts'] for i in ISLANDS])
    # realm borders fitted to our coasts, ranges, rivers and the Wall; peoples cut to the land
    import realms
    coast = coast_s
    claims = REALMS['AC298']
    fitted = realms.fit(claims, PLACES, coast, ISLANDS, RANGES, RIVERS, WALLS, island_realms={'The Iron Islands'})
    byname = {r['name']: r for r in fitted}
    colour_zones = colours(fitted)
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
        ('COAST', coast_s), ('ISLANDS', ISLANDS), ('COAST_ZONES', COAST_ZONES), ('TERRAIN_ZONES', terrain_zones()), ('COLOUR_ZONES', colour_zones), ('RANGES', RANGES), ('HILLS', HILLS), ('PEAKS', PEAKS),
        ('RIVERS', RIVERS), ('LAKES', LAKES), ('FORESTS', FORESTS), ('MARSHES', MARSHES), ('ARID', ARID), ('FARMS', FARMS),
        ('GRASS', GRASS), ('ASH', ASH), ('UPLIFT', UPLIFT), ('ICE', ICE), ('RELIEF', RELIEF),
        ('PLACES', PLACES), ('REGION_LABELS', REGION_LABELS), ('SEA_LABELS', SEA_LABELS), ('REALMS', REALMS),
        ('ADMIN', ADMIN), ('PEOPLES', PEOPLES), ('ROADS', ROADS), ('WALLS', WALLS),
        ('BEACONS', []), ('JOURNEYS', JOURNEYS),
        ('MODES', MODES), ('BATTLES', BATTLES), ('STORIES', STORIES), ('LORE_WEATHER', []),
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
# grade: text (the novels state it), author (the author's word outside the novels), design (our own choice, kept
# apart so a design call is never mistaken for a fact)
STATEMENTS = [
    {'id': 'wall-long', 'src': 'AGOT', 'grade': 'text', 'conf': 'high', 'claim': 'The Wall runs a hundred leagues, about 300 miles, from the Bay of Ice to the Bay of Seals.', 'test': ['dist', 'Eastwatch-by-the-Sea', 'Westwatch-by-the-Bridge', 300, 0.1]},
    {'id': 'westeros-long', 'src': 'AUTHOR', 'grade': 'author', 'conf': 'medium', 'claim': 'Westeros is about 3,000 miles long from the Wall to Dorne.', 'test': ['south', 'Castle Black', 'Sunspear', 3000, 0.15]},
    {'id': 'north-size', 'src': 'AUTHOR', 'grade': 'design', 'conf': 'low', 'soft': 1,
     'claim': 'The North is said to be about as large as the other kingdoms together. Ours is smaller: a design choice that keeps the published layout south of the Neck.',
     'test': ['areaRatio', 'The North', ['The Riverlands', 'The Vale', 'The Westerlands', 'The Crownlands', 'The Reach', 'The Stormlands', 'Dorne', 'The Iron Islands'], 1.0, 0.2]},
]
# where a place's position comes from (src/sources.js grades): positions south of the North were carried onto the
# published layout once (MAP_V2 §9), so the first list's places there are graded `map`, as is every place standing
# on a named anchor of the coast; places beyond the known coasts are our estimates
FAR_PEOPLES = ('sothoryos', 'yiti', 'shadow', 'naath', 'east', 'ib')
def position_grade(p):
    X, Y, people, realm, o = p[2], p[3], p[4], p[5], p[7]
    if people in FAR_PEOPLES: return 'estimate'
    if p[0] in FIXED_AT: return 'map'
    if o.get('grade'): return o['grade']
    if X < 700 and Y < -160 and realm not in ('The North', 'Beyond the Wall'): return 'map'
    return 'inferred'


def sources_js():
    led = {}
    for p in PLACES:
        name, realm = p[0], p[5]
        b = PLACE_BOOK.get(name) or BOOK_OF.get(realm) or 'AGOT'
        refs = p[7]['src'] if p[7].get('grade') else b + ('; TWOIAF' if b != 'TWOIAF' else '')     # the gazetteer cites its own
        g = position_grade(p)
        if g == 'map' and 'MAP' not in refs: refs += '; MAP'
        led[name] = [g, refs, '', 0]
    # canon tiers (LAWS II.4): 1 the novels, which always win; 2 Tales of Dunk and Egg; 3 the histories (in-world
    # bias, the novels win); provisional: the released Winds of Winter samples; the published maps give positions only
    bib = {
        'AGOT': {'t': 'A Game of Thrones', 'a': 'George R. R. Martin', 'y': 1996, 'kind': 'novel', 'tier': 1, 'cite': 'POV chapter (e.g. Bran I)'},
        'ACOK': {'t': 'A Clash of Kings', 'a': 'George R. R. Martin', 'y': 1998, 'kind': 'novel', 'tier': 1, 'cite': 'POV chapter'},
        'ASOS': {'t': 'A Storm of Swords', 'a': 'George R. R. Martin', 'y': 2000, 'kind': 'novel', 'tier': 1, 'cite': 'POV chapter'},
        'AFFC': {'t': 'A Feast for Crows', 'a': 'George R. R. Martin', 'y': 2005, 'kind': 'novel', 'tier': 1, 'cite': 'POV chapter'},
        'ADWD': {'t': 'A Dance with Dragons', 'a': 'George R. R. Martin', 'y': 2011, 'kind': 'novel', 'tier': 1, 'cite': 'POV chapter'},
        'D&E': {'t': 'Tales of Dunk and Egg (The Hedge Knight, The Sworn Sword, The Mystery Knight)', 'a': 'George R. R. Martin', 'y': 2015, 'kind': 'novellas', 'tier': 2, 'cite': 'novella'},
        'TWOIAF': {'t': 'The World of Ice & Fire', 'a': 'George R. R. Martin, Elio M. Garcia Jr., Linda Antonsson', 'y': 2014, 'kind': 'in-world history', 'tier': 3, 'cite': 'section', 'note': 'Canon told with in-world bias: the novels win.'},
        'FB': {'t': 'Fire & Blood (with The Princess and the Queen, The Rogue Prince, Sons of the Dragon)', 'a': 'George R. R. Martin', 'y': 2018, 'kind': 'in-world history', 'tier': 3, 'cite': 'section', 'note': 'Canon told with in-world bias: the novels win.'},
        'WINDS': {'t': 'The Winds of Winter, released sample chapters', 'a': 'George R. R. Martin', 'y': 0, 'kind': 'sample chapters', 'tier': 'provisional', 'note': 'Provisional, labelled where used; the published books win.'},
        'AUTHOR': {'t': 'The author, outside the novels', 'a': 'George R. R. Martin', 'y': 0, 'kind': 'author statement', 'tier': 'below the novels', 'note': 'Interviews and letters: usable, graded below the novels.'},
        'MAP': {'t': 'The published maps (The Lands of Ice and Fire, 2012; the maps in the novels)', 'a': 'Jonathan Roberts', 'y': 2012, 'kind': 'map', 'tier': 'positions only', 'note': 'Positions of named places only, read on the owner\'s computer; never the line-work.'},
    }
    todo = ['Every place: find the chapter that places it and set chk to 1; pin positions from stated distances and travel times.',
            'Seasons: the dates the Citadel announces autumn and winter (white ravens).',
            'Journeys (Phase 3): an estimated day for every waypoint, synchronised across POV chapters.']
    head = """/* The source ledger for the Known World (generated by tools/known/author.py; edit there).
   Facts only, in our own words (docs/geodyssey/LAWS.md). Grades: text (placed from the novels' words),
   map (position read from a published map; never its line-work), design (our own choice), inferred (our
   placement from the novels' relations), estimate (beyond the known coasts: ours), todo. `chk` is 0 until the
   cited chapter has been checked. SHORES lists the Earth coasts lent to each stretch: illustrative only. */
const SOURCES = (() => {
"""
    shores = {'Westeros, the North': 'Great Britain, bent onto our landmarks (Natural Earth, public domain)',
              'The Iron Islands': 'Orkney (Natural Earth, public domain)'}
    for land in SHORES.values():
        for st in land.get('stretches', []): shores[st['name']] = st['analogue'] + ' (Natural Earth, public domain)'
    body = f'const BIB = {js(bib)};\nconst PLACES = {js(led)};\nconst STATEMENTS = {js(STATEMENTS)};\nconst SHORES = {js(shores)};\nconst TODO = {js(todo)};\n'
    tail = 'return { BIB, PLACES, STATEMENTS, SHORES, TODO };\n})();\nif (typeof self !== "undefined") self.SOURCES = SOURCES;\n'
    open(os.path.join(HERE, '..', '..', 'src', 'sources.js'), 'w').write(head + body + tail)


if __name__ == '__main__':
    main()
    sources_js()
