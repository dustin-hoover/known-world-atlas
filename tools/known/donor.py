"""Westeros's coast from real coastlines: Britain upright for the North, Ireland upside down for the south.

The author has said his Westeros "began as upside down Ireland", and the North's likeness to Britain (with the Wall
near Hadrian's Wall) is well known. We take the real coastlines from Natural Earth (public domain, 1:10 million,
about 2 km between points) and bend them onto our own landmarks with a thin-plate spline: each anchor pairs a real
headland, firth or bay with the feature of Westeros that the books describe there. The real coast supplies the
detail between the anchors; where the books need something Britain and Ireland don't have (the Neck, the Bite,
the Sea of Dorne), the anchors bend the coast to it. No published map of Westeros is used.

Only the North is kept from here now: tools/known/shores.py replaces everything south of the Rills and the Bite with a
coast built through fixed points (tools/known/coast_fixed.py), and drops Ireland's islands. The Iron Islands (Orkney)
are still moved in here.

  python3 tools/known/donor.py              # preview: tools/shots/donor-preview.png (old coast in grey)
  python3 tools/known/donor.py --write      # also write tools/known/coast_donor.json for author.py

Source data: tools/refs/earth/british-isles.json, cut from Natural Earth's ne_10m_land and ne_10m_minor_islands
(see tools/refs/SOURCES.md for how to fetch them).
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, 'tools', 'refs', 'earth', 'british-isles.json')

# anchors: (name, lon, lat) on Earth -> (X, Y) in miles on our map (X east, Y north of Winterfell)
BRITAIN = [
    ('Bowness-on-Solway: the Wall, west end', -3.22, 54.95, -154, 452),
    ('Wallsend: the Wall, east end', -1.53, 54.99, 160, 458),
    ('Tynemouth: Eastwatch, the Bay of Seals', -1.42, 55.02, 167, 462),
    ('Mull of Galloway', -4.86, 54.64, -300, 560),
    ('Mull of Kintyre', -5.80, 55.31, -420, 740),
    ('Ardnamurchan Point', -6.23, 56.73, -480, 930),
    ('Cape Wrath', -5.00, 58.62, -430, 1180),
    ('Dunnet Head', -3.37, 58.67, 150, 1250),
    ('Duncansby Head', -3.03, 58.64, 330, 1200),
    ('Buchan Ness', -1.77, 57.48, 430, 950),
    ('Fife Ness', -2.58, 56.28, 330, 650),
    ('St Abbs Head', -2.14, 55.92, 250, 560),
    ('St Bees Head', -3.64, 54.51, -200, 380),
    ('Morecambe Bay', -3.00, 54.05, -250, 260),
    ('Great Orme', -3.86, 53.34, -330, 180),
    ('Holyhead: Anglesey', -4.69, 53.31, -540, 120),
    ('Bardsey: Sea Dragon Point', -4.78, 52.76, -600, 40),
    ('Aberystwyth: Cardigan Bay', -4.08, 52.41, -500, -40),
    ('Strumble Head', -5.07, 52.03, -440, -160),
    ('St David\'s Head', -5.31, 51.90, -450, -250),
    ('Worms Head', -4.33, 51.57, -318, -354),
    ('Avonmouth: Blazewater Bay', -2.70, 51.50, -48, -382),
    ('Hartland Point', -4.53, 51.02, -250, -498),
    ('Land\'s End: Cape Kraken', -5.72, 50.07, -362, -579),
    ('Lizard Point', -5.20, 49.96, -337, -654),
    ('Flamborough Head', -0.08, 54.12, 420, 250),
    ('Spurn Head', 0.11, 53.58, 440, 160),
    ('The Wash', 0.30, 52.95, 470, 60),
    ('Cromer', 1.30, 52.93, 520, -60),
    ('Lowestoft: Widow\'s Watch', 1.75, 52.48, 545, -150),
    ('Orford Ness', 1.58, 52.08, 479, -203),
    ('Harwich', 1.28, 51.95, 393, -251),
    ('Foulness', 0.95, 51.60, 242, -296),
    ('The Thames: White Harbor', 0.50, 51.48, 180, -297),
    ('Sheppey', 0.90, 51.40, 141, -325),
    ('North Foreland', 1.45, 51.38, 124, -398),
    ('Dover', 1.35, 51.12, 120, -480),
    ('Dungeness', 0.97, 50.91, 166, -556),
]
IRELAND = [
    ('Carnsore Point: Ironman\'s Bay', -6.36, 52.17, -278, -829),
    ('Wexford Harbour: Seagard', -6.40, 52.34, -307, -854),
    ('Wicklow Head', -6.00, 52.96, -305, -854),
    ('Dublin Bay', -6.15, 53.33, -323, -834),
    ('The Boyne', -6.25, 53.72, -323, -866),
    ('Dundalk Bay', -6.35, 53.98, -343, -945),
    ('Carlingford', -6.10, 54.05, -385, -1063),
    ('St John\'s Point: Lannisport', -5.66, 54.23, -398, -1179),
    ('Strangford Lough', -5.55, 54.37, -424, -1309),
    ('Belfast Lough', -5.80, 54.67, -483, -1458),
    ('Fair Head', -6.15, 55.22, -477, -1869),
    ('Rathlin Sound', -6.30, 55.24, -472, -2079),
    ('Malin Head: Starfall', -7.37, 55.38, -218, -2432),
    ('Fanad Head', -7.63, 55.27, 53, -2578),
    ('Bloody Foreland', -8.32, 55.15, 411, -2469),
    ('Rossan Point: Sunspear', -8.80, 54.70, 587, -2240),
    ('Donegal Bay: the Sea of Dorne', -8.20, 54.62, 110, -1956),
    ('Mullaghmore', -8.45, 54.47, 242, -1874),
    ('Erris Head', -10.00, 54.30, 514, -1766),
    ('Achill Head: Cape Wrath', -10.20, 53.97, 554, -1691),
    ('Clew Bay: Shipbreaker Bay', -9.60, 53.80, 388, -1595),
    ('Slyne Head: Massey\'s Hook', -10.23, 53.40, 509, -1335),
    ('Galway Bay: Blackwater Bay', -9.00, 53.20, 227, -1299),
    ('Black Head', -9.27, 53.15, 370, -1119),
    ('Loop Head: Crackclaw Point', -9.93, 52.56, 525, -1028),
    ('The Shannon: the Bay of Crabs', -9.00, 52.60, 297, -975),
    ('Kerry Head', -9.95, 52.42, 467, -1001),
    ('Slea Head: Gulltown', -10.48, 52.10, 526, -858),
    ('Valentia', -10.35, 51.90, 580, -793),
    ('Mizen Head: the Fingers', -9.82, 51.45, 578, -584),
    ('Old Head of Kinsale', -8.53, 51.60, 417, -580),
    ('Cork Harbour', -8.30, 51.80, 315, -596),
    ('Youghal', -7.85, 51.95, 230, -592),
    ('Hook Head', -6.93, 52.12, -61, -686),
]


def km(lon, lat, lat0=54.0):
    return (lon * 111.32 * math.cos(math.radians(lat0)), lat * 110.57)


class TPS:
    """Thin-plate spline from source points to target points (2-D), with a small smoothing term."""
    def __init__(self, src, dst, smooth=0.0):
        P = np.asarray(src, float); Q = np.asarray(dst, float); n = len(P)
        self.c = P.mean(axis=0); self.s = P.std() or 1.0
        P = (P - self.c) / self.s
        K = self._U(np.linalg.norm(P[:, None] - P[None], axis=2)) + smooth * np.eye(n)
        A = np.zeros((n + 3, n + 3)); A[:n, :n] = K; A[:n, n] = 1; A[:n, n + 1:] = P; A[n, :n] = 1; A[n + 1:, :n] = P.T
        b = np.zeros((n + 3, 2)); b[:n] = Q
        self.w = np.linalg.solve(A, b); self.P = P

    @staticmethod
    def _U(r):
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.where(r > 0, r * r * np.log(r), 0.0)

    def __call__(self, pts):
        X = (np.asarray(pts, float) - self.c) / self.s; n = len(self.P)
        U = self._U(np.linalg.norm(X[:, None] - self.P[None], axis=2))
        return U @ self.w[:n] + self.w[n] + X @ self.w[n + 1:]


# whole island groups moved bodily (scaled and turned, not bent): (name, lon range, lat range, centre X, Y, miles per km, turn°)
TRANSPLANTS = [
    ('The Iron Islands', (-3.5, -2.3), (58.65, 59.45), -330, -754, 2.2, 0),     # Orkney
    ('Skagos', (-2.2, -0.6), (59.8, 60.95), 395, 520, 1.05, -15),                # Shetland
]


def transplant(rings):
    out, rest = [], []
    for r in rings:
        lon = np.mean([p[0] for p in r]); lat = np.mean([p[1] for p in r])
        t = next((t for t in TRANSPLANTS if t[1][0] <= lon <= t[1][1] and t[2][0] <= lat <= t[2][1]), None)
        (out if t else rest).append((t, r))
    res = []
    for t in TRANSPLANTS:
        grp = [r for tt, r in out if tt is t]
        if not grp: continue
        P = [np.array([km(lo, la) for lo, la in r]) for r in grp]
        c = np.vstack(P).mean(axis=0); a = math.radians(t[6]); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        for q in P:
            w = ((q - c) @ R.T) * t[5] + np.array([t[3], t[4]])
            res.append({'from': 'transplant', 'name': t[0], 'n': len(q), 'pts': [[round(float(x), 2), round(float(y), 2)] for x, y in w]})
    return res, [r for _, r in rest]


def build():
    rings = json.load(open(SRC))
    moved, rings = transplant(rings)
    def side(r):                    # Ireland lies west of 5.4° W and south of 55.45° N, Britain the rest
        lon = np.mean([p[0] for p in r]); lat = np.mean([p[1] for p in r])
        if lon < -5.45 and lat < 55.45 and not (lon > -6.0 and lat > 54.9): return 'ireland'
        if -5.0 < lon < -4.2 and 54.0 < lat < 54.45: return 'man'          # the Isle of Man
        return 'britain'
    # each anchor is snapped to the nearest point of the real coast, so a headland given roughly still lands on it
    allpts = np.array([km(lo, la) for r in rings for lo, la in r])
    def snap(lo, la):
        q = np.array(km(lo, la)); return tuple(allpts[np.argmin(((allpts - q) ** 2).sum(axis=1))])
    warps = {k: TPS([snap(lo, la) for _, lo, la, _, _ in A], [(x, y) for *_, x, y in A], smooth=1e-5)
             for k, A in (('britain', BRITAIN), ('ireland', IRELAND))}
    out = []
    for r in rings:
        k = side(r)
        w = warps['britain' if k == 'man' else k]
        pts = w([km(lo, la) for lo, la in r])
        out.append({'from': k, 'n': len(r), 'name': 'Bear Island' if k == 'man' else None,
                    'pts': [[round(float(x), 2), round(float(y), 2)] for x, y in pts]})
    return out + moved


# what Britain and Ireland don't have, drawn by us: the Neck joining them, the Lands of Always Winter above Scotland,
# and the Sea of Dorne reaching west between Dorne and the Stormlands
NECK = [[-50, -593], [77, -551], [166, -567], [178, -649], [84, -678], [-47, -697]]
ALWAYS_WINTER = [[-470, 1150], [-430, 1260], [-300, 1340], [-150, 1370], [0, 1350], [150, 1370], [300, 1330], [430, 1260],
                 [470, 1150], [330, 1190], [150, 1215], [-100, 1215], [-300, 1180]]
# Blackwater Bay, opened out from King's Landing to Massey's Hook: one bay, the Blackwater Rush meeting it at the city
BLACKWATER_HEAD = [[222, -1298], [253, -1272], [415, -1137], [443, -1125], [455, -1138], [439, -1209], [441, -1240],
                   [383, -1302], [235, -1342], [222, -1317]]
SEA_OF_DORNE = [[293, -1910], [146, -1887], [41, -1909], [-27, -1929], [-1, -1950], [82, -1994], [190, -2030], [300, -2019]]


def assemble(rings):
    """-> (mainland ring, [island rings]) after joining the pieces and cutting the Sea of Dorne."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    polys = [(r.get('name'), Polygon(r['pts']).buffer(0)) for r in rings if len(r['pts']) > 3]
    land = unary_union([g for _, g in polys] + [Polygon(NECK), Polygon(ALWAYS_WINTER)]).difference(Polygon(SEA_OF_DORNE)).difference(Polygon(BLACKWATER_HEAD))
    # the warp can fold a narrow estuary into slivers: close water gaps and open land threads under about a mile
    land = land.buffer(0.5, join_style=1).buffer(-1.0, join_style=1).buffer(0.5, join_style=1).simplify(0.05)
    parts = sorted(getattr(land, 'geoms', [land]), key=lambda g: -g.area)
    ring = lambda g: [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]
    def name(g):
        for n, q in polys:
            if n and q.intersects(g) and q.intersection(g).area > 0.5 * min(q.area, g.area): return n
        return None
    return ring(parts[0]), [{'name': name(g), 'pts': ring(g)} for g in parts[1:] if g.area > 0.5]


