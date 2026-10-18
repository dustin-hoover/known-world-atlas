"""Essos and Sothoryos from real shores: each stretch of our own outline takes the detail of a real coast of like
character, and a few real islands and peninsulas are moved bodily (Valyria from the Peloponnese, Ib from Iceland).

Our outline (author.py ESSOS, SOTHORYOS) says where the coast runs, from the books and the official maps' positions.
A real coast (Natural Earth 1:10m, public domain) is laid along it like a ribbon: the real coast is smoothed into a
baseline, each real point is measured as a distance off that baseline, and set the same distance (scaled) off our
outline. Bays, spits, deltas, lagoons and the islands just offshore keep their real shapes; the outline stays ours.
No published map of the Known World is used.

  python3 tools/known/shores.py            # previews: tools/shots/shores-essos.png, tools/shots/shores-sothoryos.png
  python3 tools/known/shores.py --write    # also write tools/known/coast_shores.json for author.py
"""
import os, sys, json, math
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WORLD = os.path.join(ROOT, 'tools', 'refs', 'earth')
OUT = os.path.join(HERE, 'coast_shores.json')

# Each stretch runs from its own start on our outline (X, Y in miles, walking with the land on the left) to the next
# stretch's start, and takes the real coast from one (lon, lat) to the other (whichever way round is shorter; a coast
# walked with the land on its right is laid mirrored).
ESSOS_SHORES = [
    ((950, -360), (13.85, 43.30), (13.85, 44.86), 'the Venetian lagoons and Istria'),                # Braavos
    ((800, -700), (2.15, 41.30), (5.33, 43.28), 'the Costa Brava and the Camargue'),                 # down to Pentos
    ((782, -1122), (17.95, 40.64), (14.99, 42.00), 'Apulia and the Gargano'),                         # Pentos to Myr
    ((905, -1565), (-0.69, 37.63), (0.87, 40.72), 'the Valencian coast, the Orange Blossom Coast'),   # the Disputed Lands
    ((1150, -2100), (32.30, 31.27), (29.90, 31.20), 'the Nile delta'),                                # Volantis, the Rhoyne
    ((1460, -2262), (21.10, 38.33), (22.97, 37.98), 'the north shore of the Gulf of Corinth'),        # facing Valyria
    ((1690, -2398), (26.40, 40.10), (28.27, 36.83), 'the Aegean coast of Anatolia'),                  # the Gulf of Grief
    ((2452, -2150), (49.66, 27.00), (50.83, 28.97), 'the head of the Persian Gulf'),                  # Slaver's Bay
    ((2900, -2400), (45.00, 12.78), (52.23, 15.63), 'the Gulf of Aden'),                              # Qarth
    ((3700, -2560), (52.23, 15.63), (59.80, 22.50), 'the coast of Oman'),                             # the Red Waste's shore
    ((5150, -2660), (113.55, 22.15), (118.70, 24.85), 'the Pearl River and the Guangdong coast'),     # Asshai
    ((5450, -1900), (118.70, 24.85), (122.10, 30.00), 'the coasts of Fujian and Zhejiang'),           # Yi Ti, the Jade Sea
    ((5650, -1100), (131.90, 43.10), (139.00, 47.50), 'the Primorye coast'),                          # the far north-east
    ((5100, -560), (60.60, 69.70), (43.30, 68.65), 'the Pechora Sea'),                                # the Grey Waste
    ((4300, -330), (41.60, 41.60), (29.60, 41.18), 'the Black Sea coast of Anatolia'),               # the Shivering Sea
    ((2800, -160), (21.10, 55.70), (11.00, 54.40), 'the south shore of the Baltic'),                  # facing Ib
    ((1300, -300), (28.05, 59.47), (23.45, 59.20), 'the north coast of Estonia'),                     # Lorath's bay
]
SOTHORYOS_SHORES = [
    ((700, -3150), (-16.75, 12.55), (-7.60, 4.37), 'Guinea and the Bijagos'),                        # the west coast
    ((800, -4500), (-7.60, 4.37), (8.30, 4.60), 'the Gulf of Guinea and the Niger delta'),            # the south coast
    ((2800, -5300), (40.45, -10.47), (45.35, 2.05), 'the Swahili coast'),                            # the east coast
    ((3600, -3600), (147.85, -6.60), (137.90, -1.45), 'the north coast of New Guinea'),               # Naath's shore
    ((2200, -3120), (-74.85, 11.10), (-82.20, 9.30), 'the Caribbean coast of Colombia and Panama'),   # the Basilisk shore
]
# real places whose position, carried along with the coast, becomes a place of ours
PINS = {'Braavos': (12.335, 45.437), 'The Titan of Braavos': (12.418, 45.418)}

SIG = 50.0          # miles: shapes larger than this are our outline's, smaller ones the real coast's
TAPER = 6.0         # miles: the real detail fades in and out at each end of a stretch
ISLE_KM = 45.0      # real islands this close to the real coast come along with it
ISLE_MAX = 3000.0   # ...if smaller than this (km²)

