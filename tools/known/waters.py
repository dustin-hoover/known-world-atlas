"""Sea inlets and enclosed waters (gate rule 9b): a false gulf is a stretch of sea that reaches more than DEPTH miles
into the land through a mouth narrower than its reach, and is not one of the waters the books name.

An inlet is sea that a disc of radius r cannot reach from the open ocean (r = 3, 8 and 15 miles: mouths narrower than
6, 16 and 30 miles); its depth is the farthest it runs, through the water, from where such a disc can still go.
Named waters (NAMED: a point inside each, or a box) are kept; the rest are filled by the coast builders
(tools/known/shores.py) and fail the gate (tools/known/gate.py).
"""
import numpy as np

DEPTH = 15.0                 # miles
RADII = (3.0, 8.0, 15.0)     # miles
RES = 0.5                    # miles a pixel

# waters the books name, by a point in each (X, Y), or a box (X0, X1, Y0, Y1) for a group of sounds
NAMED = {
    'Blazewater Bay': (-260, -40, -400, -300), "Ironman's Bay": (-440, -40, -880, -640), 'The Whispering Sound': (-540, -430, -2320, -2190),
    'The Redwyne Straits': (-560, -430, -2560, -2340), 'The Sea of Dorne': (140, 660, -2230, -1930), 'Shipbreaker Bay': (380, 560, -1700, -1450),
    'Blackwater Bay': (260, 520, -1320, -1130), 'The Gullet': (420, 520, -1180, -1080), 'The Bay of Crabs': (220, 560, -1000, -860),
    'The Bite': (90, 460, -560, -380), 'The Bay of Seals': (150, 450, 400, 560), 'The Bay of Ice': (-260, -140, 380, 480),
    "The Fingers' sounds": (380, 620, -770, -470), 'The Narrow Sea': (650, -900), "Slaver's Bay": (2350, 2800, -2250, -1900),
    'The Gulf of Grief': (2150, -2450), 'The Smoking Sea': (1450, 2350, -2950, -2350), 'The Braavos lagoon': (740, 790, -520, -460),
    'The Bay of Dragons': (2650, -2000), 'The mouths of the Rhoyne': (1380, 1460, -2260, -2150), 'The Jade Sea': (4500, -2900),
    'The Sea of Myrth': (760, -1500),
}


def _named_mask(x0, y1, W, H, res):
    from PIL import Image, ImageDraw
    im = Image.new('1', (W, H), 0); d = ImageDraw.Draw(im)
    for v in NAMED.values():
        if len(v) == 2:
            u, w = (v[0] - x0) / res, (y1 - v[1]) / res; d.ellipse([u - 4, w - 4, u + 4, w + 4], fill=1)
        else:
            d.rectangle([(v[0] - x0) / res, (y1 - v[3]) / res, (v[1] - x0) / res, (y1 - v[2]) / res], fill=1)
    return np.array(im, bool)


