"""Realm and people borders that follow the land (used by author.py).

The hand-drawn realm outlines in author.py are only claims: rough shapes saying roughly where each realm lies. Here
they are fitted to our own physical geography:
  * every border at the sea follows the authored coast exactly (only land is ever assigned);
  * inland, each realm grows outward from its core (its claim, shrunk) and from its castles and towns (each place's
    realm in PLACES) by cost distance, and mountain ranges, the Wall and (a little) rivers are costly to cross, so
    where two realms meet, the border settles on the ridge, the Wall or the river between them;
  * islands go to the realm across the nearest strait, unless they have places of their own.
Nothing here is traced from any published map: the inputs are the coasts, ranges, rivers and places we authored.
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage.graph import MCP_Geometric
from skimage.measure import find_contours, approximate_polygon

STEP = 4.0                                  # miles per cell
X0, X1, Y0, Y1 = -800.0, 5000.0, -3300.0, 1500.0
W, H = int((X1 - X0) / STEP), int((Y1 - Y0) / STEP)


def _px(p): return ((p[0] - X0) / STEP, (Y1 - p[1]) / STEP)
def _xy(r, c): return [round(X0 + (c + 0.5) * STEP, 1), round(Y1 - (r + 0.5) * STEP, 1)]


def _poly_mask(polys):
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    for pts in polys:
        if len(pts) > 2: d.polygon([_px(p) for p in pts], fill=1)
    return np.array(im, bool)


def _line_mask(lines):
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    for pts, w in lines:
        d.line([_px(p) for p in pts], fill=1, width=max(1, int(round(w / STEP))))
    return np.array(im, bool)


def land_mask(coast, islands):
    return _poly_mask([coast] + [i['pts'] for i in islands])


def fit(claims, places, coast, islands, ranges, rivers, walls, island_realms=(), reach=380.0, big_island=2.0e5):
    """claims: [{name, color, pts}] -> the same realms with pts/parts fitted to the land, and a label point."""
    land = land_mask(coast, islands)
    cost = np.where(land, 1.0, 40.0)                                       # the sea can be crossed, dearly
    cost[_line_mask([(r['pts'], max(18.0, r.get('w', 30) * 0.8)) for r in ranges]) & land] += 30.0
    cost[_line_mask([(r['pts'], 6.0) for r in rivers]) & land] += 4.0
    cost[_line_mask([(w['pts'], 6.0) for w in walls])] += 4000.0            # the Wall is the border
    names = [c['name'] for c in claims]
    # small islands (not the continents): each belongs to the realm of its own places, if it has any
    isle_lab = np.full((H, W), -1, int); isles = np.zeros((H, W), bool)
    for i in islands:
        m = _poly_mask([i['pts']])
        if m.sum() * STEP * STEP > big_island: continue
        isles |= m
        inside = [p[5] for p in places if p[2] is not None and m[min(H - 1, max(0, int(_px((p[2], p[3]))[1]))), min(W - 1, max(0, int(_px((p[2], p[3]))[0])))]]
        own = [n for n in inside if n in names]
        if own: isle_lab[m] = names.index(max(set(own), key=own.count))
    dist = np.full((len(claims), H, W), np.inf, np.float32)
    for k, c in enumerate(claims):
        claim = _poly_mask([c['pts']]) & land
        core = ndimage.binary_erosion(claim, iterations=int(45 / STEP)) if claim.sum() > 400 else claim
        if not core.any(): core = claim
        seeds = list(zip(*np.nonzero(core)))
        for p in places:
            if p[5] == c['name'] and p[2] is not None:
                r, cc = _px((p[2], p[3]))[::-1]
                r, cc = int(r), int(cc)
                if 0 <= r < H and 0 <= cc < W and land[r, cc]: seeds.append((r, cc))
        if not seeds: continue
        if c['name'] in island_realms: seeds = [q for q in seeds if isles[q]]; 
        if not seeds: continue
        m = MCP_Geometric(np.where(isles, cost, np.inf) if c['name'] in island_realms else cost)
        d, _ = m.find_costs(seeds)
        dist[k] = d
    lab = np.argmin(dist, 0); best = np.min(dist, 0)
    lab[~land | ~np.isfinite(best) | (best > reach / STEP)] = -1          # far lands nobody claims stay unclaimed
    lab[isle_lab >= 0] = isle_lab[isle_lab >= 0]
    out = []
    for k, c in enumerate(claims):
        m = lab == k
        m = ndimage.binary_fill_holes(lab == k)
        rings = []
        lbl, n = ndimage.label(m)
        sizes = ndimage.sum(m, lbl, range(1, n + 1)) if n else []
        for i, sz in enumerate(sizes, 1):
            if sz < 2: continue                                             # specks
            part = np.pad(lbl == i, 1)
            cs = find_contours(part.astype(float), 0.5)
            if not cs: continue
            ring = max(cs, key=len)
            ring = approximate_polygon(ring, tolerance=0.6)
            rings.append((sz, [_xy(r - 1, cc - 1) for r, cc in ring[:-1]], i))
        if not rings: continue
        rings.sort(key=lambda t: -t[0])
        # the label sits at the cell deepest inside the largest piece
        dt = ndimage.distance_transform_edt(lbl == rings[0][2])
        r, cc = np.unravel_index(np.argmax(dt), dt.shape)
        o = {'name': c['name'], 'color': c['color'], 'pts': rings[0][1], 'label': _xy(r, cc)}
        if len(rings) > 1: o['parts'] = [q for _, q, _ in rings[1:]]
        out.append(o)
    return out


def clip_peoples(peoples, coast, islands):
    """Peoples' areas cut to the land: [{..., pts}] -> pts/parts on land only."""
    land = land_mask(coast, islands)
    out = []
    for p in peoples:
        m = _poly_mask([p['pts']]) & land
        m = ndimage.binary_fill_holes(ndimage.binary_opening(m, iterations=1))
        lbl, n = ndimage.label(m)
        rings = []
        for i in range(1, n + 1):
            part = lbl == i
            sz = part.sum()
            if sz < 6: continue
            cs = find_contours(np.pad(part, 1).astype(float), 0.5)
            ring = approximate_polygon(max(cs, key=len), tolerance=0.6)
            rings.append((sz, [_xy(r - 1, c - 1) for r, c in ring[:-1]]))
        if not rings: continue
        rings.sort(key=lambda t: -t[0])
        q = dict(p); q['pts'] = rings[0][1]
        if len(rings) > 1: q['parts'] = [r for _, r in rings[1:]]
        out.append(q)
    return out
