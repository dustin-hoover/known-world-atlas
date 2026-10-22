"""The coast of southern Westeros from its named anchors (tools/known/coast_fixed.py) and real Earth coastlines.

Between two anchors the coast is a piece of a real coastline (Natural Earth 1:10m, public domain) of the stretch's
character, turned and scaled so that it runs from the one anchor to the other: its shape between them is Earth's,
not any map's, and the line is ours. A long stretch is laid as several pieces, joined at points on the straight line
between its anchors. Each piece is chosen from many candidates (where it starts on the real coast, its scale, and
its mirror image read backwards) by what it must respect: the places the books set inland stay inland, the ports and
coastal castles stay on the shore, the rivers stay on the land, and no piece crosses another or an island.

  south.build(places, rivers, islands, north) -> (coast points from the west join round to the east join, [pieces])
"""
import os, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# real coasts by character: (from lon/lat, to lon/lat, what); each is walked with the land on the left
POOLS = {
    'rocky': [((-1.5, 48.65), (-2.2, 47.27), 'Brittany'), ((-7.6, 43.73), (-8.9, 42.0), 'Galicia'), ((-70.2, 43.6), (-67.0, 44.8), 'the coast of Maine')],
    'stony': [((-9.05, 53.25), (-9.85, 53.60), 'Connemara'), ((-8.2, 55.2), (-8.6, 54.5), 'Donegal'), ((-9.4, 54.3), (-10.1, 53.9), 'Mayo')],
    'marsh': [((4.75, 52.95), (8.4, 55.5), 'the Wadden Sea'), ((-89.4, 30.3), (-93.8, 29.7), 'the Louisiana marshes')],
    'beach': [((-6.3, 36.5), (-8.95, 37.0), 'the Gulf of Cadiz and the Algarve'), ((-9.2, 38.7), (-8.8, 41.2), 'western Portugal'), ((-5.6, 36.0), (-0.3, 39.4), 'the Spanish Levant')],
    'dry': [((13.2, 32.9), (10.75, 34.7), 'Tripolitania'), ((20.0, 31.0), (22.5, 32.9), 'Cyrenaica'), ((3.0, 36.8), (8.6, 36.95), 'the Algerian coast'),
            ((-109.9, 23.2), (-114.6, 31.6), 'the Gulf of California'), ((-9.8, 30.4), (-6.8, 34.0), 'the Atlantic coast of Morocco')],
    'kerry': [((-9.95, 52.42), (-9.82, 51.45), 'the Kerry peninsulas'), ((-8.6, 51.6), (-9.95, 51.45), 'west Cork')],
}
FALLBACK = {'stony': ['rocky'], 'kerry': ['stony', 'rocky'], 'marsh': ['beach'], 'rocky': ['stony'], 'beach': ['dry', 'marsh'], 'dry': ['beach']}
PIECE = 700.0            # miles: the longest piece; a longer stretch is laid as several
SCALES = (1.0, 1.25, 1.6, 2.0, 2.5, 0.8)   # miles of ours per km of real coast
STEP_KM = 8.0            # how far apart candidate starts are along a real coast
RANK_W = {1: 3.0, 2: 2.5, 3: 2.0, 4: 1.5, 5: 1.0, 6: 1.0}


def lines(char):
    """The real coasts of a character: [(what, points in km every 0.4 km with the land on the left)]."""
    import shores
    if char not in lines.cache:
        out = []
        for a, b, what in POOLS[char]:
            pts, poly, left, lat0, R = shores.piece_of(a, b)
            out.append((what, R if left else R[::-1]))
        lines.cache[char] = out
    return lines.cache[char]
lines.cache = {}


def candidates(A, B, char):
    """Every way a real coast of this character (or a near one) can run from A to B:
    yields (penalty for a borrowed character, what, mapped points)."""
    A, B = np.asarray(A, float), np.asarray(B, float); L = float(np.hypot(*(B - A)))
    zA, zB = complex(*A), complex(*B)
    for pen, c in [(0.0, char)] + [(150.0, f) for f in FALLBACK.get(char, [])]:
        for what, R in lines(c):
            z = R[:, 0] + 1j * R[:, 1]; n = len(z); step = max(1, int(STEP_KM / 0.4))
            arc = np.r_[0, np.cumsum(np.abs(np.diff(z)))]
            for s in SCALES:
                want = L / s
                for i0 in range(0, n, step):
                    d = np.abs(z[i0:] - z[i0])
                    k = np.nonzero(d >= want)[0]
                    if not len(k): break
                    i1 = i0 + int(k[0])
                    if arc[i1] - arc[i0] > 3.2 * want: continue           # a stretch that wraps round a great bay
                    seg = z[i0:i1 + 1]
                    for turned in (False, True):
                        q = np.conj(seg[::-1]) if turned else seg          # its mirror image, read backwards
                        w = zA + (q - q[0]) * (zB - zA) / (q[-1] - q[0])
                        yield pen + 50.0 * abs(math.log(s / 1.2)), f'{what}{" (mirrored)" if turned else ""}', np.c_[w.real, w.imag]


