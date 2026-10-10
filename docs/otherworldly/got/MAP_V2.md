# The Known World, version 2: plan

The goal is a map of our own, as rich as the best fan atlases, that follows the books. Where the books are
silent we take our own liberties, as other mapmakers have. Every coast should be tight. Every house that
held a seat has its banner, from the Conquest to the end of the novels.

Decisions already made by the owner:
- **Places:** every town, castle, holdfast, ruin and city named in the books (the five novels, The World of
  Ice & Fire, Fire & Blood). A name found only on a map and never in the books is left out.
- **Houses:** all of history now, not only the novels' years.
- **Positions the books don't give:** read from the official maps on this computer only, graded `map` in
  the ledger (LAWS I.2). Fan maps only flag problems (LAWS I.6).
- **Workflow:** this plan is approved first; then each phase goes to the work branch with screenshots, and
  merges on "merge".

## 1. Sources

All reference images stay out of git (a new ignored folder, `tools/refs/`). Each source gets one line in
`tools/refs/SOURCES.md` (in git: what it is and how we may use it, never the image itself).

| Source | Kind | Use |
|---|---|---|
| The five novels, The World of Ice & Fire, Fire & Blood | canon | names, distances, directions, travel times, heraldry, who held what and when |
| The maps printed in the novels | official | positions of named places, graded `map` |
| The Lands of Ice and Fire (Jonathan Roberts, 2012) | official | positions of named places, graded `map` |
| The maps in The World of Ice & Fire and Fire & Blood | official | positions, and old borders and kingdoms through time |
| The Atlas of Ice and Fire (Adam Whitehead) | fan | flags only: missing places, coast or inland disagreements, missing islands |
| Quartermaester and other book-based fan maps | fan | flags only |
| A Wiki of Ice and Fire (awoiaf) | fan wiki | leads only: find the chapter that names a place or house, then cite the chapter |
| HBO, the games, merchandise | adaptation | never used (LAWS I.3) |

A new tool, `tools/refs/compare.py`, lines each reference up with our map using matched places, as was done
for the Whitehead map. It lists what disagrees: place positions, coast or inland, island or mainland,
realm, and names that a map shows but we lack (each one checked against the books before it is added). It
writes a report, never geometry.

## 2. The gazetteer: every named place

- A new data file, `tools/known/gazetteer.py`, replaces the hand list in `author.py`. Each entry gives the name,
  kind (city, town, castle, holdfast, tower, ruin, village, inn, sept, landmark), region, the first book and
  chapter that names it, and where it sits.
