"""Keep journeys true to the coast: a leg travelled on land never crosses open water, a voyage never crosses land.

Used by cast.build(): each leg of every path is tested against our land (the coast and every island) as a line,
exactly, every quarter mile. A land leg that leaves the land by more than WET miles is replaced by the shortest way
round over land, a sea leg that crosses land (away from the mile at either end where it leaves or reaches a port) by
the shortest way round by sea; the time of the leg is spread over the new route by distance. The way round is found
on a 2-mile grid of the land's core (a mile in from every shore) or the sea's (a mile out), so it keeps clear of the
shore it follows. The same tests are the release gate's rule 16 (tools/known/travel.py).
"""
import math, heapq
import numpy as np


WET, END = 0.25, 1.0       # miles a leg may stray into the other element; miles at a sea leg's ends that may be ashore


class Land:
    R = 2.0

    def __init__(self, rings):
        import shapely
        from shapely.geometry import Polygon
        from shapely.ops import unary_union
        from PIL import Image, ImageDraw
        self.geom = unary_union([Polygon(r).buffer(0) for r in rings if len(r) > 2]); shapely.prepare(self.geom)
        self.edge = self.geom.boundary; shapely.prepare(self.edge)
        xs = [p[0] for r in rings for p in r]; ys = [p[1] for r in rings for p in r]
        self.x0, self.y1 = min(xs) - 60, max(ys) + 60
        W, H = int((max(xs) + 60 - self.x0) / self.R), int((self.y1 - (min(ys) - 60)) / self.R)
        def grid(g):
            im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
            for q in getattr(g, 'geoms', [g]):
                if q.is_empty: continue
                d.polygon([((x - self.x0) / self.R, (self.y1 - y) / self.R) for x, y in q.exterior.coords], fill=255)
                for h in q.interiors: d.polygon([((x - self.x0) / self.R, (self.y1 - y) / self.R) for x, y in h.coords], fill=0)
            return np.array(im) > 0
        self.M = grid(self.geom); self.H, self.W = self.M.shape
        self.core = {True: grid(self.geom.buffer(-1.0)), False: ~grid(self.geom.buffer(1.0))}   # a mile in, a mile out

    def at(self, x, y):
        import shapely
        return bool(shapely.contains_xy(self.geom, x, y))

    def shore(self, p):
        from shapely.geometry import Point
        return self.edge.distance(Point(p[0], p[1]))

    def clear(self, p, want_land=False):
        """Miles from p into the wanted element (0 if p is not in it)."""
        return self.shore(p) if self.at(p[0], p[1]) == want_land else 0.0

    def nearest(self, p, want_land, clear=0.0, reach=120.0):
        """The nearest point at least `clear` miles inside the wanted element, else p itself."""
        from shapely.geometry import Point
        from shapely.ops import nearest_points
        if self.at(p[0], p[1]) == want_land and self.shore(p) >= clear: return tuple(p[:2])
        e = nearest_points(self.edge, Point(p[0], p[1]))[0]
        if e.distance(Point(p[0], p[1])) > reach: return tuple(p[:2])
        for step in (0.3, 0.6, 1.2, 2.5):                              # step off the shore into the wanted element
            for ang in range(0, 360, 15):
                q = (e.x + math.cos(math.radians(ang)) * (clear + step), e.y + math.sin(math.radians(ang)) * (clear + step))
                if self.at(*q) == want_land and self.shore(q) >= min(clear, step) * 0.9: return q
        return (e.x, e.y)

    def to_shore(self, p, out=0.2):
        """The water's edge nearest p, `out` miles off it into the sea (where a voyage starts or ends)."""
        from shapely.geometry import Point
        from shapely.ops import nearest_points
        e = nearest_points(self.edge, Point(p[0], p[1]))[0]
        vx, vy = e.x - p[0], e.y - p[1]; L = math.hypot(vx, vy)
        if L < 1e-9: vx, vy, L = 1.0, 0.0, 1.0
        sgn = 1 if self.at(p[0], p[1]) else -1                         # from the land on out, or from the sea back in
        for k in (1, 2, 3, 5, 8):
            q = (e.x + sgn * vx / L * out * k / 2, e.y + sgn * vy / L * out * k / 2)
            if not self.at(*q): return q
        return self.nearest((e.x, e.y), False, clear=out)

    def crosses(self, a, b, want_land, slack=0.0):
        """True if the segment strays into the other element by more than WET miles, away from `slack` miles at
        either end."""
        import shapely
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(2, int(L / 0.25) + 1)
        u = np.linspace(0, 1, n); xs, ys = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        wrong = shapely.contains_xy(self.geom, xs, ys) != want_land
        wrong &= np.minimum(u, 1 - u) * L > slack
        for i in np.nonzero(wrong)[0]:
            if self.shore((xs[i], ys[i])) > WET: return True
        return False

    def route(self, a, b, want_land, step=3.0):
        """Shortest way from a to b keeping to land (or sea), string-pulled; None if there is none."""
        key = lambda p: (round(p[0] / step), round(p[1] / step))
        # an end out of its element (a ship's port inland, a walker's landing in the shallows) starts from the
        # nearest point of the element
        a0, b0 = a, b
        if self.at(a[0], a[1]) != want_land: a = self.nearest(a, want_land)
        if self.at(b[0], b[1]) != want_land: b = self.nearest(b, want_land)
        s, g = key(a), key(b)
        core = self.core[want_land]
        def ok(c):
            i, j = int((self.y1 - c[1] * step) / self.R), int((c[0] * step - self.x0) / self.R)
            return bool(0 <= i < self.H and 0 <= j < self.W and core[i, j])
        near = lambda c, e: max(abs(c[0] - e[0]), abs(c[1] - e[1])) <= 2
        pq, came, cost = [(0.0, s)], {s: None}, {s: 0.0}
        while pq:
            _, c = heapq.heappop(pq)
            if c == g: break
            if cost[c] > 4 * math.hypot(g[0] - s[0], g[1] - s[1]) + 200: continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (c[0] + dx, c[1] + dy)
                    if n == c or not (ok(n) or near(n, s) or near(n, g)): continue
                    nc = cost[c] + math.hypot(dx, dy)
                    if nc < cost.get(n, 1e18):
                        cost[n] = nc; came[n] = c; heapq.heappush(pq, (nc + math.hypot(g[0] - n[0], g[1] - n[1]), n))
        if g not in came: return None
        path, c = [], g
        while c is not None: path.append((c[0] * step, c[1] * step)); c = came[c]
        path = [tuple(a[:2])] + path[::-1][1:-1] + [tuple(b[:2])]
        out, i = [path[0]], 0
        while i < len(path) - 1:
            j = len(path) - 1
            while j > i + 1 and self.crosses(path[i], path[j], want_land, slack=0.0 if (0 < i and j < len(path) - 1) or want_land else END): j -= 1
            out.append(path[j]); i = j
        if tuple(a0[:2]) != out[0]: out.insert(0, tuple(a0[:2]))
        if tuple(b0[:2]) != out[-1]: out.append(tuple(b0[:2]))
        return out


