"""Compare our map with reference maps, and list where they disagree.

Each reference is lined up with our map by the places both name (a least-squares affine fit per region,
dropping outliers). The tool then reports, per reference:
  - places far from where the reference puts them,
  - places one map puts on the coast and the other well inland,
  - settlements the reference names that we lack (each must be found in the books before it is added),
  - islands the reference shows where we have open sea.
It writes Markdown reports to tools/refs/reports/ (git-ignored). It never writes geometry: nothing here may
be used to draw a coast, a border or a place position (LAWS I.2, I.6).

  python3 tools/refs/compare.py            # every reference found in tools/refs/
  python3 tools/refs/compare.py whitehead  # one reference
"""
import sys, os, re, json, math, difflib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'known'))
OUT = os.path.join(HERE, 'reports')

# regions are fitted separately: the references and our map may differ in how Westeros and Essos sit apart
REGIONS = {'Westeros': lambda X, Y: X < 700, 'Essos and beyond': lambda X, Y: X >= 700}
FAR, COAST, INLAND = 100, 6, 25           # miles: a position flag; "on the coast"; "well inland"


# ------------------------------------------------------------------ our map
def ours():
    import author, cast
    coast = author.chaikin(author.WESTEROS, 2)
    author.snap_walls(coast)
    places = {}
    for p in author.PLACES: places[p[0]] = dict(X=p[2], Y=p[3], kind=p[1], realm=p[5])
    for e in cast.EXTRA_PLACES: places.setdefault(e[0], dict(X=e[2], Y=e[3], kind=e[1], realm=e[5]))
    polys = [coast] + [i['pts'] for i in author.ISLANDS]
    return places, Land(polys)


class Land:
    """Our land, rasterised at 2 mi; distance to the shore in miles."""
    R = 2.0

    def __init__(self, polys):
        from PIL import Image, ImageDraw
        from scipy import ndimage
        xs = [p[0] for pl in polys for p in pl]; ys = [p[1] for pl in polys for p in pl]
        self.X0, self.Y1 = min(xs) - 200, max(ys) + 200
        W, H = int((max(xs) + 200 - self.X0) / self.R), int((self.Y1 - (min(ys) - 200)) / self.R)
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        for pl in polys: d.polygon([((x - self.X0) / self.R, (self.Y1 - y) / self.R) for x, y in pl], fill=255)
        self.M = np.array(im) > 0
        self.dland = ndimage.distance_transform_edt(self.M) * self.R      # inside land: miles to the sea
        self.dsea = ndimage.distance_transform_edt(~self.M) * self.R      # at sea: miles to land

    def ij(self, X, Y):
        i, j = int((self.Y1 - Y) / self.R), int((X - self.X0) / self.R)
        return (i, j) if 0 <= i < self.M.shape[0] and 0 <= j < self.M.shape[1] else None

    def shore(self, X, Y):
        """Signed miles to the shore: positive inland, negative at sea."""
        k = self.ij(X, Y)
        if not k: return -999
        return self.dland[k] if self.M[k] else -self.dsea[k]


# ------------------------------------------------------------------ fitting
norm = lambda s: re.sub(r'[^a-z ]', '', s.lower().replace('-', ' ').replace('’', "'").replace("'", '')).replace('the ', '').strip()


def match_names(ref_names, places, cutoff=0.86):
    """{our name: ref name} by fuzzy match of normalised names."""
    rn = {norm(n): n for n in ref_names}
    out = {}
    for name in places:
        m = difflib.get_close_matches(norm(name), rn.keys(), n=1, cutoff=cutoff)
        if m: out[name] = rn[m[0]]
    return out


def fit(pairs):
    """pairs: [(name, (u, v) in ref units, (X, Y) ours)] -> (T, residual miles, kept mask). Affine, outliers dropped."""
    A = np.array([[u, v, 1] for _, (u, v), _ in pairs], float); B = np.array([p for _, _, p in pairs], float)
    keep = np.ones(len(pairs), bool)
    while True:
        T, *_ = np.linalg.lstsq(A[keep], B[keep], rcond=None)
        r = np.hypot(*(A @ T - B).T)
        worst = int(np.argmax(np.where(keep, r, -1)))
        if keep.sum() > 8 and r[worst] > max(3 * np.median(r[keep]), 2 * FAR): keep[worst] = False
        else: return T, r, keep