- **Where it sits, in order of strength:**
  1. **text:** what the books say (on the coast, at a river mouth, a day's ride from X, across the bay from Y).
  2. **map:** read from the official maps.
  3. **inferred:** our own placement, where neither gives one.
- The text constraints become automatic tests. For example "X is on the coast", "X lies north of Y", or "it
  is N days' ride". `npm run audit` fails if a move breaks one.
- **Expected size:** several hundred places in Westeros and Essos, against 121 today.

## 3. Coastlines: tight, and our own

"Tight" here means three things:
1. **Every coastal place is on the shore,** within about 2 miles. Every inland place is clear of it. This is
   tested automatically; a bug like Saltpans 115 miles inland can't happen again.
2. **Every named coastal feature is where it belongs:** each bay, cape, point, strait, sound, river mouth,
   island and island chain that the books or official maps place. These become fixed points of the coast,
   each with its source.
3. **Much finer detail:** control points every few miles instead of about 30 today, with inlets, headlands
   and small islands. The ground view and the close zoom levels show a believable shore.

Between the fixed points the shore is ours: drawn by our own procedure, not traced. A no-tracing check
compares our coast with each official coast and must find them different in detail between the fixed
points, while agreeing at the points. If the shore matches a reference too closely along a stretch, the
build warns. This keeps us inside LAWS I.2 while the coast stays tight where it matters.

Islands get the same treatment: every named island gets its own outline, and the lesser named ones (the
Three Sisters, the Stepstones, the Iron Islands, the Basilisk Isles and so on) are each drawn.

Order of work: Westeros first (the North, the Vale and the Fingers, the Iron Islands, the Reach coast,
Dorne, the Stormlands, Blackwater Bay), then the Free Cities coast, Slaver's Bay, the Summer Sea and the
far east.

## 4. Data layers

To match the richest fan atlases, each layer is named and sourced:

| Layer | Now | Version 2 |
|---|---|---|
| Places | 121 | every named place in the books (several hundred), with kinds and symbols |
| Coasts and islands | about 30 islands, coarse shores | fine shores, every named island |
| Rivers | 15 or so | every named river and tributary, with mouths on the coast |
| Lakes, marshes, deserts | a few | every named one |
| Mountains and hills | broad ranges | named ranges, passes and peaks |
| Forests | a few | every named wood and forest |
| Roads | main roads | every named road, with fords, bridges and ferries the books mention |
| Realms and regions | 2 sets of borders | realms through time (the Seven Kingdoms before the Conquest, after it, and during the war) |
| Seas, bays, straits, capes | a handful | every named one, labelled |
| Houses and banners | battle banners only | every house that held a seat, its arms and its lords through time |

## 5. Houses, banners and lords

- **Houses** (`tools/known/houses.py`): name, blazon in our own words (from the books' description), words
  where the books give them, region, liege, colours, and a pixel sigil drawn by our generator from the blazon
  (LAWS I.4, never copied from published sigil art).
- **Seats through time:** for each castle, a list of who held it and when. For example, Harrenhal passes
  from Harren to the Qorgyles, the Towers, the Strongs, the Lothstons, the Whents, then Lannister, Bolton
  and Baelish claimants. The years come from The World of Ice & Fire, Fire & Blood and the novels; where a
  year isn't recorded, it is estimated and marked so.
- **Lords and ladies:** each holder is a character with their house. The house's banner and sigil are part
  of the character: on their card, in the Characters panel, and in their sprite (on a tabard or shield).
- **On the map:**
  - zoomed out, one banner per region shows its ruling house at that date;
  - zoomed in, a banner flies at each seat for the house holding it on that date;
  - the banner changes when the seat changes hands, as the clock runs;
  - in the ground view, the castle flies the same banner.
- **Time:** a new History timeline from Aegon's Landing to 300 AC, and earlier where The World of Ice & Fire
  gives the kingdoms' ruling houses. It sits alongside the five novels' timelines.

## 6. Phases

Each phase ends with a build, `npm run check`, `npm run audit`, screenshots of every visible change, and
the owner's "merge".

1. **Sources and comparison tool.** Gather the references locally, write `tools/refs/SOURCES.md` and
   `compare.py`, and produce the first flag reports.
2. **Gazetteer, Westeros.** Every named place, with a source for each, and the text tests.
3. **Coastline, Westeros.** Fixed points, the new fine shore, every island, and the coast tests.
4. **Rivers, roads, mountains, forests, Westeros.** Refit to the new coast and places.
5. **Houses and heraldry.** The houses file, the sigil generator, and the seats through time, for Westeros.
6. **Banners on the map and lords as characters.** Region banners, seat banners swapping in time, and the
   History timeline.
7. **Essos, Sothoryos and the rest.** Phases 2 to 4 again for the east.
8. **Journeys refit.** Every journey re-checked against the new map (the water check from the ship fix runs
   on every build).

## 7. Checks that run on every build

- Coastal places on the shore and inland places off it.
- No traveller on water without a ship, and no ship on land.
- Every place, house and seat has a source.
- The no-tracing check on coasts.
- The existing audit statements (the Wall's length and Westeros's length).

## 8. Open questions for later phases

- How far before the Conquest should the History timeline reach? The World of Ice & Fire names the ruling
  houses of the old kingdoms, but with few dates.
- Essos houses (the Free Cities' magisters, the Old Blood of Volantis) have few seats the books name.
  The plan treats them as cities, not houses, unless the books say otherwise.
- Before anything is sold or sponsored, the lawyer review in the laws still applies to the heraldry and
  the house words.
