"""Keep journeys true to the coast: a leg travelled on land never crosses open water, a voyage never crosses land.

Used by cast.build(): each leg of every path is checked against our land (the coast and every island, rasterised
at 2 miles). A land leg that crosses water is replaced by the shortest way round over land, a sea leg that crosses
land by the shortest way round by sea; the time of the leg is spread over the new route by distance. Endpoints
may sit a little off their element (a port on the shore, a ship arriving at a quay).
"""
import math, heapq
import numpy as np


class Land:
    R = 2.0

    def __init__(self, rings):
        from PIL import Image, ImageDraw
        xs = [p[0] for r in rings for p in r]; ys = [p[1] for r in rings for p in r]
        self.x0, self.y1 = min(xs) - 60, max(ys) + 60
        W, H = int((max(xs) + 60 - self.x0) / self.R), int((self.y1 - (min(ys) - 60)) / self.R)
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        for r in rings: d.polygon([((x - self.x0) / self.R, (self.y1 - y) / self.R) for x, y in r], fill=255)
        self.M = np.array(im) > 0; self.H, self.W = self.M.shape

    def at(self, x, y):
        i, j = int((self.y1 - y) / self.R), int((x - self.x0) / self.R)
        return bool(0 <= i < self.H and 0 <= j < self.W and self.M[i, j])

    def clear(self, p, want_land=False):
        """Miles from p to the other element (0 if p is not in the wanted one)."""
        if not hasattr(self, 'D'):
            from scipy.ndimage import distance_transform_edt
            self.D = {False: distance_transform_edt(~self.M) * self.R, True: distance_transform_edt(self.M) * self.R}
        i, j = int((self.y1 - p[1]) / self.R), int((p[0] - self.x0) / self.R)
        return float(self.D[want_land][i, j]) if 0 <= i < self.H and 0 <= j < self.W else (0.0 if want_land else 99.0)

    def nearest(self, p, want_land, clear=0.0, reach=120.0):
        """The nearest point at least `clear` miles inside the wanted element (within `reach`), else p itself."""
        self.clear(p)
        i, j = int((self.y1 - p[1]) / self.R), int((p[0] - self.x0) / self.R); r = int(reach / self.R)
        i0, i1, j0, j1 = max(0, i - r), min(self.H, i + r + 1), max(0, j - r), min(self.W, j + r + 1)
        ok = self.D[want_land][i0:i1, j0:j1] > max(clear, 0.1)
        if not ok.any(): return tuple(p[:2])
        ii, jj = np.nonzero(ok); k = np.argmin((ii + i0 - i) ** 2 + (jj + j0 - j) ** 2)
        return (self.x0 + (jj[k] + j0 + 0.5) * self.R, self.y1 - (ii[k] + i0 + 0.5) * self.R)

    def crosses(self, a, b, want_land, slack=4.0):
        """True if the segment leaves its element by more than `slack` miles from either end."""
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(2, int(L / 1.5))
        for k in range(1, n):
            t = k / n
            if min(t, 1 - t) * L < slack: continue
            if self.at(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) != want_land: return True
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
        ok = lambda c: self.at(c[0] * step, c[1] * step) == want_land
        near = lambda c, e: max(abs(c[0] - e[0]), abs(c[1] - e[1])) <= 1
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
            while j > i + 1 and self.crosses(path[i], path[j], want_land, slack=0.0 if 0 < i and j < len(path) - 1 else 4.0): j -= 1
            out.append(path[j]); i = j
        if tuple(a0[:2]) != out[0]: out.insert(0, tuple(a0[:2]))
        if tuple(b0[:2]) != out[-1]: out.append(tuple(b0[:2]))
        return out


def keep_to(pts, land, mode_at):
    """pts: [(x, y, t)] -> the same journey with every leg kept to its element. mode_at(t) -> 'land' | 'sea' | None."""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        m = mode_at((a[2] + b[2]) / 2)
        if m is None or math.hypot(b[0] - a[0], b[1] - a[1]) < 1 or not land.crosses(a, b, m == 'land'):
            out.append(b); continue
        r = land.route(a, b, m == 'land')
        if not r: out.append(b); continue
        L = [0.0]
        for p, q in zip(r, r[1:]): L.append(L[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
        for p, l in zip(r[1:], L[1:]): out.append((p[0], p[1], a[2] + (b[2] - a[2]) * l / (L[-1] or 1)))
    return out
