"""The no-tracing check (MAP_V2 §3) for the coast of southern Westeros: matching positions are allowed, a matching
coastline shape is not.

Our coast meets the published map only at its named anchors (tools/known/coast_fixed.py). This lines the official
preview up with our map through the places both name (positions only), finds the official shore (its sea is the blue),
and tests each stretch between two anchors twice:
  hug    how much of our shore runs within TOL miles of theirs (LIMIT at most), and
  wiggle whether our bends follow theirs: both shores are measured as offsets from the stretch's chord, their slow
         drift taken out, and the two profiles correlated; a stretch whose bends follow theirs (BENDS or more) fails.
Any failing stretch must be redrawn.

  python3 tools/refs/notrace.py              # needs tools/refs/official/ (git-ignored); exit 1 if any stretch fails
  python3 tools/refs/notrace.py --self-test  # the check run on the official shore itself: every stretch must fail

Nothing from the official map is written anywhere: the check reads it and reports.
"""
import os, sys, json, io, contextlib
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'known'))
IMG = os.path.join(ROOT, 'tools', 'refs', 'official', 'Westeros.jpg')
TOL, LIMIT, BENDS, MIN_MI = 1.5, 0.25, 0.5, 30.0
SELF_TEST = '--self-test' in sys.argv

# pixel positions of shared places on the official preview: read on the owner's computer and kept beside the
# image (git-ignored), never in the repository
OFFICIAL = os.path.join(ROOT, 'tools', 'refs', 'official', 'positions.json')


def wiggle(a, b, ours_land, their_land, D=40.0):
    """How far our bends follow theirs between anchors a and b. Along the chord, every mile, each map's land is
    measured across a band D miles either side (how far the land reaches into the band: the shore's offset, read the
    same way for both maps and independently of each other); each profile loses its drift over 40 mi, and the two
    are correlated. Near 1: our bends follow theirs."""
    a, b = np.asarray(a, float), np.asarray(b, float); L = float(np.hypot(*(b - a)))
    if L < 10: return 0.0
    u = (b - a) / L; n = np.array([-u[1], u[0]])
    grid = np.arange(0, L, 1.0); off = np.arange(-D, D + 0.01, 0.5)
    P = a + grid[:, None, None] * u + off[None, :, None] * n             # (along, across, xy)
    flat = P.reshape(-1, 2)
    def profile(land):
        y = land(flat).reshape(len(grid), len(off)).mean(axis=1) * 2 * D
        w = np.exp(-0.5 * (np.arange(-60, 61) / 20.0) ** 2); w /= w.sum()
        return y - np.convolve(np.pad(y, 60, mode='edge'), w, 'valid')
    p, q = profile(ours_land), profile(their_land)
    if p.std() < 1e-6 or q.std() < 1e-6: return 0.0
    return float(np.corrcoef(p, q)[0, 1])


def main():
    if not os.path.exists(IMG) or not os.path.exists(OFFICIAL):
        print('no-tracing check skipped: the official preview and its positions are not on this computer'); return 0
    OFF = json.load(open(OFFICIAL))
    from PIL import Image
    from scipy import ndimage as ndi
    from scipy.spatial import cKDTree
    import author, donor, coast_fixed
    with contextlib.redirect_stdout(io.StringIO()): coast = np.array(author.prepare(), float)
    from shapely.geometry import Polygon
    if not Polygon(coast).exterior.is_ccw: coast = coast[::-1]            # walk it with the land on the left, as the fixed points go
    at = {p[0]: (p[2], p[3]) for p in author.PLACES}
    names = [n for n in OFF if n in at]
    fit = donor.TPS([OFF[n] for n in names], [at[n] for n in names], smooth=0.05)
    back = donor.TPS([at[n] for n in names], [OFF[n] for n in names], smooth=0.05)     # our miles -> their pixels
    img = np.array(Image.open(IMG).convert('RGB')).astype(int)
    sea = (img[..., 2] > img[..., 0] + 20) & (img[..., 2] > img[..., 1])
    sea = ndi.binary_opening(sea, iterations=1)
    edge = sea & ~ndi.binary_erosion(sea)
    v, u = np.nonzero(edge)
    theirs = fit(np.c_[u + 0.5, v + 0.5]); tree = cKDTree(theirs)
    import shapely
    ours_poly = Polygon(coast)
    ours_land = lambda Q: shapely.contains_xy(ours_poly, Q[:, 0], Q[:, 1])
    def their_land(Q):
        px = back(Q); i = np.clip(px[:, 1].astype(int), 0, sea.shape[0] - 1); k = np.clip(px[:, 0].astype(int), 0, sea.shape[1] - 1)
        return ~sea[i, k]
    S = coast_fixed.SOUTH; tc = cKDTree(coast)
    idx = [int(tc.query(xy)[1]) for _, xy, _, _ in S]
    fails, rows = 0, []
    for i in range(len(S) - 1):
        a, b = idx[i], idx[i + 1]
        seg = coast[a:b + 1] if b >= a else np.vstack([coast[a:], coast[:b + 1]])
        if len(seg) < 3: continue
        L = float(np.hypot(*np.diff(seg, axis=0).T).sum())
        d, j = tree.query(seg); near = float((d < TOL).mean())
        meet = float(tree.query(S[i][1])[0])
        bend = wiggle(S[i][1], S[i + 1][1], their_land if SELF_TEST else ours_land, their_land)
        if SELF_TEST: near = 1.0
        bad = L >= MIN_MI and (near > LIMIT or bend >= BENDS)
        fails += bad
        rows.append((S[i][0], S[i + 1][0], L, near, bend, float(np.median(d)), meet, bad))
    for a, b, L, near, bend, med, meet, bad in rows:
        print(f"{'REDRAW' if bad else 'ok':6s} {a[:30]:30s} -> {b[:30]:30s} {L:5.0f} mi  {near * 100:3.0f}% within {TOL} mi"
              f"  bends follow {bend:+.2f}  (median {med:4.1f} mi apart; anchor {meet:4.1f} mi from their shore)")
    print(f'{len(rows)} stretches, {fails} too close to the official line')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