def to_ours(T, u, v): return tuple(np.array([u, v, 1.0]) @ T)


# ------------------------------------------------------------------ references
class ImageRef:
    """A map image: labels read by OCR, settlement symbols, sea by colour."""

    def __init__(self, key, path, sea_rgb, title):
        self.key, self.path, self.title, self.sea = key, path, title, sea_rgb

    def load(self):
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        self.img = np.array(Image.open(self.path).convert('RGB')).astype(np.int16)
        self.words = self._ocr()
        self.labels = self._labels()
        self.symbols = self._symbols()
        self.water = self._water()

    def _ocr(self):
        cache = os.path.join(os.path.dirname(self.path), 'words.json')
        if os.path.exists(cache): return json.load(open(cache))
        import pytesseract
        from PIL import Image
        im = Image.fromarray(self.img.astype(np.uint8)).convert('L'); W, H = im.size; T, O = 1500, 150; words = []
        for y0 in range(0, H, T):
            for x0 in range(0, W, T):
                box = (max(0, x0 - O), max(0, y0 - O), min(W, x0 + T + O), min(H, y0 + T + O))
                tile = im.crop(box).resize(((box[2] - box[0]) * 2, (box[3] - box[1]) * 2), Image.LANCZOS)
                d = pytesseract.image_to_data(tile, config='--psm 11', output_type=pytesseract.Output.DICT)
                for i, t in enumerate(d['text']):
                    t = t.strip()
                    if len(t) < 2 or float(d['conf'][i]) < 50: continue
                    x, y, w, h = [d[k][i] / 2 for k in ('left', 'top', 'width', 'height')]
                    cx, cy = box[0] + x + w / 2, box[1] + y + h / 2
                    if x0 <= cx < x0 + T and y0 <= cy < y0 + T:
                        words.append([t, round(box[0] + x), round(box[1] + y), round(w), round(h), float(d['conf'][i])])
        json.dump(words, open(cache, 'w'))
        return words

    def _labels(self):
        ws = sorted(self.words, key=lambda w: (w[2], w[1])); used = [False] * len(ws); labels = []
        for i, w in enumerate(ws):
            if used[i]: continue
            grp = [w]; used[i] = True; grown = True
            while grown:
                grown = False
                last = max(grp, key=lambda g: g[1] + g[3]); h = max(g[4] for g in grp)
                for j, v in enumerate(ws):
                    if not used[j] and abs((v[2] + v[4] / 2) - (last[2] + last[4] / 2)) < 0.6 * h and 0 <= v[1] - (last[1] + last[3]) < 1.3 * h:
                        grp.append(v); used[j] = True; grown = True; break
            grp.sort(key=lambda g: g[1])
            labels.append({'text': ' '.join(g[0] for g in grp), 'box': [min(g[1] for g in grp), min(g[2] for g in grp),
                           max(g[1] + g[3] for g in grp), max(g[2] + g[4] for g in grp)]})
        return labels

    def _symbols(self):
        from scipy import ndimage
        dark = self.img.max(axis=2) < 70
        for w in self.words: dark[max(0, w[2] - 2):w[2] + w[4] + 2, max(0, w[1] - 2):w[1] + w[3] + 2] = False
        lab, n = ndimage.label(dark)
        size = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1)); cm = ndimage.center_of_mass(dark, lab, range(1, n + 1))
        return np.array([(c[1], c[0]) for c, s in zip(cm, size) if 25 <= s <= 900])

    def _water(self):
        from scipy import ndimage
        sea = (np.abs(self.img - np.array(self.sea)).sum(axis=2) < 18)
        txt = np.zeros(sea.shape, bool)                      # labels written over the sea are not land
        for w in self.words: txt[max(0, w[2] - 3):w[2] + w[4] + 3, max(0, w[1] - 3):w[1] + w[3] + 3] = True
        around = ndimage.binary_dilation(sea, iterations=4)
        sea = sea | (txt & around)
        sea = ndimage.binary_closing(sea, iterations=3)      # lines drawn over the sea
        lab, n = ndimage.label(sea)
        size = ndimage.sum(sea, lab, range(1, n + 1))
        return np.isin(lab, 1 + np.nonzero(size > 20000)[0])  # open sea and great bays; lakes left out

    def symbol_for(self, label):
        x0, y0, x1, y1 = label['box']; h = y1 - y0; S = self.symbols
        dx = np.maximum(0, np.maximum(x0 - S[:, 0], S[:, 0] - x1)); dy = np.maximum(0, np.maximum(y0 - S[:, 1], S[:, 1] - y1))
        d = np.hypot(dx, dy); k = int(np.argmin(d))
        return tuple(S[k]) if d[k] <= 2.5 * h else None

    def points(self):
        """{label text: (u, v)} for labels with a settlement symbol beside them."""
        out = {}
        for l in self.labels:
            s = self.symbol_for(l)
            if s is not None and len(norm(l['text'])) >= 3: out.setdefault(l['text'], s)
        return out

    def shore(self, u, v, px_mi):
        """Signed miles to the reference's shore: positive inland."""
        from scipy import ndimage
        if not hasattr(self, '_dl'):
            self._dl = ndimage.distance_transform_edt(~self.water); self._ds = ndimage.distance_transform_edt(self.water)
        i, j = int(v), int(u)
        if not (0 <= i < self.water.shape[0] and 0 <= j < self.water.shape[1]): return None
        return (self._dl[i, j] if not self.water[i, j] else -self._ds[i, j]) * px_mi

    def islands(self):
        """Land patches wholly surrounded by the sea: [(u, v, area px)]."""
        from scipy import ndimage
        lab, n = ndimage.label(~self.water)
        size = ndimage.sum(~self.water, lab, range(1, n + 1)); cm = ndimage.center_of_mass(~self.water, lab, range(1, n + 1))
        big = max(size)
        return [(c[1], c[0], s) for c, s in zip(cm, size) if 150 < s < big * 0.05]


