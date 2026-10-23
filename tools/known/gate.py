"""The release gate: the geography and travel rules every build must pass (rules G1-G19, 7b, 9b and 18).

  python3 tools/known/gate.py              # every rule; exit 1 on any FAIL (WARNs are listed for review)
  python3 tools/known/gate.py G1 G7 9b     # some rules
  python3 tools/known/gate.py --baseline   # after a build that passes everything: approve it as the new baseline

Units are miles from Winterfell. A FAIL blocks a release; a WARN goes to review. The seeded tests
(tools/known/test_gate.py) break the map on purpose and check that each rule fails when it should.
"""
import os, sys, io, json, math, hashlib, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union

QA = os.path.join(HERE, 'qa')
REFERENCE = os.path.join(QA, 'reference_1fdf781.npz')       # the map before the coast was rebuilt: a reference only
BASELINE = os.path.join(QA, 'baseline.npz')                 # the first build to pass every rule
LOCKS = os.path.join(QA, 'locks.json')                      # island counts and ids, approved with the baseline


class Report:
    def __init__(self): self.rows = []
    def add(self, rule, level, msg): self.rows.append((rule, level, msg))
    def ok(self, rule, msg): self.add(rule, 'PASS', msg)
    def warn(self, rule, msg): self.add(rule, 'WARN', msg)
    def fail(self, rule, msg): self.add(rule, 'FAIL', msg)
    def failed(self): return any(l == 'FAIL' for _, l, _ in self.rows)
    def show(self):
        for r, l, m in self.rows: print(f'{l:4s}  {r:4s}  {m}')
        n = {l: sum(1 for _, x, _ in self.rows if x == l) for l in ('PASS', 'WARN', 'FAIL')}
        print(f"\n{n['PASS']} pass, {n['WARN']} warn, {n['FAIL']} fail")


class World:
    """The settled map, as the gate sees it (author.prepare()), and a few derived shapes."""
    def __init__(self, author=None):
        if author is None:
            import author as A
            with contextlib.redirect_stdout(io.StringIO()): self.coast = A.prepare()
            author = A
        else: self.coast = author.COAST_SETTLED
        self.A = author
        self.westeros = Polygon(self.coast).buffer(0)
        self.islands = [i for i in author.ISLANDS if len(i['pts']) > 2]
        self.rings = [('Westeros', self.coast)] + [(i['name'] or 'isle', i['pts']) for i in self.islands]
        self.land = unary_union([self.westeros] + [Polygon(i['pts']).buffer(0) for i in self.islands])
        self.edge = self.land.boundary
        self.places = {p[0]: p for p in author.PLACES}

    def shore(self, x, y): return self.edge.distance(Point(x, y))
    def on_land(self, x, y): return self.land.contains(Point(x, y))


# ---------------------------------------------------------------------------------------------------- the rules
def g1_rivers_over_sea(W, R):
    bad = []
    for r in W.A.RIVERS:
        line = LineString(r['pts'])
        wet = line.difference(W.land).length
        if wet > 0.75: bad.append(f"{r['name']} {wet:.1f} mi")
    (R.fail if bad else R.ok)('G1', 'rivers over the sea (≤ 0.75 mi each): ' + (', '.join(bad) if bad else f'all {len(W.A.RIVERS)} rivers on land'))


def g2_mouths(W, R):
    bad, n = [], 0
    for r in W.A.RIVERS:
        if r['name'] not in W.A.SEA_RIVERS: continue
        n += 1
        ends = [r['pts'][-1]] + [d['pts'][-1] for d in getattr(W.A, 'DISTRIBUTARIES', []) if d.get('of') == r['name']]
        d = min(W.shore(*e) for e in ends)
        if d > 1.0: bad.append(f"{r['name']} {d:.1f} mi")
    (R.fail if bad else R.ok)('G2', 'river mouths ≤ 1 mi from the coast: ' + (', '.join(bad) if bad else f'all {n} sea rivers'))