# ------------------------------------------------------------------ Westeros: real detail on the long straight edges
# The North is Britain, stretched to several times its size in places, and our own addition there (the Lands of Always
# Winter) is drawn as a polygon: both leave straight edges miles long. The Lands of Always Winter are laid whole like
# the shores of Essos; every other edge longer than EDGE takes a piece of a real coast of the same character, laid
# along it with its corners held, so Britain's shapes stay. South of the North the coast is built anew from fixed
# points (south_outline, below).
WESTEROS_STRETCHES = [   # (from, to on our coast, real from, real to, what, sig)
    ((470, 1150), (-470, 1150), (-61.7, 56.5), (-64.4, 60.4), 'the fjords of northern Labrador', 45.0),   # the Lands of Always Winter
]
POOLS = {                # real coasts that edges take their pieces from, in turn
    'fjord': ((-61.7, 56.5), (-64.4, 60.4), 'northern Labrador'),
    'rocky': ((-1.5, 48.65), (-2.2, 47.27), 'Brittany'),
    'stony': ((-9.05, 53.25), (-9.85, 53.60), 'Connemara'),
    'marsh': ((4.75, 52.95), (8.4, 55.5), 'the Wadden Sea'),
    'beach': ((-6.3, 36.5), (-8.95, 37.0), 'the Gulf of Cadiz and the Algarve'),
    'dry': ((13.2, 32.9), (10.75, 34.7), 'Tripolitania and the Gulf of Gabes'),
    'kerry': ((-9.95, 52.42), (-9.82, 51.45), 'the Kerry peninsulas'),
}
REGIONS = [              # (pool, X0, X1, Y0, Y1): the first that holds an edge's middle (the North and its islands)
    ('fjord', -2000, 2000, 450, 2000),
    ('rocky', -2000, 2000, -3000, 2000),
]
EDGE = 7.0               # miles

# ------------------------------------------------------------------ Westeros south of the North
# From the Rills round to the North's east coast the coast runs through fixed points: each named feature where the
# official map puts it (tools/known/coast_fixed.py, graded map). Between them the line is ours, a smooth curve, and
# each stretch takes a piece of real coast of its character from POOLS, its corners held (the Fingers, each finger's
# tip and each sound's head a fixed point, from the Kerry peninsulas).
sys.path.insert(0, HERE)
from coast_fixed import SOUTH
KM_PER_MI = 1.0         # real coast taken per mile of ours (its bays and headlands at about real size)


def spline(P, step=0.5):
    """A centripetal Catmull-Rom curve through P, every `step` miles -> (points, the index of each of P in them)."""
    P = np.asarray(P, float); E = np.r_[[2 * P[0] - P[1]], P, [2 * P[-1] - P[-2]]]
    out, at, n0 = [], [], 0
    for i in range(1, len(E) - 2):
        p0, p1, p2, p3 = E[i - 1:i + 3]
        d = [max(np.hypot(*(b - a)), 1e-6) ** 0.5 for a, b in ((p0, p1), (p1, p2), (p2, p3))]
        t0, t1 = 0.0, d[0]; t2 = t1 + d[1]; t3 = t2 + d[2]
        t = np.linspace(t1, t2, max(2, int(np.hypot(*(p2 - p1)) / step) + 1))[:, None]
        A1 = ((t1 - t) * p0 + (t - t0) * p1) / (t1 - t0); A2 = ((t2 - t) * p1 + (t - t1) * p2) / (t2 - t1)
        A3 = ((t3 - t) * p2 + (t - t2) * p3) / (t3 - t2)
        B1 = ((t2 - t) * A1 + (t - t0) * A2) / (t2 - t0); B2 = ((t3 - t) * A2 + (t - t1) * A3) / (t3 - t1)
        C = ((t2 - t) * B1 + (t - t1) * B2) / (t2 - t1)
        at.append(n0); out.append(C[:-1]); n0 += len(C) - 1
    at.append(n0); out.append(P[-1:])
    return np.vstack(out), at


def south_outline():
    """-> (the coast from the Rills round to the North's east coast, [island rings])."""
    from scipy.spatial import cKDTree
    S, at = spline([xy for _, xy, _ in SOUTH])
    sS = np.r_[0, np.cumsum(np.hypot(*np.diff(S, axis=0).T))]; tS = cKDTree(S)
    def room(i0, i1):
        # the nearest coast that is not this stretch (across a bay, a sound or a strait), from the stretch's middle
        m = (i0 + i1) // 2; L = sS[i1] - sS[i0]
        d, j = tS.query(S[m], k=600, distance_upper_bound=90); ok = np.isfinite(d); j = np.minimum(j, len(S) - 1)
        far = ok & (abs(sS[j] - sS[m]) > L / 2 + 6)
        return float(d[far].min()) if far.any() else 90.0
    pieces = {k: piece_of(a, b) for k, (a, b, _) in POOLS.items()}; used = {k: 0 for k in POOLS}
    out, isles = [], []
    for i in range(len(SOUTH) - 1):
        shore, j = SOUTH[i][2], i + 1
        path = S[at[i]:at[j] + 1]; L = sS[at[j]] - sS[at[i]]
        pts, poly, left, lat0, R = pieces[shore]
        need = int(L * KM_PER_MI / 0.4) + 2                            # real coast at about its own size
        o = used[shore] if used[shore] + need < len(R) else 0; used[shore] = o + need + 25
        sub = R[o:o + need]
        ll = np.c_[sub[:, 0] / (111.32 * math.cos(math.radians(lat0))), sub[:, 1] / 110.57]
        rm = room(at[i], at[j])
        sig = max(3.0, min(L / 3, 30.0, rm))
        amp = min(1.0, rm / (3 * sig))                                    # a narrow bay or a finger keeps its width
        c, il, _, _ = lay(path, None, None, sig=sig, taper=min(TAPER, L / 5), piece=(ll, poly, left, lat0, sub),
                          isle_km=8.0 if amp > 0.6 else 0.0, amp=amp)
        out.append(c[:-1]); isles += il
    out.append(S[-1:])
    return np.vstack(out), isles


