# Reference sources

The images and data files these entries describe live in `tools/refs/` on the working computer only. They are
git-ignored and never published (LAWS I.2, I.6). This file records what each one is and how we may use it.

Grades in the ledger: `text` (stated in the books), `map` (read from an official map), `inferred` (ours).

| Folder | Source | Kind | May be used for | Never used for |
|---|---|---|---|---|
| (none) | The five novels, The World of Ice & Fire, Fire & Blood | canon | names, positions stated in words, distances, travel times, heraldry, who held what and when | quoting prose |
| `official/` | Jonathan Roberts, The Lands of Ice and Fire (2012), previews from fantasticmaps.com | official, © George R. R. Martin | broad layout and the positions of large features, graded `map`: the ~45 places and island groups southern Westeros was fitted to, and the coast's fixed points (`tools/known/coast_fixed.py`) | tracing any line; the previews (720 × 1080) are too small to read most castle names |
| (owner's copy) | The Lands of Ice and Fire, the printed poster set | official | positions of named places, graded `map`, read from the owner's own photos of the sheets | tracing any line |
| `whitehead/` | Adam Whitehead, Atlas of Ice and Fire: the Known World (2014, 10000 × 8300; also the 2016 world maps) | fan, built from the official maps | flags only: places we lack, coast or inland disagreements, missing islands, places far from where it puts them | positions, shapes or names (a name is added only when found in the books) |
| `quartermaester/` | quartermaester.info place and seat data | fan, mixes book and TV data | flags only, and leads to chapters | positions, shapes, seat holders, or anything from its TV layer |
| (online) | A Wiki of Ice and Fire | fan wiki, CC BY-SA | leads: which chapter names a place, a house or a holder | text, images or sigil art |

## Real-world data (open; may be built into the map)

| Folder | Source | Licence | Used for |
|---|---|---|---|
| `earth/` | Natural Earth 1:10m land and minor islands | public domain | the North's coast: Britain bent onto our landmarks, Orkney moved in as the Iron Islands (`tools/known/donor.py`, output `tools/known/coast_donor.json`); the detail of the south's coast between its fixed points, and Westeros's other islands (`tools/known/shores.py`) |
| `earth/` | Natural Earth 1:10m land and minor islands | public domain | Essos's and Sothoryos's coasts: real shores laid along our own outline, and real islands moved bodily (`tools/known/shores.py`, output `tools/known/coast_shores.json`) |
| `earth/` | Natural Earth 1:10m rivers and lake centrelines | public domain | the bends of our rivers, each from its Earth analogue (`tools/known/shores.py`) |
| `earth/dem/` | Copernicus DEM GLO-90 | free for any use; credit "© DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA" | measuring the Earth analogues of our mountains (`tools/refs/analogues.py`, `docs/otherworldly/got/EARTH_ANALOGUES.md`) |

Google Maps and Google Earth imagery and terrain are not used: their terms forbid copying or sampling them.

Not used at all: HBO's maps and title sequence, the games, merchandise, and full-resolution scans of the
official maps posted without the publisher's permission.

## Using the comparison tool

`python3 tools/refs/compare.py` lines each reference up with our map by the places both name, and writes
`tools/refs/reports/*.md` (git-ignored) listing what disagrees. It writes reports, never geometry. It needs
Tesseract for reading map labels (`apt-get install tesseract-ocr`, `pip install pytesseract scikit-image scipy`).

`python3 tools/refs/notrace.py` is the no-tracing check for the coast of southern Westeros (MAP_V2 §3): it lines the
official preview up with our map by shared places and reports any stretch between two fixed points whose shore runs
too close to the official line. It reads the preview and writes nothing.
