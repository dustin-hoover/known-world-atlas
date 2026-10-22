"""The no-tracing check (MAP_V2 §3) for the coast of southern Westeros.

Our coast must meet the official map at its fixed points (tools/known/coast_fixed.py) and differ from it in detail
between them. This lines the official preview up with our map through the places both name (positions only), finds
the official shore (its sea is the blue), and for each stretch between two fixed points measures how much of our
shore runs within TOL miles of the official one. A stretch that hugs it more than LIMIT of the way is reported: there
our line would be too close to theirs, and the stretch needs more of its own detail.

  python3 tools/refs/notrace.py        # needs tools/refs/official/Westeros.jpg (git-ignored); exit 1 if any stretch fails

Nothing from the official map is written anywhere: the check reads it and reports.
"""
import os, sys, json, io, contextlib
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'known'))
IMG = os.path.join(ROOT, 'tools', 'refs', 'official', 'Westeros.jpg')
TOL, LIMIT, MIN_MI = 1.5, 0.6, 30.0

# pixel positions of shared places on the official preview: read on the owner's computer and kept beside the
# image (git-ignored), never in the repository
OFFICIAL = os.path.join(ROOT, 'tools', 'refs', 'official', 'positions.json')


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
    img = np.array(Image.open(IMG).convert('RGB')).astype(int)
    sea = (img[..., 2] > img[..., 0] + 20) & (img[..., 2] > img[..., 1])
    sea = ndi.binary_opening(sea, iterations=1)
    edge = sea & ~ndi.binary_erosion(sea)
    v, u = np.nonzero(edge)
    theirs = fit(np.c_[u + 0.5, v + 0.5]); tree = cKDTree(theirs)
    S = coast_fixed.SOUTH; tc = cKDTree(coast)
    idx = [int(tc.query(xy)[1]) for _, xy, _ in S]
    fails, rows = 0, []
    for i in range(len(S) - 1):
        a, b = idx[i], idx[i + 1]
        seg = coast[a:b + 1] if b >= a else np.vstack([coast[a:], coast[:b + 1]])
        if len(seg) < 3: continue
        L = float(np.hypot(*np.diff(seg, axis=0).T).sum())
        d = tree.query(seg)[0]; near = float((d < TOL).mean())
        meet = float(tree.query(S[i][1])[0])
        bad = L >= MIN_MI and near > LIMIT
        fails += bad
        rows.append((S[i][0], S[i + 1][0], L, near, float(np.median(d)), meet, bad))
    for a, b, L, near, med, meet, bad in rows:
        print(f"{'TOO CLOSE' if bad else 'ok':9s} {a[:34]:34s} -> {b[:34]:34s} {L:6.0f} mi  {near * 100:3.0f}% within {TOL} mi"
              f"  (median {med:4.1f} mi apart; fixed point {meet:4.1f} mi from their shore)")
    print(f'{len(rows)} stretches, {fails} too close to the official line')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