def build(places, rivers, islands, north, anchors, log=print):
    """places: [(name, X, Y, coastal, rank)]; rivers: [[(X, Y)...]] (their last miles left out by the caller);
    islands: rings that must stay clear; north: the rest of the coast (our North), which nothing may cross;
    anchors: [(name, (X, Y), character)] from the west join to the east join."""
    import shapely
    from shapely.geometry import LineString, Polygon, Point
    from shapely.ops import unary_union
    from shapely.prepared import prep
    P = np.array([[p[1], p[2]] for p in places]); coastal = np.array([p[3] for p in places]); rank = np.array([p[4] for p in places])
    Rv = np.vstack([np.asarray(r, float) for r in rivers if len(r)]) if rivers else np.zeros((0, 2))
    blocks = [LineString(north)] + [Polygon(q).buffer(1.5).exterior for q in islands if len(q) > 2]
    walls = unary_union([Polygon(q).buffer(1.5) for q in islands if len(q) > 2] + [LineString(north).buffer(0.3)])
    walls_p = prep(walls)
    out, pieces, done = [], [], []
    # each coastal place belongs to the stretch whose chord it is nearest
    chords = [LineString([anchors[i][1], anchors[i + 1][1]]) for i in range(len(anchors) - 1)]
    own = np.array([int(np.argmin([c.distance(Point(*p)) for c in chords])) for p in P]) if len(P) else np.zeros(0, int)
    rown = np.array([int(np.argmin([c.distance(Point(*p)) for c in chords])) for p in Rv]) if len(Rv) else np.zeros(0, int)
    wt = np.array([RANK_W.get(int(r), 1.0) for r in rank]) if len(P) else np.zeros(0)
    for i in range(len(anchors) - 1):
        (na, A, char), (nb, B, _) = anchors[i], anchors[i + 1]
        A, B = np.asarray(A, float), np.asarray(B, float); L = float(np.hypot(*(B - A)))
        chars = char.split('+') if '+' in char else None
        k = len(chars) if chars else max(1, math.ceil(L / PIECE))
        joins = [A + (B - A) * j / k for j in range(k + 1)]
        for j in range(k):
            a, b = joins[j], joins[j + 1]; l = float(np.hypot(*(b - a)))
            ux, uy = (b - a) / l; nx, ny = -uy, ux                        # along the chord, and to its left (the land)
            D = max(40.0, 0.6 * l)
            rel = lambda Q: np.c_[(Q[:, 0] - a[0]) * ux + (Q[:, 1] - a[1]) * uy, (Q[:, 0] - a[0]) * nx + (Q[:, 1] - a[1]) * ny]
            pr = rel(P) if len(P) else np.zeros((0, 2)); near = (pr[:, 0] > -10) & (pr[:, 0] < l + 10) & (np.abs(pr[:, 1]) < D) if len(P) else np.zeros(0, bool)
            rr = rel(Rv) if len(Rv) else np.zeros((0, 2)); rnear = (rr[:, 0] > 0) & (rr[:, 0] < l) & (np.abs(rr[:, 1]) < D) if len(Rv) else np.zeros(0, bool)
            idx = np.nonzero(near & (own == i))[0]; ridx = np.nonzero(rnear & (rown == i))[0]
            on_isle = np.array([any(Polygon(q).contains(Point(*P[t])) for q in islands if len(q) > 2) for t in idx], bool)
            idx = idx[~on_isle]
            # how far a piece may stray from its chord: no further than the open water in front of it allows
            mid = LineString([a + (b - a) * 0.15, b - (b - a) * 0.15])
            ahead = [LineString([b, B])] if j < k - 1 else []                     # the shores still to come, as their chords
            ahead += [LineString([anchors[m][1], anchors[m + 1][1]]) for m in range(i + 1, len(anchors) - 1)]
            seaward = Polygon([a - (b - a) * 0.3, b + (b - a) * 0.3, b + (b - a) * 0.3 - np.array([nx, ny]) * 600, a - (b - a) * 0.3 - np.array([nx, ny]) * 600])
            near_sea = [g.intersection(seaward) for g in [walls] + done + ahead]          # what lies across the water
            room = min([g.distance(mid) for g in near_sea if not g.is_empty] + [600.0])
            ahead_cut = [g.difference(Point(*b).buffer(1.0)) for g in ahead]
            best = None
            lim = min(0.4, max(0.02, 0.7 * room / l))
            for _ in (1,):
              for pen, what, Q in candidates(a, b, chars[j] if chars else char):
                q = rel(Q)
                if q[:, 0].min() < -0.15 * l or q[:, 0].max() > 1.15 * l: continue
                sea_dev = max(0.0, -q[:, 1].min()) / l; land_dev = max(0.0, q[:, 1].max()) / l
                if land_dev > 0.45: continue
                if sea_dev > lim:                              # its headlands drawn back to fit the water in front of it
                    q = np.c_[q[:, 0], np.where(q[:, 1] < 0, q[:, 1] * lim / sea_dev, q[:, 1])]; pen += 60.0 * math.log(sea_dev / lim); sea_dev = lim
                    Q = np.c_[a[0] + q[:, 0] * ux + q[:, 1] * nx, a[1] + q[:, 0] * uy + q[:, 1] * ny]
                dev = max(sea_dev, land_dev)
                line = LineString(Q)
                # the land side: the piece closed by a box reaching D to its left
                cap = np.array([b + np.array([nx, ny]) * D, a + np.array([nx, ny]) * D])
                poly = Polygon(np.vstack([Q, cap]))
                if not poly.is_valid: continue
                score = pen + 150.0 * max(0.0, dev - 0.3) + 400.0 * max(0.0, 0.12 - dev)     # neither wild nor ruled straight
                if len(idx):
                    ins = shapely.contains_xy(poly, P[idx, 0], P[idx, 1])
                    d = shapely.distance(line, shapely.points(P[idx])); c = coastal[idx]
                    score += float((10.0 * np.clip(d - 2.0, 0, None) * np.where(ins, 1.0, 2.0))[c].sum())    # ports stay on the shore
                    score += float((1000.0 * wt[idx])[~c & ~ins].sum())                                    # inland places stay inland
                    score += float((60.0 * np.clip(3.0 - d, 0, None))[~c & ins].sum())
                if len(ridx):
                    score += 200.0 * int((~shapely.contains_xy(poly, Rv[ridx, 0], Rv[ridx, 1])).sum())
                if best is not None and score >= best[0]: continue
                inner = line.difference(Point(*a).buffer(1.0)).difference(Point(*b).buffer(1.0))     # pieces meet at their ends
                if walls_p.intersects(inner) or any(inner.intersects(g) for g in done): continue
                if any(inner.intersects(g) for g in ahead_cut): continue        # leave the shores still to come a clear line
                # no sliver of water pinched where two pieces meet: beyond six miles of the anchor they stay apart
                outer = line.difference(Point(*a).buffer(6.0)).difference(Point(*b).buffer(6.0))
                if done and not outer.is_empty and done[-1].difference(Point(*a).buffer(6.0)).distance(outer) < 3.0: continue
                if ahead and not outer.is_empty and ahead[0].difference(Point(*b).buffer(6.0)).distance(outer) < 3.0: continue
                best = (score, what, Q)
              if best is not None: break
            if best is None: raise RuntimeError(f'no real coast fits from {na} to {nb} (piece {j + 1} of {k})')
            score, what, Q = best
            if score >= 500 and len(idx):                     # say which places the chosen piece could not keep
                cap = np.array([b + np.array([nx, ny]) * D, a + np.array([nx, ny]) * D]); poly = Polygon(np.vstack([Q, cap]))
                bad = [places[t][0] for t in idx if not coastal[t] and not poly.contains(Point(*P[t]))]
                if bad: log(f'    left at sea: {", ".join(bad)}')
            out.append(Q[:-1]); done.append(LineString(Q)); pieces.append({'from': na, 'to': nb, 'piece': j + 1, 'of': k, 'what': what, 'score': round(score, 1), 'miles': round(l)})
            log(f'  {na} -> {nb} [{j + 1}/{k}]: {what}, {l:.0f} mi, score {score:.0f}')
    out.append(np.asarray(anchors[-1][1], float)[None])
    return np.vstack(out), pieces


def constraints(author):
    """From author.py's settled map: the places of southern Westeros as (name, X, Y, coastal, rank), and the rivers'
    courses less their last five miles (where they meet the sea at an anchor)."""
    from shapely.geometry import LineString
    shore = lambda p: p[1] == 'port' or bool(p[7].get('coast')) or p[0] in author.ON_SEA or p[0] in author.FIXED_AT
    towns = [p for p in author.PLACES if shore(p)]
    pl = []
    for p in author.PLACES:
        if p[2] > 720 or p[3] > -140: continue
        near_town = any(math.hypot(q[2] - p[2], q[3] - p[3]) < (8 if p[1] in ('landmark', 'tower') else 6) for q in towns)
        pl.append((p[0], p[2], p[3], shore(p) or p[1] == 'wonder' or near_town, p[7].get('rank', 5)))
    riv = []
    for r in author.RIVERS:
        q = np.array(r['pts'], float)
        if q[:, 0].mean() > 720 or q[:, 1].mean() > -100: continue
        line = LineString(q)
        riv.append([(line.interpolate(t).x, line.interpolate(t).y) for t in np.arange(0, max(0.0, line.length - 5), 2.0)])
    return pl, riv