class PointRef:
    """A list of named points in the reference's own units (e.g. an online map's lat/lng)."""

    def __init__(self, key, title, pts):
        self.key, self.title, self._pts = key, title, pts

    def load(self): pass
    def points(self): return self._pts
    def shore(self, *a): return None
    def islands(self): return []


def quartermaester():
    path = os.path.join(HERE, 'quartermaester', 'ASoIaF-overlays.js')
    if not os.path.exists(path): return None
    pts = {}
    for key, lat, lng in re.findall(r'([A-Za-z_\']+):\s*\{lat:\s*([-0-9.]+),\s*lng:\s*([-0-9.]+)', open(path).read()):
        # a web map: undo the Mercator stretch so the units are flat (u east, v south, like an image)
        y = math.degrees(math.log(math.tan(math.pi / 4 + math.radians(float(lat)) / 2)))
        pts.setdefault(key.replace('_', ' '), (float(lng), -y))
    return PointRef('quartermaester', 'Quartermaester place markers', pts)


def references():
    refs = []
    p = os.path.join(HERE, 'whitehead', 'known-world-detailed.png')
    if os.path.exists(p): refs.append(ImageRef('whitehead', p, (165, 192, 222), 'Adam Whitehead, the Known World (2014)'))
    q = quartermaester()
    if q: refs.append(q)
    return refs


