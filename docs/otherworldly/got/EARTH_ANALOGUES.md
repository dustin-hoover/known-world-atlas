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
| The Milkwater | 66–72° N | Jökulsá á Fjöllum, Iceland | glacial meltwater river, milky with silt |
| The Last River | 62–64° N | Ångermanälven, Sweden | a cold northern river through forest to the sea |
| The White Knife | 54–57° N | the Spey, Scotland | a fast, clear river; its mouth on our map is the Thames |
| The Trident and its forks | 44–50° N | the Po and its Alpine tributaries | three rivers joining in a broad fertile plain |
| The Blackwater Rush | 39–42° N | the Tagus to Lisbon | a river reaching a great harbour city at its mouth |
| The Mander | 33–37° N | the Guadalquivir | a long river through the richest farmland |
| The Honeywine | 27–30° N | the Sebou, Morocco | a short river reaching the sea past an old city |
| The Torrentine | 23–26° N | the Draa, Morocco | a mountain torrent running dry toward the sea |
| The Greenblood | 23–25° N | the Nile in Upper Egypt | a green ribbon of life through desert |
| The Rhoyne | 26–49° N | the Danube | a great river with gorges, ruined cities and a delta |
| The Skahazadhan | 30–34° N | the Tigris and Euphrates | a river of ancient cities on a hot plain |
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
| The Stony Shore | Wales and Connemara | stony headlands and coves |
| The Iron Islands | Orkney (our donor islands) | bare, windswept, low cliffs |
| The Fingers | the Kerry peninsulas (our donor coast) | long bony fingers into the sea |
| The Reach's coast | the Landes and Arcachon, France | long sand beaches, dunes and lagoons |
| The Neck's shores | the Wadden Sea | mudflats and tidal channels |
| Dorne's coast | the Libyan and Sinai coasts | hot sand shores and low cliffs |
| The Stepstones | the Dodecanese | rocky island chain between two lands |
| The Summer Isles | the Lesser Antilles | green volcanic islands at 15° N |
| The Basilisk Isles | the Bahamas | low tropical islands and reefs |
| Valyria | Santorini's caldera | a drowned volcanic land |

## How the samples are used

1. **Heights and shape:** each range's real profile (crest height, valley floors, how steep its sides are,
   and how far apart its ridges run) sets the parameters of our ridge noise for that range.
2. **Terrain from the real thing:** later, a range can take its relief straight from its analogue's elevation,
   bent onto our range's line the way the coast is bent onto our landmarks (the same open data, credited).
3. **Colours:** Blue Marble's colours for each analogue set the palette of the ground in each region.
4. **Rivers:** the real river's sinuosity and how its tributaries branch set how ours wind and divide.
