"""Map checks run before every commit (MAP_V2 §7): places against the shore, and travellers against the water.

  python3 tools/known/checks.py            # both; exit 1 if any check fails
  python3 tools/known/checks.py places     # only the places
  python3 tools/known/checks.py water      # only the journeys

places  a place out at sea (a wonder such as the Titan may stand in the water, and a town astride a river's mouth
        over its estuary), or a port or a `coast=True` place more than 2 miles from the shore
water   every leg of every journey as a line (tools/known/travel.py): on land, at sea, by boat, at a ford or a bridge
"""
import os, sys, io, re, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np



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
    """The journeys, leg by leg as lines (tools/known/travel.py; gate rule G16)."""
    import travel
    found, legs, ncx = travel.run()
    bad = sum(len(v) for v in found.values())
    for kind, rows in found.items():
        for k, d, x, y, why in rows[:6]: print(f'  {kind:30s} {k:14s} {d:12s} at {x:.0f},{y:.0f}  {why}')
    print(f'journeys: {legs} moving legs, {bad} off their element or crossing a river with no crossing ({ncx} crossings known)')
    return not bad


if __name__ == '__main__':
    which = sys.argv[1:] or ['places', 'water']
    author, coast, polys = setup()
    ok = True
    if 'places' in which: ok &= check_places(author, polys)
    if 'water' in which: ok &= check_water(author, coast, polys)
    sys.exit(0 if ok else 1)
