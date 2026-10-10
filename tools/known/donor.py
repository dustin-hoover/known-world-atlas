"""Westeros's coast from real coastlines: Britain upright for the North, Ireland upside down for the south.

The author has said his Westeros "began as upside down Ireland", and the North's likeness to Britain (with the Wall
near Hadrian's Wall) is well known. We take the real coastlines from Natural Earth (public domain, 1:10 million,
about 2 km between points) and bend them onto our own landmarks with a thin-plate spline: each anchor pairs a real
headland, firth or bay with the feature of Westeros that the books describe there. The real coast supplies the
detail between the anchors; where the books need something Britain and Ireland don't have (the Neck, the Bite,
the Sea of Dorne), the anchors bend the coast to it. No published map of Westeros is used.

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
    ('Bowness-on-Solway: the Wall, west end', -3.22, 54.95, -140, 452),
    ('Wallsend: the Wall, east end', -1.53, 54.99, 152, 458),
    ('Tynemouth: Eastwatch, the Bay of Seals', -1.42, 55.02, 158, 462),
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
    ('Worms Head', -4.33, 51.57, -300, -330),
    ('Avonmouth: Blazewater Bay', -2.70, 51.50, -40, -385),
    ('Hartland Point', -4.53, 51.02, -200, -450),
    ('Land\'s End: Cape Kraken', -5.72, 50.07, -330, -520),
    ('Lizard Point', -5.20, 49.96, -260, -565),
    ('Flamborough Head', -0.08, 54.12, 420, 250),
    ('Spurn Head', 0.11, 53.58, 440, 160),
    ('The Wash', 0.30, 52.95, 470, 60),
    ('Cromer', 1.30, 52.93, 520, -60),
    ('Lowestoft: Widow\'s Watch', 1.75, 52.48, 545, -150),
    ('Orford Ness', 1.58, 52.08, 480, -200),
    ('Harwich', 1.28, 51.95, 400, -230),
    ('Foulness', 0.95, 51.60, 260, -250),
    ('The Thames: White Harbor', 0.50, 51.48, 190, -275),
    ('Sheppey', 0.90, 51.40, 140, -320),
    ('North Foreland', 1.45, 51.38, 112, -400),
    ('Dover', 1.35, 51.12, 104, -480),
    ('Dungeness', 0.97, 50.91, 150, -545),
]
IRELAND = [
    ('Carnsore Point: Ironman\'s Bay', -6.36, 52.17, -110, -690),
    ('Wexford Harbour: Seagard', -6.40, 52.34, -160, -722),
    ('Wicklow Head', -6.00, 52.96, -260, -780),
    ('Dublin Bay', -6.15, 53.33, -360, -830),
    ('The Boyne', -6.25, 53.72, -442, -900),
    ('Dundalk Bay', -6.35, 53.98, -472, -1000),
    ('Carlingford', -6.10, 54.05, -452, -1100),
    ('St John\'s Point: Lannisport', -5.66, 54.23, -402, -1182),
    ('Strangford Lough', -5.55, 54.37, -480, -1300),
    ('Belfast Lough', -5.80, 54.67, -522, -1450),
    ('Fair Head', -6.15, 55.22, -540, -1900),
    ('Rathlin Sound', -6.30, 55.24, -470, -2080),
    ('Malin Head: Starfall', -7.37, 55.38, -232, -2420),
    ('Fanad Head', -7.63, 55.27, 60, -2560),
    ('Bloody Foreland', -8.32, 55.15, 420, -2480),
    ('Rossan Point: Sunspear', -8.80, 54.70, 585, -2238),
    ('Donegal Bay: the Sea of Dorne', -8.20, 54.62, 100, -1990),
    ('Mullaghmore', -8.45, 54.47, 250, -1900),
    ('Erris Head', -10.00, 54.30, 520, -1760),
    ('Achill Head: Cape Wrath', -10.20, 53.97, 562, -1680),
    ('Clew Bay: Shipbreaker Bay', -9.60, 53.80, 372, -1580),
    ('Slyne Head: Massey\'s Hook', -10.23, 53.40, 470, -1380),
    ('Galway Bay: Blackwater Bay', -9.00, 53.20, 244, -1302),
    ('Black Head', -9.27, 53.15, 330, -1160),
    ('Loop Head: Crackclaw Point', -9.93, 52.56, 462, -1100),
    ('The Shannon: the Bay of Crabs', -9.00, 52.60, 300, -960),
    ('Kerry Head', -9.95, 52.42, 430, -1040),
    ('Slea Head: Gulltown', -10.48, 52.10, 525, -858),
    ('Valentia', -10.35, 51.90, 580, -800),
    ('Mizen Head: the Fingers', -9.82, 51.45, 585, -560),
    ('Old Head of Kinsale', -8.53, 51.60, 430, -520),
    ('Cork Harbour', -8.30, 51.80, 320, -545),
    ('Youghal', -7.85, 51.95, 220, -560),
    ('Hook Head', -6.93, 52.12, 0, -640),
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


def build():
    rings = json.load(open(SRC))
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
        out.append({'from': k, 'n': len(r), 'pts': [[round(float(x), 2), round(float(y), 2)] for x, y in pts]})
    return out


# what Britain and Ireland don't have, drawn by us: the Neck joining them, the Lands of Always Winter above Scotland,
# and the Sea of Dorne reaching west between Dorne and the Stormlands
NECK = [[-10, -560], [70, -548], [150, -556], [165, -640], [90, -668], [10, -655]]
ALWAYS_WINTER = [[-470, 1150], [-430, 1260], [-300, 1340], [-150, 1370], [0, 1350], [150, 1370], [300, 1330], [430, 1260],
                 [470, 1150], [330, 1190], [150, 1215], [-100, 1215], [-300, 1180]]
SEA_OF_DORNE = [[300, -1930], [150, -1915], [40, -1935], [-30, -1965], [-20, -2005], [60, -2040], [180, -2050], [300, -2030]]


def assemble(rings):
    """-> (mainland ring, [island rings]) after joining the pieces and cutting the Sea of Dorne."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    polys = [Polygon(r['pts']).buffer(0) for r in rings if len(r['pts']) > 3]
    land = unary_union(polys + [Polygon(NECK), Polygon(ALWAYS_WINTER)]).difference(Polygon(SEA_OF_DORNE))
    parts = sorted(getattr(land, 'geoms', [land]), key=lambda g: -g.area)
    ring = lambda g: [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]
    return ring(parts[0]), [ring(g) for g in parts[1:] if g.area > 0.5]


def preview(rings, path):
    from PIL import Image, ImageDraw
    sys.path.insert(0, HERE); import author
    x0, x1, y0, y1, s = -800, 900, -2700, 1500, 0.32
    im = Image.new('RGB', (int((x1 - x0) * s), int((y1 - y0) * s)), (214, 228, 238)); d = ImageDraw.Draw(im)
    f = lambda p: ((p[0] - x0) * s, (y1 - p[1]) * s)
    col = {'britain': (232, 236, 214), 'ireland': (226, 236, 210), 'man': (232, 236, 214)}
    main, isles = assemble(rings)
    for r in [main] + isles: d.polygon([f(p) for p in r], fill=(230, 236, 214), outline=(60, 80, 70))
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