def preview(rings, path):
    from PIL import Image, ImageDraw
    sys.path.insert(0, HERE); import author
    x0, x1, y0, y1, s = -800, 900, -2700, 1500, 0.32
    im = Image.new('RGB', (int((x1 - x0) * s), int((y1 - y0) * s)), (214, 228, 238)); d = ImageDraw.Draw(im)
    f = lambda p: ((p[0] - x0) * s, (y1 - p[1]) * s)
    col = {'britain': (232, 236, 214), 'ireland': (226, 236, 210), 'man': (232, 236, 214)}
    main, isles = assemble(rings)
    for r in [main] + [i['pts'] for i in isles]: d.polygon([f(p) for p in r], fill=(230, 236, 214), outline=(60, 80, 70))
    old = author.chaikin(author.WESTEROS, 2)
    d.line([f(p) for p in old + [old[0]]], fill=(150, 60, 60), width=1)
    for name, lo, la, X, Y in BRITAIN + IRELAND:
        q = f((X, Y)); d.ellipse([q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2], fill=(200, 40, 30))
    im.save(path); print('preview', path, im.size)


if __name__ == '__main__':
    rings = build()
    os.makedirs(os.path.join(ROOT, 'tools', 'shots'), exist_ok=True)
    preview(rings, os.path.join(ROOT, 'tools', 'shots', 'donor-preview.png'))
    if '--write' in sys.argv:
        main, isles = assemble(rings)
        json.dump({'coast': main, 'islands': isles}, open(os.path.join(HERE, 'coast_donor.json'), 'w'))