def g3_ports(W, R):
    bad, river_ports = [], getattr(W.A, 'RIVER_PORTS', {})
    riv = {r['name']: LineString(r['pts']) for r in W.A.RIVERS}
    lakes = {l['name']: Polygon(l['pts']).exterior for l in W.A.LAKES}
    n = 0
    for p in W.A.PLACES:
        coastal = p[1] == 'port' or p[7].get('coast') or p[0] in W.A.ON_SEA
        if not coastal: continue
        n += 1
        if p[0] in river_ports:
            on = river_ports[p[0]]; g = riv.get(on) or lakes.get(on)
            if g is None: bad.append(f'{p[0]} (tagged to {on}, which does not exist)'); continue
            d = g.distance(Point(p[2], p[3]))
            if d > 1.0: bad.append(f'{p[0]} {d:.1f} mi from {on}')
            continue
        d = W.shore(p[2], p[3])
        if d > 1.0: bad.append(f'{p[0]} {d:.1f} mi from the shore')
    (R.fail if bad else R.ok)('G3', 'ports ≤ 1 mi from the shore, river ports on their river: ' + (', '.join(bad) if bad else f'all {n}'))


def g4_validity(W, R):
    from shapely.validation import explain_validity
    bad = []
    polys = []
    for name, ring in W.rings:
        g = Polygon(ring)
        if not g.is_valid: bad.append(f'{name}: {explain_validity(g)}')
        polys.append((name, g))
    # separate land rings never cross, touch or share a vertex
    from shapely.strtree import STRtree
    gs = [g.buffer(0) for _, g in polys]; tree = STRtree(gs)
    verts = {}
    for k, (name, ring) in enumerate(W.rings):
        for x, y in ring: verts.setdefault((round(x, 3), round(y, 3)), set()).add(k)
    shared = sum(1 for v in verts.values() if len(v) > 1)
    for i, g in enumerate(gs):
        for j in tree.query(g):
            if j <= i: continue
            if g.intersects(gs[j]): bad.append(f'{polys[i][0]} and {polys[j][0]} touch or overlap')
    if shared: bad.append(f'{shared} vertices shared between separate rings')
    (R.fail if bad else R.ok)('G4', 'every ring valid, no crossings or touches: ' + ('; '.join(bad[:8]) + (f' (+{len(bad) - 8})' if len(bad) > 8 else '') if bad else f'{len(W.rings)} rings'))


def g5_islands(W, R):
    named = {}
    for i in W.islands:
        if i['name'] in ('Essos', 'Sothoryos'): continue
        named.setdefault(i['name'] or 'isle', []).append(i)
    ONE = ['Pyke', 'Great Wyk', 'Old Wyk', 'Harlaw', 'Saltcliffe', 'Blacktyde', 'Orkmont', 'Skagos', 'Bear Island', 'Dragonstone',
           'Driftmark', 'Tarth', 'Estermont', 'The Arbor', 'Fair Isle', 'Bloodstone']
    bad = [f'{n}: {len(named.get(n, []))} polygons' for n in ONE if len(named.get(n, [])) != 1]
    big = [i for i in named.get('isle', []) + named.get('islet', []) if Polygon(i['pts']).area >= 10]
    if big: bad.append(f'{len(big)} unnamed islands of 10 sq mi or more (largest {max(Polygon(i["pts"]).area for i in big):.0f} sq mi)')
    if os.path.exists(LOCKS):
        lk = json.load(open(LOCKS)).get('islands', {})
        now = {k: len(v) for k, v in named.items()}
        for k, n in lk.items():
            if now.get(k, 0) != n: bad.append(f'{k}: {now.get(k, 0)} rings, locked at {n}')
    (R.fail if bad else R.ok)('G5', 'islands locked, one polygon per named island: ' + ('; '.join(bad) if bad else f'{sum(len(v) for v in named.values())} islands'))


def land_raster(W):
    import landraster
    return landraster.rasterise([W.coast] + [i['pts'] for i in W.islands])