def route_fine(land, a, b, want_land, res=0.25, margin=15.0, inset=0.3):
    """The way from a to b on a quarter-mile grid of the exact land (or sea), `inset` miles clear of the shore, around
    the leg's own box; None if there is none (or the box is too big for a fine grid)."""
    import shapely
    import skimage.graph
    x0, x1 = min(a[0], b[0]) - margin, max(a[0], b[0]) + margin
    y0, y1 = min(a[1], b[1]) - margin, max(a[1], b[1]) + margin
    W, H = int((x1 - x0) / res) + 1, int((y1 - y0) / res) + 1
    if W * H > 2_500_000: return None
    gx, gy = np.meshgrid(x0 + np.arange(W) * res, y1 - np.arange(H) * res)
    region = land.geom.buffer(-inset) if want_land else None
    if want_land: ok = shapely.contains_xy(region, gx, gy)
    else: ok = ~shapely.contains_xy(land.geom.buffer(inset), gx, gy)
    cell = lambda p: (min(H - 1, max(0, int(round((y1 - p[1]) / res)))), min(W - 1, max(0, int(round((p[0] - x0) / res)))))
    sa, sb = cell(a), cell(b)
    from scipy import ndimage as ndi
    for c in (sa, sb):                                          # the ends may stand on the shore: open a way to them
        rr, cc = np.ogrid[:H, :W]
        ok |= (rr - c[0]) ** 2 + (cc - c[1]) ** 2 <= (inset / res + 3) ** 2
    m = skimage.graph.MCP_Geometric(np.where(ok, 1.0, -1.0))
    cost, _ = m.find_costs([sa], [sb])
    if not np.isfinite(cost[sb]): return None
    path = [(x0 + j * res, y1 - i * res) for i, j in m.traceback(sb)]
    path = [tuple(a[:2])] + path[1:-1] + [tuple(b[:2])]
    out, i = [path[0]], 0
    while i < len(path) - 1:                                    # pull the string tight where the line stays clear
        j = len(path) - 1
        while j > i + 1 and land.crosses(path[i], path[j], want_land, slack=0.0 if (0 < i and j < len(path) - 1) or want_land else END): j -= 1
        out.append(path[j]); i = j
    return out


