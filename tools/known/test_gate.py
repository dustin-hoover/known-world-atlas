"""Seeded failures (gate rule G18): each breaks a copy of the settled map on purpose, and the gate must FAIL the rule
that guards against it. A seed the gate lets through is itself a failure.

  python3 tools/known/test_gate.py          # every seed; exit 1 if one slips through

The seeds are the nine of the QA plan (a river vertex 2 mi out, a port 3 mi inland, the Neck cut, Slaver's Bay
closed, a Smoking Sea channel filled, Pyke and Great Wyk merged, a Valyria ring looped, an anchor moved half a mile,
Davos back on land) and the two failures found before (Theon's landing out at sea, the inlet at Craster's coast).
The locks a seed is tested against are those of the clean map, whether or not a baseline has been approved yet.
"""
import os, sys, io, copy, math, types, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union, nearest_points
import gate

DATA = ('RIVERS', 'PLACES', 'ISLANDS', 'LAKES', 'WALLS', 'MARSHES', 'ROADS', 'SEA_LABELS', 'DISTRIBUTARIES', 'STATEMENTS', 'RANGES')


def clone(W):
    """A copy of the settled map's data to break (the author module itself is left alone)."""
    A = W.A
    ns = types.SimpleNamespace(**{k: getattr(A, k) for k in dir(A) if not k.startswith('__')})
    for k in DATA: setattr(ns, k, copy.deepcopy(getattr(A, k)))
    ns.ON_SEA, ns.RIVER_PORTS = set(A.ON_SEA), dict(A.RIVER_PORTS)
    ns.COAST_SETTLED = [list(p) for p in W.coast]
    return ns


def ring_of(g):
    g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
    return [[round(x, 3), round(y, 3)] for x, y in list(g.exterior.coords)[:-1]]


def place(ns, name): return next(p for p in ns.PLACES if p[0] == name)


# ------------------------------------------------------------------------------------------------ the seeds
def river_out(ns, W):
    r = next(r for r in ns.RIVERS if r['name'] == 'The Mander')
    (ax, ay), (bx, by) = r['pts'][-2], r['pts'][-1]; L = math.hypot(bx - ax, by - ay) or 1
    for k in (1.0, 2.0, 2.5): r['pts'].append([bx + (bx - ax) / L * k, by + (by - ay) / L * k])


def port_inland(ns, W):
    p = next(p for p in ns.PLACES if p[1] == 'port' and p[0] not in ns.RIVER_PORTS)
    e = nearest_points(W.edge, Point(p[2], p[3]))[0]
    for ang in range(0, 360, 10):
        q = (e.x + 3.5 * math.cos(math.radians(ang)), e.y + 3.5 * math.sin(math.radians(ang)))
        if W.land.contains(Point(q)) and W.edge.distance(Point(q)) >= 3.0: p[2], p[3] = q; return
    raise RuntimeError('no inland spot found')


def neck_cut(ns, W):
    a, b = place(ns, 'Moat Cailin'), place(ns, 'The Twins'); y = (a[3] + b[3]) / 2
    ns.COAST_SETTLED = ring_of(Polygon(ns.COAST_SETTLED).buffer(0).difference(box(-700, y - 1.5, 900, y + 1.5)))


def bay_closed(ns, W):
    e = next(i for i in ns.ISLANDS if i['name'] == 'Essos')
    e['pts'] = ring_of(Polygon(e['pts']).buffer(0).union(box(1950, -2440, 2950, -2370)))     # a bar right across its mouth


def smoking_filled(ns, W):
    rings = [i for i in ns.ISLANDS if i['name'] == 'The Smoking Sea']
    a = max(rings, key=lambda i: Polygon(i['pts']).area)
    b = min((i for i in rings if i is not a), key=lambda i: Polygon(i['pts']).distance(Polygon(a['pts'])))
    g = unary_union([Polygon(a['pts']).buffer(0), Polygon(b['pts']).buffer(0)]).buffer(Polygon(a['pts']).distance(Polygon(b['pts'])) / 2 + 0.5).buffer(-0.5)
    a['pts'] = ring_of(g); ns.ISLANDS.remove(b)


def pyke_merged(ns, W):
    p = next(i for i in ns.ISLANDS if i['name'] == 'Pyke'); g = next(i for i in ns.ISLANDS if i['name'] == 'Great Wyk')
    d = Polygon(p['pts']).distance(Polygon(g['pts']))
    p['pts'] = ring_of(unary_union([Polygon(p['pts']).buffer(0), Polygon(g['pts']).buffer(0)]).buffer(d / 2 + 0.5).buffer(-0.5))
    ns.ISLANDS.remove(g)