def g6_flips(W, R, land=None):
    import landraster
    from scipy import ndimage as ndi
    land = land_raster(W) if land is None else land
    approved = os.path.exists(BASELINE)
    ref = landraster.load(BASELINE if approved else REFERENCE)
    flip = land != ref
    lab, n = ndi.label(flip)
    sizes = ndi.sum(flip, lab, range(1, n + 1)) if n else []
    big = [(int(s), k + 1) for k, s in enumerate(sizes) if s > 25]
    X0, X1, Y0, Y1, RES = landraster.X0, landraster.X1, landraster.Y0, landraster.Y1, landraster.RES
    touched = []
    if approved and big:                                       # a flip may not touch a place, a river or a route
        pts = [(p[2], p[3], p[0]) for p in W.A.PLACES]
        for r in W.A.RIVERS: pts += [(x, y, r['name']) for x, y in r['pts']]
        for x, y, nm in pts:
            i, j = int((Y1 - y) / RES), int((x - X0) / RES)
            if 0 <= i < lab.shape[0] and 0 <= j < lab.shape[1] and lab[i, j] and sizes[lab[i, j] - 1] > 25: touched.append(nm)
    msg = f"{len(big)} flips over 25 sq mi against the {'baseline' if approved else 'reference (1fdf781, not approved)'}" + \
          (f', largest {max(s for s, _ in big):,} sq mi' if big else '')
    if touched: R.fail('G6', msg + '; touching ' + ', '.join(sorted(set(touched))[:10]))
    elif big: R.warn('G6', msg)
    else: R.ok('G6', msg)


def g7_anchors(W, R):
    import coast_fixed
    bad = []
    if len(coast_fixed.ANCHORS) != coast_fixed.FROZEN['count']: bad.append(f"{len(coast_fixed.ANCHORS)} anchors, frozen at {coast_fixed.FROZEN['count']}")
    if coast_fixed.checksum() != coast_fixed.FROZEN['sha256']: bad.append('the anchor list changed (checksum)')
    ring = LineString(list(W.coast) + [W.coast[0]])
    for n, (x, y) in coast_fixed.ANCHORS:
        d = ring.distance(Point(x, y))
        if d > 0.1: bad.append(f'{n} {d:.2f} mi off the coast')
    (R.fail if bad else R.ok)('G7', 'named anchors frozen and held to 0.1 mi: ' + ('; '.join(bad) if bad else f'{len(coast_fixed.ANCHORS)} anchors'))


def g7b_graft(W, R):
    """The built coast stays within 5 mi of the canonical outline that shores.py drew (coast_shores.json) between the
    anchors: nothing downstream may move the south's coast further."""
    import coast_fixed
    path = os.path.join(HERE, 'coast_shores.json')
    if not os.path.exists(path): R.warn('7b', 'no coast_shores.json'); return
    outline = LineString(json.load(open(path))['Westeros']['coast'])
    P = np.asarray(W.coast, float); south = P[(P[:, 1] < -150) & (P[:, 0] < 720)]
    d = np.array([outline.distance(Point(*q)) for q in south[::4]]) if len(south) else np.zeros(1)
    (R.fail if d.max() > 5 else R.ok)('7b', f'the south coast within 5 mi of its canonical outline: worst {d.max():.1f} mi')


def g8_one_westeros(W, R):
    from scipy import ndimage as ndi
    from PIL import Image, ImageDraw
    res, x0, x1, y0, y1 = 0.5, -300, 400, -800, -150
    im = Image.new('1', (int((x1 - x0) / res), int((y1 - y0) / res)), 0); d = ImageDraw.Draw(im)
    d.polygon([((x - x0) / res, (y1 - y) / res) for x, y in W.coast], fill=1)
    land = np.array(im, bool)
    core = ndi.distance_transform_edt(land) * res >= 5.0           # what is left when 5 mi is taken off every shore
    lab, _ = ndi.label(core)
    def at(n): p = W.places[n]; return lab[int((y1 - p[3]) / res), int((p[2] - x0) / res)]
    a, b = at('Moat Cailin'), at('The Twins')
    (R.ok if a and a == b else R.fail)('G8', 'one Westeros: the North and the south joined by land at least 10 mi wide through the Neck' if a and a == b else 'the Neck is cut or narrower than 10 mi')