def keep_to(pts, land, mode_at):
    """pts: [(x, y, t)] -> the same journey with every leg kept to its element. mode_at(t) -> 'land' | 'sea' | None."""
    pts = list(pts)
    for i, p in enumerate(pts):             # a stop between two legs on the same element stands on that element
        a = mode_at((pts[i - 1][2] + p[2]) / 2) if i else None
        b = mode_at((p[2] + pts[i + 1][2]) / 2) if i + 1 < len(pts) else None
        m = a if a == b or b is None else b if a is None else None
        if m is None or land.at(p[0], p[1]) == (m == 'land') or land.shore(p) <= (WET if m == 'land' else END): continue
        q = land.nearest(p, m == 'land', clear=0.3, reach=20.0)
        pts[i] = (q[0], q[1], p[2])
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        m = mode_at((a[2] + b[2]) / 2)
        if m is None or math.hypot(b[0] - a[0], b[1] - a[1]) < 0.25 or not land.crosses(a, b, m == 'land', 0.0 if m == 'land' else END):
            out.append(b); continue
        r = land.route(a, b, m == 'land')
        sl = 0.0 if m == 'land' else END
        if not r or any(land.crosses(p, q, m == 'land', sl if (p == r[0] or q == r[-1]) else 0.0) for p, q in zip(r, r[1:])):
            r = route_fine(land, a, b, m == 'land') or r                # the coarse grid missed a narrow way
        if not r: out.append(b); continue
        L = [0.0]
        for p, q in zip(r, r[1:]): L.append(L[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
        for p, l in zip(r[1:], L[1:]): out.append((p[0], p[1], a[2] + (b[2] - a[2]) * l / (L[-1] or 1)))
    return out


CROSS, TOWN = 2.0, 5.0     # miles: a land leg crosses a river within CROSS of a ford, a bridge or a road's crossing,
                           # or within TOWN of a castle or town on the river (its bridges, ferries and boats)


def unbridged(seg, river, near):
    """The points where a leg crosses a river with no crossing near: none if it crosses an even number of times (the
    line only clips a meander and comes back to the same bank), else every point, unless one of them lies near a
    crossing. near: [(x, y, radius)] of that river's crossings."""
    hits = _points(seg.intersection(river))
    if len(hits) % 2 == 0: return []
    if any(math.hypot(c[0] - g.x, c[1] - g.y) <= c[2] for g in hits for c in near): return []
    return hits


def _points(g):
    return [g] if g.geom_type == 'Point' else [q for q in getattr(g, 'geoms', []) if q.geom_type == 'Point']


def by_crossings(pts, mode_at, rivers, crossings, reach=60.0, passes=4):
    """pts: [(x, y, t)] -> the same journey with every land leg that crosses a river away from a crossing sent by the
    nearest crossing of that river (within `reach` miles), its time spread by distance. rivers: {name: points};
    crossings: [(x, y, label, river)]."""
    from shapely.geometry import LineString
    R = {n: LineString(p) for n, p in rivers.items()}
    on = {}
    for c in crossings: on.setdefault(c[3], []).append((c[0], c[1], c[4] if len(c) > 4 else CROSS))
    pts = list(pts)
    for _ in range(passes):
        out, moved = [pts[0]], False
        for a, b in zip(pts, pts[1:]):
            if mode_at((a[2] + b[2]) / 2) != 'land' or math.hypot(b[0] - a[0], b[1] - a[1]) < 0.25:
                out.append(b); continue
            seg = LineString([a[:2], b[:2]])
            hits = sorted((seg.project(g), n, g) for n, L in R.items() for g in unbridged(seg, L, on.get(n, [])))
            c = None
            if hits:
                _, n, g = hits[0]
                c = min(on.get(n, []), key=lambda c: math.hypot(c[0] - g.x, c[1] - g.y), default=None)
                if c is None or math.hypot(c[0] - g.x, c[1] - g.y) > reach or min(math.hypot(c[0] - a[0], c[1] - a[1]), math.hypot(c[0] - b[0], c[1] - b[1])) < 0.5: c = None
            if c is None: out.append(b); continue
            d1, d2 = math.hypot(c[0] - a[0], c[1] - a[1]), math.hypot(b[0] - c[0], b[1] - c[1])
            out.append((c[0], c[1], a[2] + (b[2] - a[2]) * d1 / ((d1 + d2) or 1))); out.append(b); moved = True
        pts = out
        if not moved: break
    return pts