def valyria_loop(ns, W):
    v = max((i for i in ns.ISLANDS if i['name'] == 'Valyria'), key=lambda i: Polygon(i['pts']).area)
    n = len(v['pts']); v['pts'][n // 4], v['pts'][3 * n // 4] = v['pts'][3 * n // 4], v['pts'][n // 4]


def anchor_moved(ns, W):
    import coast_fixed
    ax, ay = dict(coast_fixed.ANCHORS)['Lannisport']
    ns.COAST_SETTLED = [[x + 0.5, y] if math.hypot(x - ax, y - ay) < 1.0 else [x, y] for x, y in ns.COAST_SETTLED]


def built_copy(W):
    import cast
    if not cast.BUILT:
        with contextlib.redirect_stdout(io.StringIO()): cast.build(W.A.PLACES, W.A.ROADS, W.A.STORIES, [r for _, r in W.rings], W.A.RIVERS)
    return {'full': copy.deepcopy(cast.BUILT['full']), 'windows': list(cast.BUILT['windows']), 'crossings': cast.BUILT['crossings']}


def davos_on_land(ns, W):
    import cast
    B = built_copy(W); T = cast.T; a, b = T('300 9 1'), T('300 11 2')
    P = B['full']['davos']; wh, sk = place(ns, 'White Harbor'), place(ns, 'Skagos')
    B['full']['davos'] = [p for p in P if p[2] < a] + [(wh[2], wh[3], a), (sk[2], sk[3], b)] + [p for p in P if p[2] > b]
    B['windows'] = [w for w in B['windows'] if not (w[3] == 'sea' and 'davos' in w[0] and T(w[1]) <= T('300 9 2') <= T(w[2]))]
    ns.built = B


def theon_at_sea(ns, W):
    import cast
    B = built_copy(W); T = cast.T
    P = B['full']['theon']; k = min(range(len(P)), key=lambda i: abs(P[i][2] - T('299 3 12')) + 0.01 * math.hypot(P[i][0] + 421, P[i][1] + 170))
    P[k] = (-440.0, -250.0, P[k][2]); ns.built = B


def craster_inlet(ns, W):
    c = Polygon(ns.COAST_SETTLED).buffer(0)
    e = nearest_points(c.exterior, Point(-430, -60))[0]
    q = nearest_points(c.buffer(-30).exterior, e)[0]                       # straight in from the shore, 30 mi
    from shapely.geometry import LineString
    ns.COAST_SETTLED = ring_of(c.difference(LineString([(e.x - (q.x - e.x) * 0.1, e.y - (q.y - e.y) * 0.1), (q.x, q.y)]).buffer(1.5)))


SEEDS = [('a river vertex 2 mi out', ['G1'], river_out), ('a port 3 mi inland', ['G3'], port_inland),
         ('the Neck cut', ['G8'], neck_cut), ("Slaver's Bay closed", ['G13'], bay_closed),
         ('a Smoking Sea channel filled', ['G14'], smoking_filled), ('Pyke and Great Wyk merged', ['G5'], pyke_merged),
         ('a Valyria ring looped', ['G4'], valyria_loop), ('an anchor moved half a mile', ['G7'], anchor_moved),
         ('Davos back on land', ['G16'], davos_on_land), ("Theon's landing out at sea", ['G16'], theon_at_sea),
         ("an inlet at Craster's coast", ['9b'], craster_inlet)]


def run(W=None, quiet=False):
    """-> the names of the seeds the gate let through."""
    W = W or gate.World()
    clean = gate.lock_data(W)
    real_locks = gate.locks
    gate.locks = lambda: clean                         # each seed against the clean map's own locks
    missed = []
    try:
        for name, rules, breaks in SEEDS:
            ns = clone(W); breaks(ns, W)
            W2 = gate.World(ns)
            if hasattr(ns, 'built'): W2.built = ns.built
            R = gate.run(rules, W2)
            caught = any(l == 'FAIL' and r in rules for r, l, _ in R.rows)
            if not quiet: print(f"{'caught' if caught else 'MISSED'}  {name:32s} " + ' | '.join(f'{r} {l}: {m[:110]}' for r, l, m in R.rows))
            if not caught: missed.append(name)
    finally:
        gate.locks = real_locks
    return missed


if __name__ == '__main__':
    missed = run()
    print(f'{len(SEEDS) - len(missed)} of {len(SEEDS)} seeded failures caught')
    sys.exit(1 if missed else 0)