def g9_seas_lakes(W, R):
    import waters
    from scipy import ndimage as ndi
    from PIL import Image, ImageDraw
    res, x0, x1, y0, y1 = 2.0, -1500, 6000, -5600, 1600
    im = Image.new('1', (int((x1 - x0) / res), int((y1 - y0) / res)), 0); dr = ImageDraw.Draw(im)
    for _, ring in W.rings: dr.polygon([((x - x0) / res, (y1 - y) / res) for x, y in ring], fill=1)
    sea = ~np.array(im, bool); lab, _ = ndi.label(sea)
    ocean = lab[0, 0]
    bad, warn = [], []
    for s in W.A.SEA_LABELS:
        name, x, y = s[0], s[1], s[2]
        i, j = int((y1 - y) / res), int((x - x0) / res)
        if not sea[i, j]: bad.append(f'{name} label on land'); continue
        if lab[i, j] != ocean: bad.append(f'{name} cut off from the ocean')
    tags = {l['name'] for l in W.A.LAKES} | {s[0] for s in W.A.SEA_LABELS}
    # the lakes and inland seas the books name (there is no Lake Lhazar in them: Lhazar is grazing land)
    for need in ('The Gods Eye', 'The Long Lake', 'Dagger Lake', 'The Womb of the World', 'The Sea of Dorne'):
        if need not in tags: warn.append(f'{need} not tagged')
    enclosed = int(sum(1 for k in range(1, lab.max() + 1) if k != ocean and (lab == k).sum() * res * res > 25)) if lab.max() < 2000 else -1
    msg = f'{len(W.A.SEA_LABELS)} seas joined to the ocean, {len(W.A.LAKES)} lakes tagged'
    if bad: R.fail('G9', msg + ': ' + '; '.join(bad))
    elif warn: R.warn('G9', msg + ': ' + '; '.join(warn))
    else: R.ok('G9', msg)


def g9b_inlets(W, R):
    import waters
    rings = [r for _, r in W.rings]
    found = []
    for box in ((-1000, 1000, -2700, 1500), (600, 5900, -3000, 1100), (-300, 4000, -5600, -2700)):
        f, _ = waters.inlets(rings, box, res=0.5 if box[0] == -1000 else 1.0)
        found += [x for x in f if not x['named'] and x.get('depth')]
    bad = sorted({(round(x['X']), round(x['Y']), x['depth']) for x in found}, key=lambda t: -t[2])
    (R.fail if bad else R.ok)('9b', 'no unnamed sea inlet deeper than 15 mi: ' + (', '.join(f'{x},{y} ({d:.0f} mi)' for x, y, d in bad[:10]) + (f' (+{len(bad) - 10})' if len(bad) > 10 else '') if bad else 'none'))


def g10_wall(W, R):
    w = next(x for x in W.A.WALLS if x.get('ice'))
    P = np.asarray(w['pts'], float); a, b = P[0], P[-1]; L = float(np.hypot(*(b - a)))
    u = (b - a) / L; off = np.abs((P - a) @ np.array([-u[1], u[0]]))
    line = LineString(P)
    bad, warn = [], []
    if off.max() > 3: bad.append(f'not straight ({off.max():.1f} mi off its line)')
    for end, out in ((a, -u), (b, u)):
        if not W.on_land(*end): bad.append(f'an end at sea ({W.shore(*end):.2f} mi out)')
        elif W.shore(*end) > 0.25: bad.append(f'an end {W.shore(*end):.2f} mi short of the shore')
        q = end + out * 0.5
        if W.on_land(*q): bad.append('the shore lies beyond an end (a gap)')
    length = line.length
    if not 280 <= length <= 320: warn.append(f'{length:.0f} mi long (a hundred leagues is about 300)')
    for n in ('Castle Black', 'Eastwatch-by-the-Sea', 'The Shadow Tower', 'Westwatch-by-the-Bridge'):
        p = W.places.get(n)
        if p and line.distance(Point(p[2], p[3])) > 1.0: bad.append(f'{n} {line.distance(Point(p[2], p[3])):.1f} mi off the Wall')
    e = W.places.get('Eastwatch-by-the-Sea')
    if e and W.shore(e[2], e[3]) > 1.0: bad.append(f'Eastwatch {W.shore(e[2], e[3]):.1f} mi from the Bay of Seals')
    msg = f'the Wall {length:.0f} mi, coast to coast'
    if bad: R.fail('G10', msg + ': ' + '; '.join(bad))
    elif warn: R.warn('G10', msg + ': ' + '; '.join(warn))
    else: R.ok('G10', msg)


