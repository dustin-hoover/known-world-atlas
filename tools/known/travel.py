"""Rule 16, travellers: every leg of every journey tested as a line, not sampled over time.

  python3 tools/known/travel.py            # exit 1 on any FAIL
  python3 tools/known/travel.py --list     # every finding, not just the first few per kind

Each leg (one step of a journey to the next) is walked every quarter mile. Its mode is the narrowest MODES window
that covers it (cast.py), or walking:
  land (walk, ride, wheelhouse)  may not leave the land by more than a quarter mile; where it crosses a river (an odd
                                 number of times: a line that clips a meander and comes back is not a crossing) it does
                                 so at a ford, a bridge or a ferry: within 2 miles of a road's crossing, a named or
                                 tagged ford or bridge (cast.py FORDS), or within 5 of a castle or town on the river
  sea (sea, blackship)           may not cross land, except within a mile of a port or landing it leaves or reaches
  boat                           keeps to a river, a lake or the sea's edge (within 1.5 miles of the water)
  dragon                         goes anywhere
Where a journey changes between land and sea (a landing or an embarkation) the point is within a mile of the shore.
A leg no window covers walks: it is a land leg and must pass the land test, so a leg with water on it needs its mode
set by hand (cast.py MODES or a LANE or RIVER step).
"""
import os, sys, io, re, math, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np

LAND_MODES, SEA_MODES, RIVER_MODES, AIR_MODES = {'walk', 'ride', 'wheelhouse'}, {'sea', 'blackship'}, {'boat', 'barrel'}, {'dragon', 'fly'}
STEP, WET, SHORE, CROSS, BOAT = 0.25, 0.25, 1.0, 2.0, 1.5


def world():
    import author, cast, paths
    with contextlib.redirect_stdout(io.StringIO()):
        coast = author.prepare()
        polys = [coast] + [i['pts'] for i in author.ISLANDS if len(i['pts']) > 2]
        cast.build(author.PLACES, author.ROADS, author.STORIES, polys)
    return author, cast, polys


def run(verbose=False):
    import shapely
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import unary_union
    author, cast, polys = world()
    import paths
    land = unary_union([Polygon(pl).buffer(0) for pl in polys]); shapely.prepare(land); edge = land.boundary
    water = unary_union([LineString(r['pts']).buffer(BOAT) for r in author.RIVERS] + [Polygon(l['pts']).buffer(BOAT) for l in author.LAKES]
                        + [edge.buffer(BOAT)]); shapely.prepare(water)
    rivers = [(r['name'], LineString(r['pts'])) for r in author.RIVERS]
    cx = cast.BUILT['crossings']
    full, windows, CHARS, T = cast.BUILT['full'], cast.BUILT['windows'], cast.CHARS, cast.T
    rules = [(re.compile(rx), T(a), T(b), m) for rx, a, b, m in windows]
    def mode(k, t):
        if 'dragon' in CHARS[k]: return 'dragon'
        return next((m for rx, a, b, m in rules if a <= t <= b and rx.search(k)), 'walk')
    def day(t):
        y = int(t // 365) + 1; r = t - (y - 1) * 365; mo = int(r // 30) + 1
        return f'{y} {mo} {r - (mo - 1) * 30 + 1:.1f}'
    found = {'land on water': [], 'sea on land': [], 'landing off the shore': [], 'boat off the water': [], 'river crossed with no crossing': []}
    legs = moving = 0
    for k, P in full.items():
        prev = None
        for (ax, ay, ta), (bx, by, tb) in zip(P, P[1:]):
            L = math.hypot(bx - ax, by - ay)
            if L < STEP: continue
            moving += 1; legs += 1
            m = mode(k, (ta + tb) / 2)
            kind = 'land' if m in LAND_MODES else 'sea' if m in SEA_MODES else 'river' if m in RIVER_MODES else 'air'
            if prev and {prev[0], kind} == {'land', 'sea'}:                 # a landing or an embarkation
                d = edge.distance(Point(ax, ay))
                if d > SHORE: found['landing off the shore'].append((k, day(ta), ax, ay, f'{d:.1f} mi from the shore'))
            prev = (kind, bx, by)
            if kind == 'air': continue
            n = max(2, int(L / STEP) + 1); u = np.linspace(0, 1, n)
            xs, ys = ax + (bx - ax) * u, ay + (by - ay) * u
            if kind == 'land':
                wet = ~shapely.contains_xy(land, xs, ys)
                for i in np.nonzero(wet)[0]:
                    d = edge.distance(Point(xs[i], ys[i]))
                    if d > WET: found['land on water'].append((k, day(ta + (tb - ta) * u[i]), xs[i], ys[i], f'{m}, {d:.1f} mi out')); break
                seg = LineString([(ax, ay), (bx, by)])
                for name, R in rivers:
                    for g in paths.unbridged(seg, R, [(c[0], c[1], c[4]) for c in cx if c[3] == name])[:1]:
                        found['river crossed with no crossing'].append((k, day(ta), g.x, g.y, name))
            elif kind == 'sea':
                dry = shapely.contains_xy(land, xs, ys)
                s = u * L
                for i in np.nonzero(dry)[0]:
                    if min(s[i], L - s[i]) <= SHORE: continue                # leaving or reaching its port
                    d = edge.distance(Point(xs[i], ys[i]))
                    if d > WET: found['sea on land'].append((k, day(ta + (tb - ta) * u[i]), xs[i], ys[i], f'{d:.1f} mi inland')); break
            else:
                off = ~shapely.contains_xy(water, xs, ys) & shapely.contains_xy(land, xs, ys)
                for i in np.nonzero(off)[0]:
                    found['boat off the water'].append((k, day(ta + (tb - ta) * u[i]), xs[i], ys[i], m)); break
    return found, legs, len(cx)


def main():
    found, legs, ncx = run()
    lim = None if '--list' in sys.argv else 6
    bad = 0
    for kind, rows in found.items():
        print(f"{'FAIL' if rows else 'PASS'}  {kind}: {len(rows)}")
        bad += len(rows)
        for k, d, x, y, why in rows[:lim]: print(f'      {k:14s} {d:12s} at {x:7.1f},{y:7.1f}  {why}')
    print(f'{legs} moving legs, {ncx} river crossings known')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
