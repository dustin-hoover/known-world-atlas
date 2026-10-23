"""The colour of each region's ground, taken from its Earth analogue in NASA's Blue Marble (public domain).

For each region we sample the analogue's land in Blue Marble Next Generation (July 2004, 5400 x 2700, no clouds)
and keep the median colour. author.py lays each colour over its region (COLOUR_ZONES) and the terrain grades its
own ground toward it (gen.js), so the North reads like the Scottish moors and Dorne like the Anti-Atlas.

  python3 tools/known/colours.py      # writes tools/known/colours.json and tools/shots/colours.png
Needs tools/refs/earth/bluemarble-july.jpg:
  https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74092/world.200407.3x5400x2700.jpg
"""
import os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, 'tools', 'refs', 'earth', 'bluemarble-july.jpg')

# region (as named in REALMS, or an ARID area): (analogue, lat0, lat1, lon0, lon1)
ANALOGUES = {
    'Beyond the Wall': ('Lapland taiga', 66.5, 68.5, 21, 28),
    'The North': ('the Scottish Highlands and moors', 56.3, 57.6, -5.2, -3.0),
    'The Iron Islands': ('Lewis and Harris: peat, rock and wind, no trees', 57.8, 58.4, -7.1, -6.2),
    'The Vale': ('the Swiss Alps and pre-Alps', 46.3, 47.2, 7.0, 9.5),
    'The Riverlands': ('the Po valley', 44.8, 45.5, 8.8, 11.5),
    'The Westerlands': ('Asturias and León', 42.6, 43.3, -6.8, -5.0),
    'The Crownlands': ('Lazio', 41.6, 42.4, 11.9, 13.2),
    'The Reach': ('the Normandy bocage: fields and orchards, green all summer', 48.7, 49.2, -1.0, 0.5),
    'The Stormlands': ('Cantabria and the Basque coast', 43.0, 43.4, -4.0, -2.0),
    'Dorne': ('the Anti-Atlas and the Draa', 29.0, 30.8, -8.5, -5.5),
    'The Dornish sands': ('the Rub\' al Khali', 19.5, 21.5, 48.0, 52.0),
    'Braavos': ('the Dutch coast', 52.2, 53.2, 4.6, 6.0),
    'Pentos': ('Tuscany', 43.0, 43.8, 10.8, 12.0),
    'Norvos': ('the Bavarian foothills', 47.6, 48.2, 10.5, 12.5),
    'Qohor': ('the Carpathian forests', 48.0, 49.0, 22.5, 24.5),
    'Myr': ('Apulia', 40.6, 41.4, 16.0, 17.5),
    'Volantis': ('the Nile delta', 30.6, 31.3, 30.4, 31.6),
    'The Dothraki Sea': ('the Flint Hills tallgrass prairie: tall green grass', 38.0, 39.0, -97.0, -96.0),
    "Slaver's Bay": ('Mesopotamia', 32.0, 33.5, 44.0, 46.0),
    'The Red Waste': ('the Nafud', 27.5, 28.8, 39.5, 42.0),
    'Lhazar': ('the Zagros foothills', 34.0, 35.0, 45.5, 46.6),
    'Qarth': ('the Hadhramaut', 15.0, 16.0, 48.0, 50.0),
    'Yi Ti': ('the Yangtze plain', 30.0, 31.0, 111.0, 115.0),
}


def sample(img, lat0, lat1, lon0, lon1):
    H, W, _ = img.shape
    i0, i1 = int((90 - lat1) / 180 * H), int((90 - lat0) / 180 * H)
    j0, j1 = int((lon0 + 180) / 360 * W), int((lon1 + 180) / 360 * W)
    px = img[i0:i1 + 1, j0:j1 + 1].reshape(-1, 3).astype(float)
    water = (px[:, 2] > px[:, 0] + 12) & (px[:, 2] > px[:, 1] - 5) & (px.sum(axis=1) < 300)
    land = px[~water]
    return [int(v) for v in np.median(land if len(land) else px, axis=0)]


if __name__ == '__main__':
    from PIL import Image, ImageDraw
    img = np.array(Image.open(SRC).convert('RGB'))
    out = {k: {'analogue': a, 'rgb': sample(img, *box)} for k, (a, *box) in ANALOGUES.items()}
    json.dump(out, open(os.path.join(HERE, 'colours.json'), 'w'), indent=1)
    sw = Image.new('RGB', (520, 26 * len(out)), (20, 22, 26)); d = ImageDraw.Draw(sw)
    for i, (k, v) in enumerate(out.items()):
        d.rectangle([4, 4 + 26 * i, 60, 24 + 26 * i], fill=tuple(v['rgb'])); d.text((70, 8 + 26 * i), f"{k}  <-  {v['analogue']}  {v['rgb']}", fill=(230, 230, 230))
    os.makedirs(os.path.join(ROOT, 'tools', 'shots'), exist_ok=True)
    sw.save(os.path.join(ROOT, 'tools', 'shots', 'colours.png'))
    for k, v in out.items(): print(f"{k:22s} {v['rgb']}  {v['analogue']}")