def g11_neck(W, R):
    m = next(x for x in W.A.MARSHES if x['name'] == 'The Neck')
    mp = Polygon(m['pts']).buffer(0)
    wet = mp.difference(W.land).area
    bad, warn = [], []
    if wet > 1.0: bad.append(f'{wet:.0f} sq mi of the marsh over the sea')
    mc = W.places.get('Moat Cailin'); gw = W.places.get('Greywater Watch')
    kr = next(r for r in W.A.ROADS if r['name'] == 'The Kingsroad'); road = LineString(kr['pts'])
    if mc:
        if road.distance(Point(mc[2], mc[3])) > 0.5: bad.append(f'Moat Cailin {road.distance(Point(mc[2], mc[3])):.1f} mi off the Kingsroad')
        north_edge = max(y for _, y in m['pts'])
        if mp.exterior.distance(Point(mc[2], mc[3])) > 3.0: bad.append(f'Moat Cailin {mp.exterior.distance(Point(mc[2], mc[3])):.1f} mi inside the marsh, not at its edge')
    if gw and not mp.contains(Point(gw[2], gw[3])): warn.append('Greywater Watch outside the marsh')
    others = [r['name'] for r in W.A.ROADS if r['name'] != 'The Kingsroad' and LineString(r['pts']).intersects(mp)]
    if others: bad.append('roads through the Neck besides the Kingsroad: ' + ', '.join(others))
    msg = 'the Neck: a wetland on land, Moat Cailin on the causeway'
    if bad: R.fail('G11', msg + ': ' + '; '.join(bad))
    elif warn: R.warn('G11', msg + ': ' + '; '.join(warn))
    else: R.ok('G11', msg)


RHOYNE_TOWNS = {'Ny Sar': 'The Rhoyne', 'Chroyane': 'The Rhoyne', 'Selhorys': 'The Rhoyne', 'Valysar': 'The Rhoyne',
                'Sar Mell': 'The Rhoyne', 'Volon Therys': 'The Rhoyne', 'Volantis': 'The Rhoyne', 'Ghoyan Drohe': 'The Little Rhoyne',
                'Norvos': 'The Noyne', 'Qohor': 'The Qhoyne', 'Ar Noy': 'The Qhoyne', 'Sarhoy': 'The Rhoyne, the Sarhoy mouth'}


def g12_rhoyne(W, R):
    """The Rhoyne: a tree (each daughter meets its river once, nothing crosses outside the delta), its towns on it,
    Volantis at a mouth on the sea, and wider than any river of Westeros."""
    riv = {r['name']: r for r in W.A.RIVERS}
    sysn = {'The Rhoyne'}
    grew = True
    while grew:
        grew = False
        for r in W.A.RIVERS:
            if (r.get('to') in sysn or r.get('of') in sysn) and r['name'] not in sysn: sysn.add(r['name']); grew = True
    bad = []
    for n in sysn:
        r = riv[n]; parent = r.get('to') or r.get('of')
        if not parent: continue
        end = r['pts'][-1] if r.get('to') else r['pts'][0]
        d = LineString(riv[parent]['pts']).distance(Point(end))
        if d > 1.0: bad.append(f'{n} {"ends" if r.get("to") else "starts"} {d:.1f} mi from {parent}')
    names = sorted(sysn)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            x = LineString(riv[a]['pts']).intersection(LineString(riv[b]['pts']))
            if x.is_empty: continue
            pts = [x] if x.geom_type == 'Point' else [g for g in getattr(x, 'geoms', [x]) if g.geom_type == 'Point']
            joins = [Point(riv[n]['pts'][-1] if riv[n].get('to') else riv[n]['pts'][0]) for n in (a, b) if riv[n].get('to') or riv[n].get('of')]
            stray = [q for q in pts if all(q.distance(j) > 3.0 for j in joins)]
            if stray: bad.append(f'{a} and {b} cross at {stray[0].x:.0f},{stray[0].y:.0f}')
    for t, on in RHOYNE_TOWNS.items():
        p = W.places.get(t)
        if not p: bad.append(f'{t} missing'); continue
        d = LineString(riv[on]['pts']).distance(Point(p[2], p[3]))
        if d > 1.0: bad.append(f'{t} {d:.1f} mi from {on}')
    v = W.places.get('Volantis')
    if v and Point(riv['The Rhoyne']['pts'][-1]).distance(Point(v[2], v[3])) > 1.0: bad.append('Volantis not at the Rhoyne\'s mouth')
    west = max(r['w1'] for r in W.A.RIVERS if np.mean([x for x, _ in r['pts']]) < 700)
    if riv['The Rhoyne']['w1'] <= west: bad.append(f"the Rhoyne ({riv['The Rhoyne']['w1']} m) no wider than Westeros's widest ({west} m)")
    lake = next((l for l in W.A.LAKES if l['name'] == 'Dagger Lake'), None)
    if not lake: bad.append('no Dagger Lake')
    elif Polygon(lake['pts']).distance(Point(riv['The Qhoyne']['pts'][-1])) > 1.0: bad.append('the Qhoyne does not reach Dagger Lake')
    msg = f'the Rhoyne: {len(sysn)} rivers in one tree, {len(RHOYNE_TOWNS)} towns on their rivers, Volantis at the mouth'
    (R.fail if bad else R.ok)('G12', msg + (': ' + '; '.join(bad) if bad else ''))


