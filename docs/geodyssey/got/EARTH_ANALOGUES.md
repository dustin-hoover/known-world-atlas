# Earth analogues for the Known World

Every physical feature of our map gets a real place on Earth to learn from: a match in latitude (on our globe,
latitude = 58° + Y / 69.05 miles), in height and in character. We sample the real place's open elevation and
imagery data and use what we learn (heights, ridge spacing, valley depth, slopes, colours, river patterns) to
shape our own terrain. Nothing is copied from any map of Westeros. Where a book says something, the book wins.

Open data only (Google Maps' imagery and terrain may not be copied or sampled):
- **Elevation:** Copernicus DEM GLO-90 (© DLR and © Airbus, provided under COPERNICUS by the EU and ESA; free for
  any use with this credit), with NASA SRTM (public domain) as a fallback.
- **Coastlines:** Natural Earth 1:10m (public domain), used for the coast of Westeros itself (see `tools/known/donor.py`).
- **Imagery for colours:** NASA Blue Marble (public domain).
- **Rivers:** HydroSHEDS / HydroRIVERS (free with credit), for river patterns and sinuosity.

`tools/refs/analogues.py` downloads each analogue's elevation tiles into `tools/refs/earth/dem/` (git-ignored) and
writes `tools/shots/analogues/*.png` (a hillshade of each, drawn at the same scale as our feature) and a table
of measurements.

## Mountains and hills

| Our feature | Our latitude | Our height | Analogue | Why | Sample box (lat, lon) |
|---|---|---|---|---|---|
| The Frostfangs | 66–72° N | 3,000 m | Brooks Range, Alaska | glaciated range at 68° N, sharp peaks over broad valleys | 67.5–68.5, −151 to −148 |
| Mountains of the Moon | 45–49° N | 3,400 m | Bernese Alps, Switzerland | high, deeply glaciated, sheer valleys like the Vale's | 46–47, 7–9 |
| The Giant's Lance | 47° N | 4,300 m | the Matterhorn and Monte Rosa | a lone horn towering over the range | 45.8–46.1, 7.5–8 |
| The Red Mountains | 25–28° N | 3,000 m | Hajar Mountains, Oman | red, dry, folded, about 3,000 m at 23° N | 22.8–23.6, 56.8–58.2 |
| The Dornish Marches | 28° N | 500 m | Anti-Atlas foothills, Morocco | dry broken hills below a red range | 29.5–30.3, −8.8 to −7.2 |
| The Bones | 28–45° N | 3,600 m | Sierra Nevada, California | a long north–south wall, wet grassland on one side, desert on the other | 36–39, −120 to −118 |
| Mountains of the Shadow | 21–25° N | 4,200 m | Yemen Highlands (Haraz) | dark basalt highlands rising from a hot coast | 14.8–15.8, 43.3–44.5 |
| The Velvet Hills | 43–48° N | 900 m | the Chianti hills, Tuscany | soft, rounded, green hills along a great river | 43.3–43.8, 11–11.7 |
| The Westerlands hills | 42–45° N | 900 m | Asturias and León, Spain | rugged gold-bearing hills by the sea (the Romans mined gold at Las Médulas) | 42.3–43.5, −7 to −5.5 |
| The Barrowlands | 54–55° N | 260 m | the Yorkshire Wolds | low rolling chalk downs with ancient barrows | 53.9–54.2, −0.9 to −0.2 |

## Volcanoes and lone peaks

| Our feature | Our latitude | Our height | Analogue | Why | Sample box |
|---|---|---|---|---|---|
| Dragonmont | 41° N | 1,100 m | Stromboli | an island volcano that smokes, about 1,000 m | 38.7–38.9, 15.1–15.3 |
| The Fourteen Flames | 21° N | 2,600 m | Tibesti volcanoes, Chad | a field of huge volcanoes at 21° N | 19.5–21.5, 17–19 |
| The Mother of Mountains | 44° N | 1,500 m | Ulytau, Kazakhstan | a lone mountain rising from the steppe | 48.4–48.9, 66.5–67.3 |

## Rivers and lakes

| Our feature | Our latitude | Analogue | Why |
|---|---|---|---|
| The Milkwater | 66–72° N | the Torne (Jökulsá á Fjöllum for colour) | a cold river running out of the fells to the sea |
| The Last River | 62–64° N | the Dalälven, Sweden | a cold northern river through forest to the sea |
| The White Knife | 54–57° N | the Severn | a long river to a great estuary; its mouth on our map is the Thames |
| The Trident and its forks | 44–50° N | the lower Po; the Ticino (Green Fork), the Mincio (Blue Fork), the Drava (Red Fork) | three rivers joining in a broad fertile plain |
| The Blackwater Rush | 39–42° N | the Tagus to Lisbon | a river reaching a great harbour city at its mouth |
| The Mander | 33–37° N | the Guadalquivir | a long river through the richest farmland |
| The Honeywine | 27–30° N | the Sebou, Morocco | a short river reaching the sea past an old city |
| The Torrentine | 23–26° N | the Moulouya, Morocco | a mountain river crossing dry country to the sea |
| The Greenblood | 23–25° N | the Nile in Upper Egypt | a green ribbon of life through desert |
| The Rhoyne | 26–49° N | the Danube | a great river with gorges, ruined cities and a delta |
| The Skahazadhan | 30–34° N | the Tigris | a river of ancient cities on a hot plain |
| The Gods Eye | 43–44° N | Lake Constance | a large lake with an island (the Isle of Faces) |
| The Long Lake | 61° N | Loch Ness | long, narrow and deep in a glen |

## Forests, marshes, deserts and ice

| Our feature | Our latitude | Analogue | Why |
|---|---|---|---|
| The Haunted Forest | 65–71° N | the Lapland taiga | dark conifer forest thinning toward the tundra |
| The Wolfswood | 56–59° N | the Caledonian pinewoods | old pine and birch forest by a rocky coast |
| The Kingswood | 36–38° N | the Sila forest, Calabria | old forest near a capital, oak and pine |
| The Rainwood | 32–34° N | Yakushima, Japan | rain forest at 30° N, ever wet from the sea |
| The Forest of Qohor | 41–45° N | the Dinaric forests | deep beech and fir forest on limestone hills |
| The jungles of Sothoryos | 6° S–11° N | the Darién Gap | roadless tropical rain forest and swamp |
| The Neck | 50–52° N | the Fens and the Somerset Levels | flat, wet, reedy fenland between two seas |
| The Dornish sands | 22–26° N | the Rub' al Khali | sand sea and red dunes |
| The Red Waste | 24–35° N | the Nafud, Arabia | red sand desert |
| Lhazar | 30–35° N | the Zagros foothills | dry grassy hills of herders |
| The Land of Always Winter | 74–78° N | north-east Greenland | ice cap, ice-choked fjords |

## Coasts and islands

| Our coast | Analogue | Why |
|---|---|---|
| Beyond the Wall, the Frozen Shore | the Scottish sea lochs (our donor coast), Lofoten | fjords and skerries |
| The Stony Shore | Wales and Connemara (the Rills and Cape Kraken from Connemara) | stony headlands and coves |
| The Iron Islands | Orkney (our donor islands) | bare, windswept, low cliffs |
| The Fingers | the Kerry peninsulas | long bony fingers into the sea |
| The Reach's coast | the Landes and Arcachon, France | long sand beaches, dunes and lagoons |
| The Neck's shores | the Wadden Sea | mudflats and tidal channels |
| Dorne's coast | the Libyan and Sinai coasts | hot sand shores and low cliffs |
| The Stepstones | the Dodecanese | rocky island chain between two lands |
| The Summer Isles | the Lesser Antilles | green volcanic islands at 15° N |
| The Basilisk Isles | the Bahamas | low tropical islands and reefs |
| Valyria | Santorini's caldera | a drowned volcanic land |

## The shores of Essos and Sothoryos

`tools/known/shores.py` lays a real coast along each stretch of our own outline (the outline stays ours, from the
books and named places' positions; the real coast gives the bays, spits, deltas, lagoons and the islands just
offshore, at about their real size), and moves a few real islands and one peninsula bodily.

| Our coast | Real shore laid along it | Why |
|---|---|---|
| Braavos and the north-west corner | the Venetian lagoons and Istria | a city of a hundred islands in a lagoon; Braavos stands where Venice falls |
| Braavos to Pentos | the Costa Brava and the Camargue | rocky coves, then a delta plain; Pentos takes Marseille's place, an old trading port |
| Pentos to Myr | Apulia and the Gargano | a long warm shore with one great headland |
| Myr to the Orange Shore | the Valencian coast (the Orange Blossom Coast) | lagoons, deltas and orange groves |
| Volantis and the mouths of the Rhoyne | the Nile delta | a great river's delta and lagoons at a city of many peoples |
| facing Valyria | the north shore of the Gulf of Corinth | the other side of the gulf from the Peloponnese |
| the Gulf of Grief to Astapor | the Aegean coast of Anatolia | the ragged coast of an old empire, many islands |
| Slaver's Bay | the head of the Persian Gulf | a hot, shallow gulf with a great river at its head (Meereen, the Skahazadhan) |
| Qarth's coast | the Gulf of Aden | a dry coast near a famous strait |
| the shore of the Red Waste | the coast of Oman | desert meeting the sea |
| Asshai | the Pearl River and the Guangdong coast | a city at a river's mouth at the end of the world |
| Yi Ti and the Jade Sea | the coasts of Fujian and Zhejiang | drowned river valleys and a thousand islands |
| the far north-east | the Primorye coast | a cold, steep, straight shore |
| the Grey Waste | the Pechora Sea | low tundra coast, lagoons and a delta |
| the Shivering Sea | the Black Sea coast of Anatolia | a long north-facing shore with deltas and one great headland |
| facing Ib | the south shore of the Baltic | spits, lagoons and dunes |
| Lorath's bay | the north coast of Estonia | low cliffs and bays |
| Sothoryos, west | Guinea and the Bijagós | mangrove coast and an archipelago |
| Sothoryos, south | the Gulf of Guinea and the Niger delta | rain forest to the sea, a vast delta |
| Sothoryos, east | the Swahili coast | coral islands and creeks |
| Sothoryos, north (Naath's shore) | the north coast of New Guinea | jungle mountains to the sea |
| Sothoryos, north-west (the Basilisk shore) | the Caribbean coast of Colombia and Panama | the Darién's coast and the San Blas islands |

The North keeps Britain (`tools/known/donor.py`), stretched to several times its size in places, and the Lands of
Always Winter are drawn by us, so the coast there had straight edges miles long. `shores.py` lays real detail on every
edge longer than 7 miles, its corners held, and lays the Lands of Always Winter whole. South of the North the coast
runs between named anchors (`tools/known/coast_fixed.py`, positions only), and each stretch between two anchors is
a whole real coastline of its character, turned and scaled to run from one to the other (`tools/known/south.py`; the
pools below, with Galicia and Maine for rocky shores, Donegal and Mayo for stony ones, the Louisiana marshes beside
the Wadden Sea, western Portugal and the Spanish Levant for beaches, and Cyrenaica, Algeria, the Gulf of California
and Morocco's Atlantic coast for Dorne). Each stretch's choice is written to the ledger (`src/sources.js` SHORES) and
is illustrative only:

| Our coast | Real detail from | Why |
|---|---|---|
| the Lands of Always Winter, beyond the Wall | northern Labrador | ice-worn fjords and skerries at the edge of the ice |
| the Rills, the Stony Shore, Cape Kraken, the Flint Cliffs | Connemara | stony headlands, coves and islets |
| Blazewater Bay's head, the Neck, the Bite, the Bay of Crabs | the Wadden Sea | mudflats, creeks and barrier islands |
| the westerlands, the stormlands, the Vale, Massey's Hook | Brittany | granite headlands, rias and islets |
| the Reach, Blackwater Bay | the Gulf of Cádiz and the Algarve | sand, lagoons and low cliffs |
| Dorne, the Sea of Dorne's south shore | Tripolitania and the Gulf of Gabès | hot shores, lagoons and sebkhas |
| the Fingers | the Kerry peninsulas | long bony fingers into the sea |

| Moved bodily | From | Why |
|---|---|---|
| Valyria (the peninsula) | the Peloponnese | a peninsula on a narrow isthmus, broken into fingers |
| the isles of the Smoking Sea | the Cyclades | Valyria's ruins on Santorini's drowned caldera, the Fourteen Flames on Naxos |
| Ib | Iceland | a large cold island across a northern sea (Ib Nefer where Reykjavík is) |
| Tyrosh, Lys, Bloodstone | Brač, Hvar, Vis | the Dalmatian islands' size and shape |
| the Stepstones | the Kornati | a scatter of small bare islands |
| the Iron Islands | Orkney (by donor.py), centred on the group's position (graded `map`) | bare, windswept, low cliffs |
| Dragonstone, Driftmark, Claw Isle | La Palma, Oléron, Guernsey | a volcanic isle by a long low one; a small rocky one off a cape |
| Tarth, Estermont | Rhodes, Ibiza | large green islands off a stormy coast |
| Fair Isle, the Shield Islands | Jersey, the Îles d'Hyères | a single isle in a sound; a short chain across a river's bay |
| the Arbor, the Three Sisters | Mallorca, the Frisian islands | a wine island across a strait; a low chain in a shallow bight |

Each island group sits on its position (graded `map`; `tools/known/shores.py` TRANSPLANTS), and its castles and towns
stand on the real island's own towns and harbours (TRANSPLANT_PINS: High Tide on Oléron, Faircastle on St Helier,
Ryamsport on Palma, the three Shields on Porquerolles, Port-Cros and Le Levant...).

None of them is set down as the real place: `shores.py` `disguise()` mirrors each one across a line through its
anchor, draws it a little longer and narrower along that line and warps it gently (a smooth field seeded by the
island's name, which never folds). The line is chosen to move its pinned towns least, and the whole is then turned and
scaled (by at most a tenth) so the towns come back to their marks; Valyria's neck is held to the mainland the same
way. They keep a real coast's character without reading as the Peloponnese, Iceland or Mallorca.
`python3 tools/known/shores.py --east --write` rebuilds the east and the transplants with Westeros's coast kept, then
fills any false inlet rule 9b would find on the gate's own grids.

## How the samples are used

1. **Heights and shape:** each range's real profile (crest height, valley floors, how steep its sides are,
   and how far apart its ridges run) sets the parameters of our ridge noise for that range.
2. **Terrain from the real thing:** later, a range can take its relief straight from its analogue's elevation,
   bent onto our range's line the way the coast is bent onto our landmarks (the same open data, credited).
3. **Colours (done):** `tools/known/colours.py` samples each region's analogue in Blue Marble (July) and writes
   `tools/known/colours.json`; each realm, and each desert, grades our ground toward its analogue's colour
   relative to the average of all regions (so Dorne reads like the Anti-Atlas, the North like the Scottish moors).
4. **Rivers (done for the courses):** `tools/known/shores.py` lays each analogue's centreline (Natural Earth) along
   our river, so the Rhoyne bends like the Danube and the Mander like the Guadalquivir; bends larger than a
   river's own scale (8–30 miles) stay ours. Towns that stood on a river move onto its new course.
