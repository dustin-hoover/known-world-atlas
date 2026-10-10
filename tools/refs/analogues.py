"""Sample the Earth analogues of our mountains and hills (docs/otherworldly/got/EARTH_ANALOGUES.md).

Downloads Copernicus DEM GLO-90 tiles (© DLR and © Airbus, provided under COPERNICUS by the EU and ESA; free for
any use with this credit) into tools/refs/earth/dem/ (git-ignored), then for each analogue writes a hillshade to
tools/shots/analogues/ and prints what we measure:
  peak     highest point (m)            relief   95th - 5th percentile height (m)
  valley   median height of the lowest quarter (m)
  slope    median and 90th percentile slope (degrees)
  ridge    dominant spacing between ridges (km), from the elevation's spectrum
  hyps     hypsometric integral (0 = low land with a few spires, 1 = a high plateau cut by gorges)

  python3 tools/refs/analogues.py            # all
  python3 tools/refs/analogues.py Frostfangs # one
"""
import os, sys, math, json, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DEM = os.path.join(HERE, 'earth', 'dem')
SHOTS = os.path.join(ROOT, 'tools', 'shots', 'analogues')

# name of ours: (analogue, lat0, lat1, lon0, lon1, our height m)
ANALOGUES = {
    'The Frostfangs': ('Brooks Range', 67.5, 68.5, -151, -148, 3000),
    'Mountains of the Moon': ('Bernese Alps', 46.0, 47.0, 7.0, 9.0, 3400),
    "The Giant's Lance": ('Matterhorn and Monte Rosa', 45.8, 46.1, 7.5, 8.0, 4300),
    'The Red Mountains': ('Hajar Mountains', 22.8, 23.6, 56.8, 58.2, 3000),
    'The Dornish Marches': ('Anti-Atlas foothills', 29.5, 30.3, -8.8, -7.2, 500),
    'The Bones': ('Sierra Nevada', 36.0, 39.0, -120.0, -118.0, 3600),
    'Mountains of the Shadow': ('Yemen Highlands', 14.8, 15.8, 43.3, 44.5, 4200),
    'The Velvet Hills': ('Chianti hills', 43.3, 43.8, 11.0, 11.7, 900),
    'The Westerlands hills': ('Asturias and Leon', 42.3, 43.5, -7.0, -5.5, 900),
    'The Barrowlands': ('Yorkshire Wolds', 53.9, 54.2, -0.9, -0.2, 260),
    'Dragonmont': ('Stromboli', 38.7, 38.9, 15.1, 15.3, 1100),
    'The Fourteen Flames': ('Tibesti volcanoes', 19.5, 21.5, 17.0, 19.0, 2600),
    'The Mother of Mountains': ('Ulytau', 48.4, 48.9, 66.5, 67.3, 1500),
}


def tile_url(lat, lon):
    ns, ew = ('N' if lat >= 0 else 'S'), ('E' if lon >= 0 else 'W')
    name = f'Copernicus_DSM_COG_30_{ns}{abs(lat):02d}_00_{ew}{abs(lon):03d}_00_DEM'
    return name, f'https://copernicus-dem-90m.s3.amazonaws.com/{name}/{name}.tif'


def load_box(lat0, lat1, lon0, lon1):
    """Mosaic of the 1° tiles covering the box, cropped to it; (heights m, metres per pixel x, y)."""
    import tifffile
    os.makedirs(DEM, exist_ok=True)
    rows = []
    for la in range(math.floor(lat1 - 1e-9), math.floor(lat0) - 1, -1):         # north to south
        row = []
        for lo in range(math.floor(lon0), math.ceil(lon1)):
            name, url = tile_url(la, lo)
            path = os.path.join(DEM, name + '.tif')
            if not os.path.exists(path):
                try: urllib.request.urlretrieve(url, path)
                except Exception: path = None                      # open sea: no tile
            a = tifffile.imread(path).astype(np.float32) if path else np.zeros((1200, 1200), np.float32)
            if a.shape[1] != 1200:                                  # high-latitude tiles are narrower: resample to 1200
                a = np.array([np.interp(np.linspace(0, a.shape[1] - 1, 1200), np.arange(a.shape[1]), r) for r in a], np.float32)
            row.append(a)
        rows.append(np.hstack(row))
    m = np.vstack(rows)
    H, W = m.shape; n0, w0 = math.floor(lat1 - 1e-9) + 1, math.floor(lon0)
    i0, i1 = int((n0 - lat1) * 1200), int((n0 - lat0) * 1200); j0, j1 = int((lon0 - w0) * 1200), int((lon1 - w0) * 1200)
    m = m[i0:i1, j0:j1]
    my = 111320 / 1200; mx = my * math.cos(math.radians((lat0 + lat1) / 2))
    return np.maximum(m, 0), mx, my


