# The Known World

An unofficial, Google Earth–style globe of the lands of A Song of Ice and Fire (Westeros, Essos and
Sothoryos) that looks like a real planet from orbit. Terrain, imagery, fields, forests, rooftops and
weather are generated procedurally in the browser from hand-authored geography.

The second world of the Other Worldly Project, built on the engine of
[Arda Atlas](https://github.com/dustin-hoover/arda-atlas) and following its laws
([docs/otherworldly/LAWS.md](docs/otherworldly/LAWS.md)): facts from the novels in our own words, no copied
maps or artwork, no material from screen adaptations.

- **Globe:** MapLibre GL JS with 3D terrain, labels, three basemaps
- **Geography:** our own generalised drawing of three continents: coasts, ranges, rivers, the Gods Eye,
  forests, the Neck, the Dornish sands, the Dothraki grasslands, the Red Waste, the smoking ruins of
  Valyria, and the Wall (some 300 miles of ice, about 700 feet high)
- **Places:** 107 castles, cities and sites, each in the source ledger (`src/sources.js`, audited by `npm run audit`)
- **Time:** years After the Conquest counted in moons; seasons that last years (the long summer ends
  as the story opens, winter comes later); story events with estimated dates
- **Weather, ground view and sound** from the Arda engine

## Run it

```bash
npm install
npm run dev          # builds, then serves http://localhost:8765/dist/preview.html
npm run author       # regenerate src/geo.js and src/sources.js from tools/known/author.py, then build
npm run audit        # check the map against the source ledger (writes docs/SOURCES.md)
```

## Status
Phase 1–2 of [docs/otherworldly/got/PLAN.md](docs/otherworldly/got/PLAN.md): frame, calendar, geography,
places, realms. Next: journeys and the cast (Phase 3), battles and landmarks (Phase 4).

An unofficial fan project, not endorsed by the author or publishers. Places, people and events are from
George R. R. Martin's A Song of Ice and Fire.