def westeros(ring, donor_isles=()):
    """-> (coast ring, [{'name', 'pts'}] islands): the North's coast with real detail laid on its long straight edges,
    and the south built anew from its fixed points."""
    ring = np.asarray(ring, float)
    if not Polygon(ring).exterior.is_ccw: ring = ring[::-1]
    sc, sisles = south_outline()                                       # from the Rills round to the North's east coast
    n = len(ring)
    iw = int(np.argmin(((ring - sc[0]) ** 2).sum(1))); ie = int(np.argmin(((ring - sc[-1]) ** 2).sum(1)))
    north = ring[(ie + np.arange((iw - ie) % n + 1)) % n][1:-1]       # round the North from the east join to the west
    ring = np.vstack([north, sc]); n = len(ring)
    isles = [{'name': None, 'pts': q} for q in sisles]
    done = np.zeros(n, bool); done[len(north):] = True; spans = {len(north): np.vstack([sc, sc[-1:]])}
    # the Lands of Always Winter, smoothed (our corners there are only a drawing's) and laid whole
    for a, b, ra, rb, what, sig in WESTEROS_STRETCHES:
        ia = int(np.argmin(((ring - a) ** 2).sum(1))); ib = int(np.argmin(((ring - b) ** 2).sum(1)))
        idx = (ia + np.arange((ib - ia) % n + 1)) % n; done[idx[:-1]] = True
        P = resample(ring[idx], 0.5); P = smooth(P, 20 / 0.5)
        c, il, _, info = lay(P, ra, rb, sig=sig)
        print(f'  Westeros: {what:40s} k={info["k"]:.2f} mi/km, {info["ours_mi"]} mi, {len(il)} islands')
        spans[ia] = c; isles += [{'name': None, 'pts': q} for q in il]
    pieces = {k: piece_of(a, b) for k, (a, b, _) in POOLS.items()}
    at = {k: 0 for k in POOLS}; count = [0]

    def detail(ring, done=None, spans={}):
        """Every edge longer than EDGE takes a piece of real coast from its region's pool, its ends held."""
        n = len(ring); done = np.zeros(n, bool) if done is None else done; out = []; got = []
        from scipy.spatial import cKDTree
        D = resample(np.vstack([ring, ring[:1]]), 0.5); sD = np.arange(len(D)) * 0.5; LD = sD[-1]; tD = cKDTree(D)
        def room(m, sm, L):
            # the nearest coast that is not this stretch of it (across a firth, a sea loch, a strait)
            d, j = tD.query(m, k=200, distance_upper_bound=60); j = np.minimum(j, len(D) - 1)
            far = np.isfinite(d) & (np.minimum(abs(sD[j] - sm), LD - abs(sD[j] - sm)) > L / 2 + 6)
            return float(d[far].min()) if far.any() else 60.0
        s_at = np.r_[0, np.cumsum(np.hypot(*np.diff(ring, axis=0).T))]
        i = 0
        while i < n:
            if i in spans:
                out.append(spans[i][:-1]); i += 1
                while i < n and done[i]: i += 1
                continue
            if done[i]: i += 1; continue
            P, Q = ring[i], ring[(i + 1) % n]; L = math.hypot(*(Q - P))
            if L < EDGE: out.append(P[None]); i += 1; continue
            m = (P + Q) / 2
            pool = next(k for k, x0, x1, y0, y1 in REGIONS if x0 <= m[0] <= x1 and y0 <= m[1] <= y1)
            pts, poly, left, lat0, R = pieces[pool]
            need = int(L * 1.6 / 0.4) + 2                              # about as much real coast as the edge is long
            o = at[pool] if at[pool] + need < len(R) else 0; at[pool] = o + need + 25
            sub = R[o:o + need]
            ll = np.c_[sub[:, 0] / (111.32 * math.cos(math.radians(lat0))), sub[:, 1] / 110.57]
            sig = max(2.0, min(L / 4, 12.0))
            amp = min(1.0, room(m, s_at[i] + L / 2, L) / (3 * sig))     # a narrow sea loch keeps its width
            c, il, _, _ = lay(np.array([P, Q]), None, None, sig=sig, taper=min(TAPER, L / 5),
                              piece=(ll, poly, left, lat0, sub), isle_km=8.0 if amp > 0.6 else 0.0, amp=amp)
            out.append(c[:-1]); got += il; count[0] += 1; i += 1
        return np.vstack(out), got

    coast, il = detail(ring, done, spans)
    isles += [{'name': None, 'pts': q} for q in il]
    for d in donor_isles:                                              # Britain's islands, stretched with it
        r = np.asarray(d['pts'], float)
        if not d.get('name') and r[:, 1].mean() < -150: continue        # Ireland's and the south's: the new coast brings its own
        if not Polygon(r).exterior.is_ccw: r = r[::-1]
        c, _ = detail(r) if len(r) > 3 else (r, [])
        isles.append({'name': d.get('name'), 'pts': c})
    print(f'  Westeros: real detail laid on {count[0]} straight edges')
    return coast, isles


# ------------------------------------------------------------------ rivers: the bends of a real river laid along ours
# our river: (Natural Earth river names, the real reach from (lon, lat) to its mouth (lon, lat), the analogue)
RIVERS = {
    'The White Knife': (['Severn'], (-3.55, 52.45), (-2.70, 51.60), 'the Severn'),
    'The Last River': (['Dalälven'], (15.00, 60.75), (17.30, 60.65), 'the Dalälven below Siljan'),
    'The Milkwater': (['Tornelven'], (19.50, 68.20), (24.15, 65.85), 'the Torne'),
    'The Green Fork': (['Ticino'], (8.85, 45.90), (9.15, 45.15), 'the Ticino'),
    'The Blue Fork': (['Mincio'], (10.70, 45.45), (10.95, 45.06), 'the Mincio'),
    'The Red Fork': (['Drau', 'Mur'], (12.40, 46.75), (18.90, 45.55), 'the Drava'),
    'The Trident': (['Po'], (9.20, 45.10), (12.45, 44.95), 'the lower Po'),
    'The Blackwater Rush': (['Tajo', 'Tejo'], (-3.00, 40.30), (-9.10, 38.70), 'the Tagus'),
    'The Mander': (['Guadalquivir'], (-3.20, 37.95), (-6.35, 36.80), 'the Guadalquivir'),
    'The Honeywine': (['Oued Sebou'], (-4.70, 34.00), (-6.65, 34.27), 'the Sebou'),
    'The Torrentine': (['Moulouya'], (-4.60, 33.00), (-2.33, 35.10), 'the Moulouya'),
    'The Greenblood': (['Nile'], (32.90, 24.10), (31.25, 30.05), 'the Nile below Aswan'),
    'The Rhoyne': (['Danube', 'Donau'], (8.60, 47.95), (29.60, 45.20), 'the Danube'),
    'The Skahazadhan': (['Tigris', 'Shatt al Arab'], (43.10, 36.40), (48.50, 29.95), 'the Tigris'),
}
RSIG, RSIG_MAX = 8.0, 30.0       # miles: bends smaller than this (more on a long river) are the real river's