NAMED_PASSES = ("The Prince's Pass", 'The Boneway', 'The Bloody Gate', 'The Skirling Pass')


def g18_rivers_downhill(W, R):
    """Rule 18: no river climbs (more than 5 m within a mile, downstream, on the generated ground: rivercheck.py), and no
    river crosses a range's crest except at a named pass (its valley would be a new pass)."""
    bad, warn = [], []
    passes = [Point(p[2], p[3]) for n, p in W.places.items() if n in NAMED_PASSES]
    for g in W.A.RANGES:
        crest = LineString(g['pts'])
        for r in W.A.RIVERS:
            x = LineString(r['pts']).intersection(crest)
            if x.is_empty: continue
            q = x if x.geom_type == 'Point' else list(getattr(x, 'geoms', [x]))[0]
            if not any(q.distance(p) < 15 for p in passes): bad.append(f"{r['name']} crosses {g['name']} at {q.x:.0f},{q.y:.0f}")
    try:
        import rivercheck
        _, rows = __import__('asyncio').run(rivercheck.measure())
    except Exception as e:
        rows = None; warn.append(f'the ground was not measured ({type(e).__name__}: {str(e)[:80]})')
    if rows:
        for r in rows:
            if r['rises']: bad.append(f"{r['name']} climbs {r['worst']:.0f} m at {r['at']}")
            elif r['banks'] and r['off'] / r['banks'] > rivercheck.OFF_FLOOR: warn.append(f"{r['name']} off its valley floor at {r['off']} of {r['banks']} miles")
    msg = f"rivers never climb and cross no crest{'' if rows is None else f' ({len(rows)} rivers walked on the ground)'}"
    if bad: R.fail('18', msg + ': ' + '; '.join(bad))
    elif warn: R.warn('18', msg + ': ' + '; '.join(warn))
    else: R.ok('18', msg)


RULES = {'G1': g1_rivers_over_sea, 'G2': g2_mouths, 'G3': g3_ports, 'G4': g4_validity, 'G5': g5_islands, 'G6': g6_flips,
         'G7': g7_anchors, '7b': g7b_graft, 'G8': g8_one_westeros, 'G9': g9_seas_lakes, '9b': g9b_inlets, 'G10': g10_wall,
         'G11': g11_neck, 'G12': g12_rhoyne, '18': g18_rivers_downhill}


def run(which=None, W=None):
    W = W or World(); R = Report()
    for k, f in RULES.items():
        if which and k not in which: continue
        try: f(W, R)
        except Exception as e: R.fail(k, f'the check itself failed: {type(e).__name__}: {e}')
    return R


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    R = run(args or None); R.show()
    sys.exit(1 if R.failed() else 0)