# ------------------------------------------------------------------ the report
def report(ref, places, land):
    ref.load()
    pts = ref.points()
    m = match_names(pts.keys(), places)
    lines = [f'# {ref.title}', '', 'Flags only. Every item is a question for the books; nothing here is a position or a shape to copy.', '']
    found_names = set(m.values())
    for region, inside in REGIONS.items():
        pairs = [(n, pts[m[n]], (places[n]['X'], places[n]['Y'])) for n in m if inside(places[n]['X'], places[n]['Y'])]
        if len(pairs) < 6:
            lines += [f'## {region}', '', f'Only {len(pairs)} places in common: too few to line up.', '']; continue
        T, r, keep = fit(pairs)
        px_mi = math.sqrt(abs(np.linalg.det(T[:2])))
        sx, sy = np.hypot(*T[0]), np.hypot(*T[1])
        lines += [f'## {region}', '',
                  f'{len(pairs)} places in common, {int(keep.sum())} used for the fit. Median distance after fitting: '
                  f'{np.median(r[keep]):.0f} mi. Shape: our map is {100 * (sx / sy - 1):+.0f}% wider east–west than the reference, '
                  f'relative to its north–south length.', '']
        far = sorted([(ri, n) for (n, _, _), ri in zip(pairs, r) if ri > FAR], reverse=True)
        if far:
            lines += ['### Places far from where the reference puts them', '', '| Place | Miles | Direction the reference puts it |', '|---|---|---|']
            for ri, n in far:
                u, v = pts[m[n]]; X, Y = to_ours(T, u, v); p = places[n]
                ang = math.degrees(math.atan2(Y - p['Y'], X - p['X']))
                lines.append(f'| {n} | {ri:.0f} | {compass(ang)} |')
            lines.append('')
        coast = []
        for n, (u, v), (X, Y) in pairs:
            ours_s = land.shore(X, Y); ref_s = ref.shore(u, v, px_mi)
            if ref_s is None: continue
            if ours_s <= COAST and ref_s >= INLAND: coast.append((n, f'on our coast ({ours_s:.0f} mi), {ref_s:.0f} mi inland on the reference'))
            if ref_s <= COAST and ours_s >= INLAND: coast.append((n, f'{ours_s:.0f} mi inland on ours, on the reference\'s coast'))
            if ours_s < -1 and ref_s > 2: coast.append((n, f'in the sea on ours ({-ours_s:.0f} mi out), on land on the reference'))
        if coast:
            lines += ['### Coast or inland', ''] + [f'- **{n}**: {t}' for n, t in coast] + ['']
        isl = []
        for u, v, a in ref.islands():
            X, Y = to_ours(T, u, v)
            if not inside(X, Y) or land.shore(X, Y) > -15: continue
            near = min(ref.labels, key=lambda l: math.hypot((l['box'][0] + l['box'][2]) / 2 - u, (l['box'][1] + l['box'][3]) / 2 - v)) if hasattr(ref, 'labels') else None
            isl.append((a * px_mi * px_mi, X, Y, near['text'] if near else ''))
        if isl:
            lines += ['### Islands the reference shows where we have open sea', '', '| Nearest label on the reference | Size (sq mi) | Where on ours |', '|---|---|---|']
            for a, X, Y, t in sorted(isl, reverse=True)[:40]: lines.append(f'| {t} | {a:.0f} | {X:.0f}, {Y:.0f} |')
            lines.append('')
        miss = []
        for name, (u, v) in pts.items():
            if name in found_names: continue
            X, Y = to_ours(T, u, v)
            c = clean(name)
            if len(c) < 4 or (c.isupper() and ' ' in c) or not re.search(r'[aeiouy]', c.lower()): continue
            if inside(X, Y) and land.shore(X, Y) > -30: miss.append((name, X, Y))
        if miss:
            lines += ['### Names the reference shows that we lack', '', 'Add one only when the books name it. Positions are not to be copied.', '']
            lines += [', '.join(sorted({clean(n) for n, _, _ in miss})), '']
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, ref.key + '.md'); open(path, 'w').write('\n'.join(lines))
    return path


def compass(a):
    return ['east', 'north-east', 'north', 'north-west', 'west', 'south-west', 'south', 'south-east'][int(((a % 360) + 22.5) // 45) % 8]


def clean(s): return re.sub(r'[^A-Za-z\' -]', '', s).strip()


if __name__ == '__main__':
    places, land = ours()
    want = sys.argv[1:]
    for ref in references():
        if want and ref.key not in want: continue
        print('wrote', report(ref, places, land))