def real_river(names, src, mouth):
    """The named real river from src to its mouth, as (lon, lat) points."""
    from shapely.ops import linemerge, snap
    if not hasattr(real_river, 'f'):
        real_river.f = json.load(open(os.path.join(WORLD, 'ne_10m_rivers_lake_centerlines.geojson')))['features']
    parts, near = [], box(min(src[0], mouth[0]) - 1.5, min(src[1], mouth[1]) - 1.5, max(src[0], mouth[0]) + 1.5, max(src[1], mouth[1]) + 1.5)
    for ft in real_river.f:                  # the named river near its reach (not another of the same name)
        if (ft['properties'].get('name') or '') in names:
            g = shapely.geometry.shape(ft['geometry'])
            parts += [q for q in getattr(g, 'geoms', [g]) if q.intersects(near)]
    g = unary_union(parts); g = snap(g, g, 0.08)
    if g.geom_type == 'MultiLineString': g = linemerge(g)
    A, Bm = Point(src), Point(mouth)
    line = min(getattr(g, 'geoms', [g]), key=lambda q: q.distance(A) + q.distance(Bm) - 0.01 * q.length)
    a, b = line.project(Point(src)), line.project(Point(mouth))
    sub = shapely.ops.substring(line, min(a, b), max(a, b))
    P = np.array(sub.coords)
    return P if a <= b else P[::-1]


def rivers(ours):
    """-> {name: points}: each of our rivers (author.RIVERS) with the bends of its real analogue."""
    out = {}
    for r in ours:
        if r['name'] not in RIVERS: continue
        names, src, mouth, what = RIVERS[r['name']]
        ll = real_river(names, src, mouth); lat0 = float(ll[:, 1].mean())
        R = resample(km(ll[:, 0], ll[:, 1], lat0), 0.3)
        P = resample(np.asarray(r['pts'], float), 0.5); P = smooth(P, 10 / 0.5)      # our course, its corners rounded
        sig = min(RSIG_MAX, max(RSIG, LineString(P).length / 15))     # a long river keeps bigger real bends
        c, _, _, info = lay(P, None, None, sig=sig, taper=4.0, piece=(ll, None, True, lat0, R), isle_km=0.0)
        c = LineString(c).simplify(0.05)
        out[r['name']] = [[round(x, 2), round(y, 2)] for x, y in c.coords]
        print(f"  {r['name']:20s} {what:24s} k={info['k']:.2f} mi/km, {info['ours_mi']} mi, {len(out[r['name']])} points")
    return out


# ------------------------------------------------------------------ real islands and peninsulas moved bodily
# (name, real land: (lon0, lon1, lat0, lat1) or a polygon in lon/lat, anchor (lon, lat), our (X, Y) for the anchor,
#  miles per km, turn°, role). Role 'attach' joins the land to Essos by a short isthmus at the anchor.
PELOPONNESE = [(21.05, 36.1), (23.9, 36.1), (23.9, 37.85), (23.1, 37.88), (22.95, 37.98), (22.4, 38.2),
               (21.78, 38.315), (21.3, 38.36), (21.05, 38.36)]
