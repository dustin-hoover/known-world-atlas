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
- **Places:** 121 castles, cities and sites, each in the source ledger (`src/sources.js`, audited by `npm run audit`)
- **Time:** years After the Conquest counted in moons; seasons that last years (the long summer ends
  as the story opens, winter comes later); story events with estimated dates
- **Seasons on the ground:** the land itself changes with the books' long seasons. Beyond the Wall it turns to
  tundra and then ice the farther north you go; as the summer ends the forests brown, snow creeps south over the
  North and the Wall, and by the winter of 300 AC it lies over the whole North
- **The cast:** some seventy characters (principal, secondary, companions and the dark and mysterious, from the
  Others and Coldhands to Melisandre, Quaithe and the three-eyed crow), each a pixel figure drawn from the books'
  descriptions, with all six Stark direwolves and Daenerys's three dragons
- **Journeys** for every one of them from A Game of Thrones through A Dance with Dragons, along the roads and
  sea lanes, on foot, on horseback, in the queen's wheelhouse, by ship, by river boat and on dragonback
- **Realms that follow the land:** each kingdom's border is fitted to our own coasts (exactly, at the sea), and
  inland settles on the mountain ranges, the Wall and the rivers between realms (`tools/known/realms.py`)
- **Lords and monarchs:** every kingdom's Lord Paramount and its king (and any rival crown) on each date, in the
  place cards and the Characters panel, with the lords themselves among the cast
- **Deaths and battles:** the dead lie where they fell for a time under a death mark (at the Red Wedding the bodies
  are everywhere); a dozen battles from the Green Fork to the battle beneath the Wall, with house banners
- **Characters panel:** a profile for each, the road they took, and everyone they crossed paths with
- **Castles as described** in the ground view: Winterfell, Castle Black, the Eyrie, Harrenhal, the Twins, the
  Red Keep, Storm's End, Dragonstone, Pyke, the Hightower, Riverrun, Casterly Rock and Sunspear
- **Weather, ground view and sound** from the Arda engine

## Run it

```bash
npm install
npm run dev          # builds, then serves http://localhost:8765/dist/preview.html
npm run author       # regenerate src/geo.js and src/sources.js from tools/known/author.py, then build
npm run audit        # check the map against the source ledger (writes docs/SOURCES.md)
```

## Status
Phases 1–3 of [docs/otherworldly/got/PLAN.md](docs/otherworldly/got/PLAN.md): frame, calendar, geography,
places, realms, seasons, the cast and their journeys, castles. Next: battles (Phase 4). The cast, its journeys and
travel modes are authored in `tools/known/cast.py`; every date there is an estimate and the app says so.

An unofficial fan project, not endorsed by the author or publishers. Places, people and events are from
George R. R. Martin's A Song of Ice and Fire.
