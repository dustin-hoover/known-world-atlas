# The Known World: handoff

Where the work stands, for a new chat picking it up. Read this, then `CLAUDE.md` (engine notes and conventions) and
`docs/otherworldly/LAWS.md` (the rules every world follows).

## The project

- **The Known World** (this repo, `dustin-hoover/known-world-atlas`): an unofficial globe of A Song of Ice and Fire,
  books only, built on the Arda Atlas engine. Live at https://dustin-hoover.github.io/known-world-atlas/
- It is the second world of the **Otherworldly** project. The first, **Arda Atlas** (`dustin-hoover/arda-atlas`,
  https://dustin-hoover.github.io/arda-atlas/), is worked on in a separate chat. Keep the two repos separate; the
  owner wants the Arda link kept "pure".
- Future, not now: a merged Otherworldly site under its own name (not the owner's), funded by ads, with a message
  board and feedback. The visit counter below is its first piece.

## How the owner works

- Changes go to the work branch first; the owner reviews screenshots, then says "merge" before anything goes to
  `main` (which publishes the site through GitHub Pages).
- Show screenshots of every visible change (`tools/app_test.py`, see `CLAUDE.md`).
- Dates the books don't give are estimates and the app says "(date est.)". Staged or inferred things (routes the
  books don't describe, the Wall drawn taller at a distance) are labelled as ours.
- The laws: facts from the novels in our own words; no traced map line-work (published fan maps such as the Atlas
  of Ice and Fire blog are built from the copyrighted official maps, so they are not used); no screen adaptations.

## What is built (all merged to `main`)

- Geography of Westeros, Essos and Sothoryos; 121 places; realm borders fitted to the coasts, ranges, rivers and
  the Wall (`tools/known/realms.py`); peoples layer.
- The books' long seasons on the ground: tundra and ice beyond the Wall in any season, snow spreading south as
  winter comes.
- The Wall: a bold icy band on the map, a 700-ft wall of ice looming on the horizon in the ground view, running sea
  to sea (its ends snap to the shore on every build; 284 mi).
- About seventy characters with profiles (Characters panel), the six direwolves and three dragons, the Lords
  Paramount and monarchs of each kingdom by date, journeys AGOT-ADWD with travel modes (horse, wheelhouse, ship,
  river boat, dragon), deaths (body under a death mark, the Red Wedding littered with the dead), twelve battles with
  house banners, Drogo's khalasar.
- Castles in the ground view: Winterfell, Castle Black, the Eyrie, Harrenhal, the Twins, the Red Keep, Storm's End,
  Dragonstone, Pyke, the Hightower, Riverrun, Casterly Rock, Sunspear.
- Playback speeds 1 h, 6 h, 12 h, 1 day, 4 days per second.
- Visit counter: GoatCounter account `otherworldly` (https://otherworldly.goatcounter.com), on both atlases. The
  owner leaves their own visits out with `#toggle-goatcounter` on each device; they had not yet tested it.

## Ideas raised but not started

- More detail drawn from the books (more castles, villages, finer coasts and rivers), within the laws.
- Arda now has a final resting place after each death (tombs, pyres, mounds); the Known World only has the body
  lying under a death mark. The owner may want the same here.
- Journeys are not yet routed over the terrain (`src/routes.js` is empty, so they follow straight legs between waypoints and roads).

## Working setup

- Branch for work: `ccr-30078a2c-wtppal` (or whatever branch the new session is given); merge to `main` on approval.
- `npm run author` regenerates `src/geo.js` from `tools/known/author.py` and `tools/known/cast.py`, then builds.
- `npm run audit` checks the map against the source ledger; `npm run check` is the syntax check CI runs.