TRANSPLANTS = [
    ('Valyria', PELOPONNESE, (22.98, 37.93), (1700, -2420), 1.75, 0, 'attach'),                         # the Peloponnese
    ('The Smoking Sea', (24.2, 26.6, 36.2, 37.7), (25.0, 37.0), (1960, -2690), 1.2, 0, 'island'),      # the Cyclades, Santorini
    ('Ib', (-24.7, -13.2, 63.2, 66.7), (-18.6, 64.9), (2815, 40), 0.9, 0, 'island'),                    # Iceland
    ('Tyrosh', (16.35, 16.95, 43.24, 43.43), (16.65, 43.33), (778, -1722), 1.25, 0, 'island'),          # Brač
    ('Lys', (16.38, 17.25, 43.07, 43.24), (16.8, 43.15), (953, -2029), 0.85, 0, 'island'),              # Hvar
    ('The Stepstones', (15.15, 15.65, 43.66, 43.99), (15.38, 43.82), (772, -2101), 2.4, 40, 'island'),  # the Kornati
    ('Bloodstone', (16.0, 16.28, 42.97, 43.1), (16.15, 43.04), (859, -2050), 2.0, 0, 'island'),         # Vis
    ('Lorath', (21.75, 23.45, 57.85, 59.12), (22.6, 58.5), (1242, -232), 0.5, 0, 'island'),             # Saaremaa, Hiiumaa, Muhu
    ('New Ghis', (14.15, 14.6, 35.78, 36.1), (14.4, 35.92), (2240, -2455), 2.0, 0, 'island'),            # Malta and Gozo
    ('The Basilisk Isles', (-65.1, -64.25, 18.2, 18.8), (-64.7, 18.45), (1700, -2880), 1.2, 0, 'island'),  # the Virgin Islands
    ('Naath', (8.4, 8.98, 3.18, 3.8), (8.7, 3.5), (2050, -2950), 1.7, 90, 'island'),                     # Bioko
    ('The Summer Isles', (-172.85, -171.35, -14.1, -13.4), (-172.1, -13.75), (-150, -2970), 1.6, 0, 'island'),  # Samoa
    # Westeros's own islands, which Britain and Ireland don't give us
    ('Dragonstone', (-18.05, -17.7, 28.43, 28.87), (-17.86, 28.66), (494, -1076), 0.8, 0, 'island'),    # La Palma
    ('Driftmark', (-1.45, -1.15, 45.78, 46.06), (-1.30, 45.92), (443, -1113), 1.8, 0, 'island'),         # Oléron
    ('Claw Isle', (-2.7, -2.5, 49.4, 49.52), (-2.58, 49.46), (552, -1042), 1.8, 0, 'island'),            # Guernsey
    ('Tarth', (27.65, 28.3, 35.85, 36.48), (27.97, 36.17), (557, -1528), 1.2, 36, 'island'),            # Rhodes
    ('Fair Isle', (-2.27, -1.98, 49.15, 49.27), (-2.12, 49.21), (-420, -1042), 2.5, 90, 'island'),       # Jersey
    ('Estermont', (1.15, 1.65, 38.8, 39.15), (1.42, 38.98), (575, -1651), 0.9, 0, 'island'),             # Ibiza
    ('The Arbor', (2.3, 3.5, 39.25, 39.98), (2.98, 39.6), (-526, -2513), 1.2, 0, 'island'),              # Mallorca
    ('The Shield Islands', (6.15, 6.55, 42.97, 43.05), (6.33, 43.01), (-428, -1697), 2.5, 90, 'island'), # the Îles d'Hyères
    ('The Three Sisters', (4.7, 5.6, 53.0, 53.47), (5.1, 53.25), (275, -467), 1.3, -30, 'island'),      # Texel, Vlieland, Terschelling
    ('Lonely Light', (-8.65, -8.5, 57.79, 57.85), (-8.588, 57.817), (-640, -500), 3.0, 0, 'island'),    # St Kilda, far out west
    ('Ghaston Grey', (10.04, 10.11, 42.56, 42.63), (10.077, 42.588), (-270, -2520), 1.5, 0, 'island'),   # Pianosa, a prison isle itself
]


