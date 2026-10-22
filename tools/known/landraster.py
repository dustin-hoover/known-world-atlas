"""Our land as a raster at 1 mile a pixel, for the land/sea flip check (gate G6).

  python3 tools/known/landraster.py OUT.npz      # rasterise the current map (author.prepare) to OUT.npz
"""
import os, sys, io, contextlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
X0, X1, Y0, Y1, RES = -954, 5850, -5502, 1500, 1.0       # the rasters.js extent, in miles


def polygons():
    import author
    with contextlib.redirect_stdout(io.StringIO()): coast = author.prepare()
    return author, [coast] + [i['pts'] for i in author.ISLANDS if len(i['pts']) > 2]


def rasterise(polys, res=RES):
    from PIL import Image, ImageDraw
    W, H = int((X1 - X0) / res), int((Y1 - Y0) / res)
    im = Image.new('1', (W, H), 0); d = ImageDraw.Draw(im)
    for pl in polys: d.polygon([((x - X0) / res, (Y1 - y) / res) for x, y in pl], fill=1)
    return np.array(im, bool)


def save(path, land):
    np.savez_compressed(path, land=np.packbits(land, axis=1), shape=np.array(land.shape), extent=np.array([X0, X1, Y0, Y1, RES]))


def load(path):
    z = np.load(path); h, w = z['shape']
    return np.unpackbits(z['land'], axis=1)[:, :w].astype(bool)


if __name__ == '__main__':
    _, polys = polygons()
    land = rasterise(polys)
    save(sys.argv[1], land)
    print(f'{sys.argv[1]}: {land.sum():,} sq mi of land, {os.path.getsize(sys.argv[1]) / 1024:.0f} KB')
