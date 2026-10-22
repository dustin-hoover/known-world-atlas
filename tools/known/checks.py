"""Map checks run before every commit (MAP_V2 §7): places against the shore, and travellers against the water.

  python3 tools/known/checks.py            # both; exit 1 if any check fails
  python3 tools/known/checks.py places     # only the places
  python3 tools/known/checks.py water      # only the journeys

places  a place out at sea (a wonder such as the Titan may stand in the water, and a town astride a river's mouth
        over its estuary), or a port or a `coast=True` place more than 2 miles from the shore
water   a traveller more than about 3 miles out to sea while moving on foot or horseback (any mode that is not a
        ship, a boat or a dragon), sampled every quarter day. Two short steps are known and allowed: Davos leaving
        White Harbor and Tormund beyond the Wall (KNOWN below); a new one fails the check.
"""
import os, sys, io, re, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np

WATER_MODES = {'sea', 'boat', 'dragon', 'blackship', 'barrel', 'fly'}
KNOWN = {('Davos Seaworth', '300 9'), ('Tormund', '300 4'), ('Tormund', '300 9')}      # (traveller, 'year moon') already reported


def setup():
    import author
    with contextlib.redirect_stdout(io.StringIO()): coast = author.prepare()
    polys = [coast] + [i['pts'] for i in author.ISLANDS if len(i['pts']) > 2]
    return author, coast, polys


def mask(polys, res=2.0):
    """A fast land test: our coasts and islands drawn at `res` miles a pixel."""
    from PIL import Image, ImageDraw
    xs = [p[0] for pl in polys for p in pl]; ys = [p[1] for pl in polys for p in pl]
    x0, y1 = min(xs) - 50, max(ys) + 50
    W, H = int((max(xs) + 50 - x0) / res), int((y1 - (min(ys) - 50)) / res)
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    for pl in polys: d.polygon([((x - x0) / res, (y1 - y) / res) for x, y in pl], fill=255)
    M = np.array(im) > 0
    def land(P):
        i, j = int((y1 - P[1]) / res), int((P[0] - x0) / res)
        return bool(0 <= i < H and 0 <= j < W and M[i, j])
    return land


def check_places(author, polys):
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    land = unary_union([Polygon(pl).buffer(0) for pl in polys]); edge = land.boundary
    bad = []
    # towns that stand astride a river's mouth (author.MOUTH_TOWNS), and their towers, may stand over its water
    mouths = [q for q in author.PLACES if q[0] in author.MOUTH_TOWNS]
    astride = lambda p: any(np.hypot(p[2] - q[2], p[3] - q[3]) < 8 and (p is q or p[1] in ('landmark', 'tower')) for q in mouths)
    for p in author.PLACES:
        if p[1] == 'wonder': continue
        P = Point(p[2], p[3]); d = edge.distance(P)
        if not land.contains(P) and d > (5.0 if astride(p) else 0.5): bad.append(f'  AT SEA   {p[0]:32s} {p[1]:9s} {d:5.1f} mi out')
        elif (p[1] == 'port' or p[7].get('coast')) and d > 2.0: bad.append(f'  INLAND   {p[0]:32s} {p[1]:9s} {d:5.1f} mi from the shore')
    print(f'places: {len(author.PLACES)} checked, {len(bad)} off')
    for b in bad: print(b)
    return not bad


def check_water(author, coast, polys):
    import cast
    _, journeys, modes, _, _ = cast.build(author.PLACES, author.ROADS, author.STORIES, polys)
    land = mask(polys)
    rules = [(re.compile(rx), cast.T(a), cast.T(b), m) for rx, a, b, m in modes]
    def mode(name, t):
        return next((m for rx, a, b, m in rules if a <= t <= b and rx.search(name)), 'walk')
    def label(t):
        y = int(t // 365) + 1; r = t - (y - 1) * 365; mo = int(r // 30) + 1
        return f'{y} {mo}', f'{y} {mo} {r - (mo - 1) * 30 + 1:4.1f}'
    def at(p, t):
        for i in range(len(p) - 1):
            if p[i][2] <= t <= p[i + 1][2]:
                f = (t - p[i][2]) / ((p[i + 1][2] - p[i][2]) or 1)
                return p[i][0] + (p[i + 1][0] - p[i][0]) * f, p[i][1] + (p[i + 1][1] - p[i][1]) * f
        return None
    found, new = set(), []
    for js in journeys.values():
        for j in js:
            p = j['pts']; t = p[0][2]
            while t < p[-1][2]:
                P, Q = at(p, t), at(p, t + 0.25)
                wet = P and not land(P) and not any(land((P[0] + dx, P[1] + dy)) for dx, dy in ((3, 0), (-3, 0), (0, 3), (0, -3)))
                moving = P and Q and np.hypot(Q[0] - P[0], Q[1] - P[1]) > 0.2
                if wet and moving and mode(j['name'], t) not in WATER_MODES:
                    moon, day = label(t)
                    if (j['name'], moon) not in found:
                        found.add((j['name'], moon))
                        known = (j['name'], moon) in KNOWN
                        line = f"  {'known' if known else 'NEW  '} {j['name']:28s} {mode(j['name'], t):8s} on the water at {P[0]:.0f},{P[1]:.0f} on {day}"
                        print(line)
                        if not known: new.append(line)
                t += 0.25
    print(f'water: {len(found)} wet steps, {len(new)} new')
    return not new


if __name__ == '__main__':
    which = sys.argv[1:] or ['places', 'water']
    author, coast, polys = setup()
    ok = True
    if 'places' in which: ok &= check_places(author, polys)
    if 'water' in which: ok &= check_water(author, coast, polys)
    sys.exit(0 if ok else 1)