def world_land():
    """Natural Earth land and minor islands as shapely polygons (lon, lat), loaded once."""
    if not hasattr(world_land, 'g'):
        gs = []
        for f in ('ne_10m_land.geojson', 'ne_10m_minor_islands.geojson'):
            for ft in json.load(open(os.path.join(WORLD, f)))['features']:
                g = shapely.geometry.shape(ft['geometry']).buffer(0)
                gs += [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon']
        world_land.g = gs
        world_land.tree = shapely.STRtree(gs)
    return world_land.g


def km(lo, la, lat0):
    return np.c_[np.asarray(lo) * 111.32 * math.cos(math.radians(lat0)), np.asarray(la) * 110.57]


def resample(P, step):
    d = np.hypot(*np.diff(P, axis=0).T); s = np.r_[0, np.cumsum(d)]
    u = np.linspace(0, s[-1], max(2, int(s[-1] / step) + 1))
    return np.c_[np.interp(u, s, P[:, 0]), np.interp(u, s, P[:, 1])]


def smooth(P, sig):
    """Gaussian smoothing along the line (sig in samples), the ends held by odd reflection."""
    k = min(int(3 * sig) + 1, len(P) - 2)
    x = np.arange(-k, k + 1); w = np.exp(-0.5 * (x / sig) ** 2); w /= w.sum()
    pad = np.r_[2 * P[0] - P[k:0:-1], P, 2 * P[-1] - P[-2:-k - 2:-1]]
    return np.c_[np.convolve(pad[:, 0], w, 'valid'), np.convolve(pad[:, 1], w, 'valid')]


def frame(line, s, h):
    L = line.length; s = np.clip(s, 0, L)
    at = lambda u: shapely.get_coordinates(shapely.line_interpolate_point(line, np.clip(u, 0, L)))
    T = at(s + h) - at(s - h); T /= np.maximum(np.hypot(*T.T), 1e-9)[:, None]
    return at(s), T, np.c_[T[:, 1], -T[:, 0]]          # foot, tangent, right-hand normal


def real_coast(a, b):
    """The real coast between a and b (lon, lat): (lon/lat points, its polygon, land_on_left)."""
    world_land()
    A, B = Point(a), Point(b)
    near = world_land.tree.query(A.buffer(0.5))                     # the land nearest both ends, not an islet off one
    i = min(near, key=lambda j: world_land.g[j].distance(A) + world_land.g[j].distance(B)) if len(near) else world_land.tree.nearest(A)
    poly = shapely.geometry.polygon.orient(world_land.g[i], 1.0)
    R = np.array(poly.exterior.coords)[:-1]; n = len(R)
    ia = int(np.argmin(((R - a) ** 2).sum(1))); ib = int(np.argmin(((R - b) ** 2).sum(1)))
    fwd = (ib - ia) % n; back = (ia - ib) % n
    if fwd <= back: idx = (ia + np.arange(fwd + 1)) % n; left = True
    else: idx = (ia - np.arange(back + 1)) % n; left = False
    return R[idx], world_land.g[i], left


def ring_path(ring, a, b):
    """Our ring (CCW) from the vertex nearest a forward to the vertex nearest b."""
    R = np.asarray(ring, float); n = len(R)
    ia = int(np.argmin(((R - a) ** 2).sum(1))); ib = int(np.argmin(((R - b) ** 2).sum(1)))
    return R[(ia + np.arange((ib - ia) % n + 1)) % n]


def piece_of(a, b):
    """The real coast a..b, ready to lay: (lon/lat points, its polygon, land_on_left, lat0, points in km every 0.4 km)."""
    pts, poly, left = real_coast(a, b)
    lat0 = float(pts[:, 1].mean())
    return pts, poly, left, lat0, resample(km(pts[:, 0], pts[:, 1], lat0), 0.4)


def lay(ours, a, b, pins=None, sig=SIG, taper=TAPER, piece=None, isle_km=ISLE_KM, amp=1.0):
    """Lay the real coast a..b (or a piece already cut) along our path;
    -> (mapped coast points, [mapped island rings], {pin: (X, Y)}, info)."""
    pts, poly, left, lat0, R = piece or piece_of(a, b)
    C = LineString(resample(np.asarray(ours, float), 0.5)); Lc = C.length
    k = Lc / LineString(smooth(R, 25 / 0.4)).length                   # first guess at miles per km
    for _ in range(2):
        B = smooth(R, sig / k / 0.4); cB = np.r_[0, np.cumsum(np.hypot(*np.diff(B, axis=0).T))]; k = Lc / cB[-1]
    TAPER = taper
    TB = np.gradient(B, axis=0); TB /= np.maximum(np.hypot(*TB.T), 1e-9)[:, None]; NB = np.c_[TB[:, 1], -TB[:, 0]]
    sea = 1.0 if left else -1.0
    from scipy.spatial import cKDTree
    tree = cKDTree(R)

    def carry(P, idx=None):
        # each real point keeps its offset from the baseline point of the same place along the coast (its own index,
        # or the nearest real coast point's for an island or a pin), in that point's frame
        if idx is None: idx = tree.query(P)[1]
        d = P - B[idx]; n = (d * NB[idx]).sum(1) * sea; t = (d * TB[idx]).sum(1)
        u = cB[idx] * k
        fc, Tc, Nc = frame(C, u, 0.5)
        w = np.clip(np.minimum(u, Lc - u) / TAPER, 0, 1); w = w * w * (3 - 2 * w) * amp
        return fc + (k * w)[:, None] * (n[:, None] * Nc + t[:, None] * Tc)

    def rigid(Q, c):
        # an island moves whole: its centre is carried like the coast, its shape turned with the coast and scaled by k
        j = tree.query(c)[1]; T = TB[j:j + 1]; _, Tc, _ = frame(C, np.array([cB[j] * k]), 0.5)
        if not left: Q = np.c_[Q[:, 0], 2 * c[1] - Q[:, 1]]; T = T * [1, -1]      # mirrored like the coast
        a = math.atan2(Tc[0, 1], Tc[0, 0]) - math.atan2(T[0, 1], T[0, 0])
        M = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]) * k
        return (Q - c) @ M.T + carry(c[None])[0]

    coast = carry(R, np.arange(len(R)))
    # the islands just off this stretch of real coast
    line_ll = LineString(pts); isles = []
    for j in (world_land.tree.query(line_ll.buffer(isle_km / 80)) if isle_km > 0 else []):
        g = world_land.g[j]
        if g.equals(poly) or g is poly: continue
        Q = km(*np.array(g.exterior.coords).T, lat0)
        if Polygon(Q).area > ISLE_MAX or Polygon(Q).area < 0.5: continue
        c = Polygon(Q).representative_point()
        if LineString(R).distance(c) > isle_km: continue
        j = tree.query(np.array(c.coords)[0])[1]
        if cB[j] * k < 2 * TAPER or (cB[-1] - cB[j]) * k < 2 * TAPER: continue
        isles.append(rigid(Q, np.array(c.coords)[0]))
    got = {}
    for name, (lo, la) in (pins or {}).items():
        q = km([lo], [la], lat0)
        if LineString(R).distance(Point(q[0])) < 25: got[name] = carry(q)[0].tolist()
    return coast, isles, got, {'k': round(k, 2), 'mirrored': not left, 'real_km': round(LineString(R).length), 'ours_mi': round(Lc)}


# places that stand on a moved land: (land, real lon, lat). Valyria's ruins on Santorini's drowned caldera,
# the Fourteen Flames on Naxos, the largest of the isles around it; Dragonstone's castle on La Palma's harbour
TRANSPLANT_PINS = {'Valyria': ('The Smoking Sea', (25.43, 36.42)), 'The Fourteen Flames': ('The Smoking Sea', (25.47, 37.07)),
                   'Ib Nefer': ('Ib', (-21.94, 64.15)), 'Lorath': ('Lorath', (22.48, 58.25)), 'New Ghis': ('New Ghis', (14.51, 35.9)),
                   'Tall Trees Town': ('The Summer Isles', (-171.76, -13.83)), 'Dragonstone': ('Dragonstone', (-17.77, 28.68)),
                   'Dragonmont': ('Dragonstone', (-17.87, 28.72)), 'Evenfall Hall': ('Tarth', (28.22, 36.44)),
                   # the castles and towns of Westeros's islands, each on its island's real town or harbour
                   'High Tide': ('Driftmark', (-1.33, 45.95)), 'Spicetown': ('Driftmark', (-1.20, 45.89)),
                   'Claw Isle': ('Claw Isle', (-2.535, 49.455)), 'Greenstone': ('Estermont', (1.435, 38.915)),
                   'Faircastle': ('Fair Isle', (-2.11, 49.19)), 'Ryamsport': ('The Arbor', (2.65, 39.57)),
                   'Vinetown': ('The Arbor', (3.12, 39.84)), 'Starpike': ('The Arbor', (2.95, 39.62)),
                   'Greenshield': ('The Shield Islands', (6.45, 43.03)), 'Greyshield': ('The Shield Islands', (6.385, 43.005)),
                   'Southshield': ('The Shield Islands', (6.20, 43.0)), 'Sisterton': ('The Three Sisters', (5.22, 53.36)),
                   'Lonely Light': ('Lonely Light', (-8.567, 57.81)), 'Ghaston Grey': ('Ghaston Grey', (10.09, 42.585)),
                   # and in the east: Valyria's drowned cities on the Peloponnese, Ib's towns, the isles' ports
                   'Oros': ('Valyria', (22.11, 37.04)), 'Tyria': ('Valyria', (22.80, 37.57)), 'Ib Sar': ('Ib', (-18.09, 65.68)),
                   'Gogossos': ('The Basilisk Isles', (-64.93, 18.34)), 'Lotus Port': ('The Summer Isles', (-172.27, -13.70)),
                   'Last Lament': ('The Summer Isles', (-171.6, -14.02))}