def measure(h, mx, my):
    land = h > 1
    v = h[land] if land.any() else h.ravel()
    gy, gx = np.gradient(h, my, mx); slope = np.degrees(np.arctan(np.hypot(gx, gy)))[land]
    # ridge spacing: the wavelength holding the most power in the radially averaged spectrum (above 2 km)
    z = h - h.mean(); F = np.abs(np.fft.fftshift(np.fft.fft2(z * np.outer(np.hanning(z.shape[0]), np.hanning(z.shape[1]))))) ** 2
    ky = np.fft.fftshift(np.fft.fftfreq(z.shape[0], my)); kx = np.fft.fftshift(np.fft.fftfreq(z.shape[1], mx))
    K = np.hypot(*np.meshgrid(kx, ky)); wl = np.where(K > 0, 1 / np.maximum(K, 1e-12), np.inf) / 1000
    bins = np.geomspace(2, min(z.shape[0] * my, z.shape[1] * mx) / 2000, 24)
    pw = [F[(wl >= a) & (wl < b)].mean() * ((a + b) / 2) ** -1 if ((wl >= a) & (wl < b)).any() else 0 for a, b in zip(bins, bins[1:])]
    ridge = float(np.sqrt(bins[int(np.argmax(pw))] * bins[int(np.argmax(pw)) + 1]))
    lo, hi = np.percentile(v, 5), np.percentile(v, 95)
    return {'peak': float(v.max()), 'relief': float(hi - lo), 'valley': float(np.median(v[v <= np.percentile(v, 25)])),
            'slope50': float(np.median(slope)), 'slope90': float(np.percentile(slope, 90)), 'ridge_km': ridge,
            'hyps': float((v.mean() - v.min()) / max(1, v.max() - v.min()))}


def hillshade(h, mx, my, path, title):
    from PIL import Image, ImageDraw
    gy, gx = np.gradient(h, my, mx)
    az, alt = math.radians(315), math.radians(40)
    sl = np.arctan(np.hypot(gx, gy)); asp = np.arctan2(-gx, gy)
    sh = np.sin(alt) * np.cos(sl) + np.cos(alt) * np.sin(sl) * np.cos(az - asp)
    t = np.clip(h / max(1, np.percentile(h, 99.5)), 0, 1)
    col = np.stack([90 + 150 * t, 120 + 110 * t, 80 + 150 * t], -1) * np.clip(0.35 + 0.75 * sh, 0, 1.2)[..., None]
    col[h <= 1] = (60, 90, 120)
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    s = 900 / max(im.size); im = im.resize((int(im.size[0] * s), int(im.size[1] * s)))
    d = ImageDraw.Draw(im); d.rectangle([0, 0, im.size[0], 18], fill=(0, 0, 0)); d.text((4, 3), title, fill=(255, 255, 255))
    im.save(path)


if __name__ == '__main__':
    want = sys.argv[1:]
    os.makedirs(SHOTS, exist_ok=True)
    out = {}
    for ours, (name, la0, la1, lo0, lo1, our_h) in ANALOGUES.items():
        if want and not any(w.lower() in ours.lower() for w in want): continue
        h, mx, my = load_box(la0, la1, lo0, lo1)
        m = measure(h, mx, my)
        # the same at one mile per sample, for comparing with our terrain (slopes depend on the sampling)
        f = max(1, round(1609 / my)); fx = max(1, round(1609 / mx))
        hc = h[:h.shape[0] // f * f, :h.shape[1] // fx * fx].reshape(h.shape[0] // f, f, h.shape[1] // fx, fx).mean(axis=(1, 3))
        m1 = measure(hc, mx * fx, my * f)
        out[ours] = dict(analogue=name, ours_m=our_h, **m, slope50_1mi=m1['slope50'], slope90_1mi=m1['slope90'])
        hillshade(h, mx, my, os.path.join(SHOTS, ours.replace("'", '').replace(' ', '-').lower() + '.png'),
                  f'{ours}  <-  {name}  (Copernicus DEM GLO-90)')
        print(f"{ours:26s} <- {name:26s} peak {m['peak']:5.0f} relief {m['relief']:5.0f} valley {m['valley']:5.0f} "
              f"slope {m['slope50']:4.1f}/{m['slope90']:4.1f} (1 mi: {out[ours]['slope50_1mi']:4.1f}/{out[ours]['slope90_1mi']:4.1f}) ridge {m['ridge_km']:5.1f} km hyps {m['hyps']:.2f}", flush=True)
    json.dump(out, open(os.path.join(SHOTS, 'measurements.json'), 'w'), indent=1)