def inlets(polys, box, res=RES, depth=DEPTH, radii=RADII, named=True):
    """polys: land rings [(X, Y)...]; box: (X0, X1, Y0, Y1) to look in (margin added).
    -> [{'depth', 'area', 'r', 'X', 'Y', 'mask', 'named'}], and the frame (x0, y1, res) of the masks."""
    from PIL import Image, ImageDraw
    from scipy import ndimage as ndi
    import skimage.graph
    m = max(radii) * 3 + 10
    x0, x1, y0, y1 = box[0] - m, box[1] + m, box[2] - m, box[3] + m
    W, H = int((x1 - x0) / res), int((y1 - y0) / res)
    im = Image.new('1', (W, H), 0); d = ImageDraw.Draw(im)
    for pl in polys:
        q = np.asarray(pl, float)
        if q[:, 0].max() < x0 or q[:, 0].min() > x1 or q[:, 1].max() < y0 or q[:, 1].min() > y1: continue
        d.polygon([((x - x0) / res, (y1 - y) / res) for x, y in q], fill=1)
    land = np.array(im, bool); sea = ~land
    land_lab, _ = ndi.label(land)
    keep = _named_mask(x0, y1, W, H, res) if named else np.zeros_like(sea)
    found, seen = [], np.zeros_like(sea)
    lab_sea, _ = ndi.label(sea)
    to_land = ndi.distance_transform_edt(sea)                       # pixels from each sea pixel to the land
    for r in radii:
        rp = r / res
        centres = to_land >= rp                                         # where a disc of radius r fits
        opened = ndi.distance_transform_edt(~centres) <= rp             # everywhere such a disc covers
        lab, n = ndi.label(opened)
        edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); edge = edge[edge > 0]
        ocean = np.isin(lab, edge)                                      # ...going from the open sea
        reach = ocean | ~np.isin(lab_sea, np.unique(lab_sea[ocean]))    # enclosed waters are counted separately below
        rest = sea & ~reach
        cl, cn = ndi.label(rest)
        for i, sl in enumerate(ndi.find_objects(cl), 1):
            if sl is None: continue
            g = 4 + int(depth / res)                                    # its depth, through the water, from the open sea
            s0, s1 = slice(max(0, sl[0].start - g), sl[0].stop + g), slice(max(0, sl[1].start - g), sl[1].stop + g)
            comp_b = cl[s0, s1] == i
            if comp_b.sum() * res * res < depth: continue
            src = np.argwhere(ocean[s0, s1] & ndi.binary_dilation(comp_b, iterations=2))
            if not len(src): continue
            mcp = skimage.graph.MCP_Geometric(np.where(sea[s0, s1], 1.0, -1.0))
            dist, _ = mcp.find_costs(src)
            dmax = float(np.max(np.where(comp_b, dist, 0))) * res
            if dmax <= depth: continue
            full = np.zeros_like(sea); full[s0, s1] = comp_b
            if (full & seen).sum() > comp_b.sum() * 0.5: continue       # already found at a smaller radius
            shores = np.unique(land_lab[s0, s1][ndi.binary_dilation(comp_b, iterations=3) & (land_lab[s0, s1] > 0)])
            if len(shores) > 1: continue                                 # a strait between two lands, not an inlet
            seen |= full
            yy, xx = np.nonzero(full)
            found.append({'depth': round(dmax, 1), 'area': round(comp_b.sum() * res * res, 1), 'r': r,
                          'X': round(x0 + xx.mean() * res, 1), 'Y': round(y1 - yy.mean() * res, 1),
                          'mask': full, 'named': bool((full & keep).any())})
    # enclosed waters: sea with no way out to the open ocean at all
    edge = np.unique(np.r_[lab_sea[0], lab_sea[-1], lab_sea[:, 0], lab_sea[:, -1]]); edge = edge[edge > 0]
    for i, sl in enumerate(ndi.find_objects(lab_sea), 1):
        if i in edge or sl is None: continue
        comp = lab_sea[sl] == i
        a = comp.sum() * res * res
        if a < 25: continue
        full = np.zeros_like(sea); full[sl] = comp; yy, xx = np.nonzero(comp)
        found.append({'depth': None, 'area': round(a, 1), 'r': 0, 'X': round(x0 + (xx.mean() + sl[1].start) * res, 1),
                      'Y': round(y1 - (yy.mean() + sl[0].start) * res, 1), 'mask': full, 'named': bool((full & keep).any()), 'enclosed': True})
    return found, (x0, y1, res)


def fill(ring, others, box, res=RES, depth=DEPTH, keep=(), absorb=None):
    """The ring with its unnamed inlets (deeper than `depth`) filled; `others` are the other land rings, which stay
    apart (a strait between two lands is never filled) unless `absorb[i]` says the other may join the land (an unnamed
    islet in a filled inlet), and so does any water at a point in `keep` (the coast's named anchors must stay on the
    shore). -> (new ring, [filled inlets], {indices of `others` absorbed})."""
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    from skimage import measure
    main = Polygon(ring).buffer(0)
    others = list(others); absorb = list(absorb) if absorb is not None else [False] * len(others)
    oth = [Polygon(o).buffer(0) if len(o) > 2 else Polygon() for o in others]
    found, (x0, y1, rs) = inlets([ring] + list(others), box, res, depth)
    adds, done, gone = [], [], set()
    for f in found:
        if f['named']: continue
        parts = []
        for c in measure.find_contours(np.pad(f['mask'], 1).astype(float), 0.5):
            q = np.c_[x0 + (c[:, 1] - 1) * rs, y1 - (c[:, 0] - 1) * rs]
            if len(q) > 3: parts.append(Polygon(q).buffer(0))
        if not parts: continue
        g = unary_union(parts).buffer(rs * 1.5)
        if not g.intersects(main): continue                                        # not ours
        touch = [i for i, o in enumerate(oth) if not o.is_empty and g.intersects(o)]
        if any(not absorb[i] for i in touch): continue                             # a strait beside a named island
        if any(g.distance(Point(*k)) < 2.0 for k in keep): continue                # water at a named anchor
        adds.append(unary_union([g] + [oth[i] for i in touch])); gone.update(touch); done.append({k: v for k, v in f.items() if k != 'mask'})
    if not adds: return [list(p) for p in ring], [], set()
    g = unary_union([main] + adds)
    g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
    out = [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]
    if not Polygon(out).is_valid:                                      # rounding can pinch a ring: mend it
        h = Polygon(out).buffer(0); h = max(getattr(h, 'geoms', [h]), key=lambda q: q.area)
        out = [[round(x, 3), round(y, 3)] for x, y in list(h.exterior.coords)[:-1]]
    return out, done, gone