def transplants(pins=None):
    """-> [{'name', 'role', 'anchor', 'pts'}] in our miles; fills `pins` with the moved places."""
    out = []
    world_land()
    for name, clip, (alo, ala), (X, Y), s, turn, role in TRANSPLANTS:
        clip = box(clip[0], clip[2], clip[1], clip[3]) if len(clip) == 4 and not isinstance(clip[0], tuple) else Polygon(clip)
        lat0 = clip.centroid.y; a = math.radians(turn)
        A = km([alo], [ala], lat0)[0]
        def f(P):
            P = P - A
            return np.c_[P[:, 0] * math.cos(a) - P[:, 1] * math.sin(a), P[:, 0] * math.sin(a) + P[:, 1] * math.cos(a)] * s + (X, Y)
        for p, (land, (lo, la)) in TRANSPLANT_PINS.items():
            if land == name and pins is not None: pins[p] = f(km([lo], [la], lat0))[0].tolist()
        for j in world_land.tree.query(clip):
            g = world_land.g[j]
            if role == 'island':                     # whole islands only, never a piece cut by the box
                if not clip.contains(g.representative_point()) or g.area > clip.area: continue
                c = g
            else: c = g.intersection(clip)
            for q in getattr(c, 'geoms', [c]):
                if q.geom_type != 'Polygon' or q.area < 1e-5: continue
                P = f(km(*np.array(q.exterior.coords)[:-1].T, lat0))
                if Polygon(P).area > 0.3: out.append({'name': name, 'role': role, 'anchor': [X, Y], 'pts': P})
    return out


def build(name, ring, shores, pins=None, extra=()):
    """-> (mainland ring, [{'name', 'pts'}] islands, {pin: (X, Y)}) for one land mass."""
    ring = np.asarray(ring, float)
    if not Polygon(ring).exterior.is_ccw: ring = ring[::-1]
    coast, isles, got = [], [], {}
    for i, (start, a, b, what) in enumerate(shores):
        end = shores[(i + 1) % len(shores)][0]
        c, il, g, info = lay(ring_path(ring, start, end), a, b, pins)
        print(f'  {name}: {what:48s} k={info["k"]:.2f} mi/km{" mirrored" if info["mirrored"] else ""}, '
              f'{info["real_km"]} km real for {info["ours_mi"]} mi, {len(il)} islands')
        coast.append(c[:-1]); isles += il; got.update(g)
    land = shapely.make_valid(Polygon(np.vstack(coast)))
    parts = [land] + [shapely.make_valid(Polygon(q)) for q in isles if len(q) > 3]
    named = []
    for t in extra:
        g = shapely.make_valid(Polygon(t['pts'])); parts.append(g); named.append((t['name'], g))
        if t['role'] == 'attach':                                     # a short isthmus to the mainland
            A = Point(t['anchor']); m = shapely.ops.nearest_points(land, A)[0]
            parts.append(LineString([A, m]).buffer(3.5, cap_style=1))
    g = unary_union(parts)
    g = g.buffer(0.5, join_style=1).buffer(-1.0, join_style=1).buffer(0.5, join_style=1).simplify(0.08)
    polys = sorted([q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon'], key=lambda q: -q.area)
    ringify = lambda q: [[round(x, 2), round(y, 2)] for x, y in list(q.exterior.coords)[:-1]]
    def nm(q):
        for n, h in named:
            if h.intersects(q) and h.intersection(q).area > 0.5 * min(h.area, q.area): return n
        return None
    return ringify(polys[0]), [{'name': nm(q), 'pts': ringify(q)} for q in polys[1:] if q.area > 0.4], got


def preview(path, main, isles, box_, old, places, extra=()):
    from PIL import Image, ImageDraw
    x0, x1, y0, y1, s = box_
    im = Image.new('RGB', (int((x1 - x0) * s), int((y1 - y0) * s)), (214, 228, 238)); d = ImageDraw.Draw(im)
    f = lambda p: ((p[0] - x0) * s, (y1 - p[1]) * s)
    for r in [main] + [i['pts'] for i in isles]: d.polygon([f(p) for p in r], fill=(232, 230, 210), outline=(60, 80, 70))
    d.line([f(p) for p in list(old) + [old[0]]], fill=(200, 70, 60), width=1)
    for p in places:
        if x0 < p[2] < x1 and y0 < p[3] < y1 and p[1] in ('city', 'ruin', 'port', 'town', 'wonder'):
            q = f((p[2], p[3])); d.ellipse([q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2], fill=(0, 0, 160)); d.text((q[0] + 3, q[1] - 5), p[0], fill=(0, 0, 100))
    im.save(path); print('preview', path, im.size)


def sheet(path, segs, main, isles, places, cols=4, size=420):
    """One panel per stretch of coast: the new coast filled, our old outline in red."""
    from PIL import Image, ImageDraw
    rows = (len(segs) + cols - 1) // cols
    im = Image.new('RGB', (cols * size, rows * size), (255, 255, 255))
    land = [main] + [i['pts'] for i in isles]
    for n, (what, P) in enumerate(segs):
        x0, y0 = P.min(0) - 40; x1, y1 = P.max(0) + 40; s = (size - 8) / max(x1 - x0, y1 - y0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        tile = Image.new('RGB', (size - 4, size - 4), (214, 228, 238)); d = ImageDraw.Draw(tile)
        f = lambda p: ((p[0] - cx) * s + size / 2 - 2, (cy - p[1]) * s + size / 2 - 2)
        for r in land:
            r = np.asarray(r)
            if r[:, 0].max() < cx - size / s or r[:, 0].min() > cx + size / s or r[:, 1].max() < cy - size / s or r[:, 1].min() > cy + size / s: continue
            d.polygon([f(p) for p in r], fill=(232, 230, 210), outline=(60, 80, 70))
        d.line([f(p) for p in P], fill=(200, 70, 60), width=1)
        for p in places:
            q = f((p[2], p[3]))
            if 0 < q[0] < size and 0 < q[1] < size and p[1] in ('city', 'ruin', 'port', 'town', 'wonder'):
                d.ellipse([q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2], fill=(0, 0, 160)); d.text((q[0] + 3, q[1] - 5), p[0], fill=(0, 0, 100))
        d.text((4, 4), f'{what}  ({int(x1 - x0)} mi across)', fill=(0, 0, 0))
        im.paste(tile, ((n % cols) * size + 2, (n // cols) * size + 2))
    im.save(path); print('sheet', path, im.size)


WZOOMS = {'always-winter': (0, 1250, 500), 'sea-of-dorne': (300, -2080, 260), 'reach': (-420, -1900, 420), 'blackwater': (340, -1200, 200),
          'dorne': (180, -2350, 460), 'north-east': (400, 200, 300), 'neck': (-100, -560, 380), 'westerlands': (-380, -1000, 300),
          'vale': (450, -700, 300), 'south': (0, -1400, 1300)}
ZOOMS = {'braavos': (790, -520, 120), 'valyria': (1700, -2450, 260), 'slavers-bay': (2620, -2150, 260), 'yi-ti': (5450, -1700, 300)}


def run(write=False):
    sys.path.insert(0, HERE); import author
    old = {'Essos': author.chaikin(author.ESSOS, 2), 'Sothoryos': author.chaikin(author.SOTHORYOS, 2)}   # our outlines
    tp = {}; extra = transplants(tp)
    out = {}
    donor = json.load(open(os.path.join(HERE, 'coast_donor.json')))
    wc, wi = westeros(donor['coast'], donor['islands'])
    clean = lambda g: g.buffer(0.5, join_style=1).buffer(-1.0, join_style=1).buffer(0.5, join_style=1).simplify(0.08)
    ringify = lambda q: [[round(x, 2), round(y, 2)] for x, y in list(q.exterior.coords)[:-1]]
    g = clean(unary_union([shapely.make_valid(Polygon(wc))] + [shapely.make_valid(Polygon(i['pts'])) for i in wi if not i['name'] and len(i['pts']) > 3]))
    polys = sorted([q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon'], key=lambda q: -q.area)
    named = []
    for i in wi:                                                       # the named islands (the Iron Islands...) keep their names
        if not i['name'] or len(i['pts']) < 4: continue
        h = clean(shapely.make_valid(Polygon(i['pts'])))
        named += [{'name': i['name'], 'pts': ringify(q)} for q in getattr(h, 'geoms', [h]) if q.geom_type == 'Polygon' and q.area > 0.4]
    out['Westeros'] = {'coast': ringify(polys[0]), 'islands': [{'name': None, 'pts': ringify(q)} for q in polys[1:] if q.area > 0.4] + named}
    print(f"  Westeros: {len(out['Westeros']['coast'])} points, {len(out['Westeros']['islands'])} islands")
    for nm, (cx, cy, half) in WZOOMS.items():
        preview(os.path.join(ROOT, 'tools', 'shots', f'shores-{nm}.png'), out['Westeros']['coast'], out['Westeros']['islands'],
                (cx - half, cx + half, cy - half, cy + half, 700 / (2 * half)), donor['coast'], author.PLACES)
    for name, shores, box_ in (('Essos', ESSOS_SHORES, (600, 5800, -2950, 150, 0.2)),
                               ('Sothoryos', SOTHORYOS_SHORES, (400, 3900, -5500, -2900, 0.25))):
        main, isles, got = build(name, old[name], shores, PINS, extra if name == 'Essos' else ())
        ring = np.asarray(old[name], float)
        if not Polygon(ring).exterior.is_ccw: ring = ring[::-1]
        segs = [(w, ring_path(ring, st, shores[(i + 1) % len(shores)][0])) for i, (st, a, b, w) in enumerate(shores)]
        sheet(os.path.join(ROOT, 'tools', 'shots', f'shores-{name.lower()}-sheet.png'), segs, main, isles, author.PLACES)
        if name == 'Essos': got.update(tp)
        print(f'  {name}: {len(main)} points, {len(isles)} islands, pins {got}')
        out[name] = {'coast': main, 'islands': isles, 'pins': got}
        preview(os.path.join(ROOT, 'tools', 'shots', f'shores-{name.lower()}.png'), main, isles, box_, old[name], author.PLACES)
    for nm, (cx, cy, half) in ZOOMS.items():
        land = out['Essos' if cx > 700 and cy > -2950 else 'Sothoryos']
        preview(os.path.join(ROOT, 'tools', 'shots', f'shores-{nm}.png'), land['coast'], land['islands'],
                (cx - half, cx + half, cy - half, cy + half, 700 / (2 * half)), old['Essos'], author.PLACES)
    out['rivers'] = rivers(author.RIVERS_DRAWN_LIST if hasattr(author, 'RIVERS_DRAWN_LIST') else author.RIVERS)
    if write: json.dump(out, open(OUT, 'w'))
    return out


if __name__ == '__main__':
    run('--write' in sys.argv)
