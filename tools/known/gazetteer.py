"""The gazetteer: every place of Westeros the books name (MAP_V2 phase 2), beyond the first list in author.py.

Each entry gives the name, its kind, where it sits on our map, its people and realm, the book that first names it,
a note in our own words, and the grade of its position:
  text      the books say where it is (on a river, at a castle's gate, a day's ride from somewhere)
  inferred  our own placement, in keeping with what the books say of the land around it
Positions are given against our own geography, never copied from a published map:
  ('at', X, Y)                  miles, X east and Y north of Winterfell
  ('near', place, bearing, mi)  from a place already on the map (bearing in degrees, or N, NE, E ...)
  ('in', place, dx, dy)         a few miles from a place: a quarter, a tower or a hall in or by it
  ('between', a, b, f)          the fraction f of the way from a to b
  ('river', river, f)           on a river, the fraction f of the way from its source to its mouth
  ('on', river, X, Y)           on a river, at the point of its course nearest (X, Y)
  ('wall', X)                   on the Wall, where it crosses X
`coast=True` puts a place on the waterline (a port, a castle on a sea cliff); `move=True` moves a place already
in author.py instead of adding one. `seat` names the house that holds it in the novels (phase 5 fills in the rest).
"""
import math

BEARING = {'N': 90, 'NNE': 67.5, 'NE': 45, 'ENE': 22.5, 'E': 0, 'ESE': -22.5, 'SE': -45, 'SSE': -67.5, 'S': -90,
           'SSW': -112.5, 'SW': -135, 'WSW': -157.5, 'W': 180, 'WNW': 157.5, 'NW': 135, 'NNW': 112.5}
KIND = {'castle': 'fortress', 'holdfast': 'fortress', 'inn': 'village', 'sept': 'landmark', 'hall': 'landmark', 'temple': 'landmark'}


def G(name, kind, where, people, realm, src, note, rank=5, grade='inferred', **o):
    return {'name': name, 'kind': kind, 'where': where, 'people': people, 'realm': realm, 'src': src, 'note': note,
            'rank': rank, 'grade': grade, **o}


N, R, V, I, W, C, S, H, D = ('north', 'The North'), ('river', 'The Riverlands'), ('vale', 'The Vale'), \
    ('iron', 'The Iron Islands'), ('west', 'The Westerlands'), ('crown', 'The Crownlands'), ('storm', 'The Stormlands'), \
    ('reach', 'The Reach'), ('dorne', 'Dorne')
WATCH = ('watch', 'The Wall')

PLACES = [
    # ------------------------------------------------------------ the Wall: its nineteen castles, west to east
    G('Sentinel Stand', 'ruin', ('wall', -98), *WATCH, 'AFFC', 'An abandoned castle of the Night\'s Watch on the Wall.', rank=6, grade='text'),
    G('Greyguard', 'ruin', ('wall', -86), *WATCH, 'ASOS', 'A castle of the Watch on the Wall, given to the free folk to hold.', rank=6, grade='text'),
    G('Stonedoor', 'ruin', ('wall', -74), *WATCH, 'ASOS', 'A castle of the Watch at a gate through the Wall, given to the free folk.', rank=6, grade='text'),
    G('Hoarfrost Hill', 'ruin', ('wall', -63), *WATCH, 'ADWD', 'An abandoned castle of the Watch on the Wall.', rank=6, grade='text'),
    G('Icemark', 'ruin', ('wall', -52), *WATCH, 'ADWD', 'An abandoned castle of the Watch on the Wall.', rank=6, grade='text'),
    G('Deep Lake', 'ruin', ('wall', -20), *WATCH, 'ADWD', 'A castle of the Watch on the Wall, reopened in the novels.', rank=6, grade='text'),
    G('Queensgate', 'ruin', ('wall', 0), *WATCH, 'ADWD', 'A castle of the Watch on the Wall, named for a queen who visited it.', rank=6, grade='text'),
    G('Oakenshield', 'ruin', ('wall', 38), *WATCH, 'ADWD', 'A castle of the Watch on the Wall, given to the free folk.', rank=6, grade='text'),
    G('Woodswatch-by-the-Pool', 'ruin', ('wall', 55), *WATCH, 'ADWD', 'An abandoned castle of the Watch by a pool below the Wall.', rank=6, grade='text'),
    G('Sable Hall', 'ruin', ('wall', 73), *WATCH, 'ADWD', 'A castle of the Watch on the Wall, given to the free folk.', rank=6, grade='text'),
    G('Rimegate', 'ruin', ('wall', 91), *WATCH, 'ADWD', 'An abandoned castle of the Watch on the Wall.', rank=6, grade='text'),
    G('The Long Barrow', 'ruin', ('wall', 108), *WATCH, 'ADWD', 'A castle of the Watch built against a great barrow, reopened in the novels.', rank=6, grade='text'),
    G('The Torches', 'ruin', ('wall', 126), *WATCH, 'ADWD', 'An abandoned castle of the Watch on the Wall.', rank=6, grade='text'),
    G('Greenguard', 'ruin', ('wall', 143), *WATCH, 'ADWD', 'A castle of the Watch near the Wall\'s eastern end.', rank=6, grade='text'),

    G('The Bridge of Skulls', 'landmark', ('in', 'Westwatch-by-the-Bridge', 5.9, 11.7), *WATCH, 'ACOK', 'The bridge across the Gorge, by Westwatch, west of the Shadow Tower.', grade='text'),

    # ------------------------------------------------------------ the North
    G('Wintertown', 'town', ('in', 'Winterfell', 2.5, -2.5), *N, 'AGOT', 'The town under Winterfell\'s walls, which fills in winter.', grade='text'),
    G('Castle Cerwyn', 'castle', ('near', 'Winterfell', 'ESE', 24), *N, 'ACOK', 'Seat of House Cerwyn, within a day\'s ride of Winterfell.', grade='text', seat='Cerwyn'),
    G('Hornwood', 'castle', ('at', 215, -95), *N, 'ACOK', 'Seat of House Hornwood, between the Dreadfort and the White Knife.', rank=4, seat='Hornwood'),
    G('Oldcastle', 'castle', ('at', 372, -262), *N, 'ADWD', 'Seat of House Locke, on the east coast above White Harbor.', coast=True, seat='Locke'),
    G('Flint\'s Finger', 'castle', ('at', -348, -313), *N, 'TWOIAF', 'Seat of a branch of House Flint, on a finger of land on the west coast.', coast=True, seat='Flint'),
    G('The Wolf\'s Den', 'hall', ('in', 'White Harbor', 1.0, 0.6), *N, 'ADWD', 'The old stronghold of White Harbor, older than the city around it.', grade='text'),
    G('The New Castle', 'hall', ('in', 'White Harbor', -0.6, 1.1), *N, 'ADWD', 'The Manderlys\' castle on the hill above White Harbor.', grade='text'),
    G('The Sept of the Snows', 'sept', ('in', 'White Harbor', 0.4, -0.7), *N, 'ADWD', 'The great sept of White Harbor.', grade='text'),
    G('The Great Barrow', 'landmark', ('in', 'Barrowton', 1.6, 0.6), *N, 'ADWD', 'The vast barrow of the First King beside Barrowton.', grade='text'),
    G('The Gatehouse Tower', 'tower', ('in', 'Moat Cailin', 0.0, -0.9), *N, 'ACOK', 'One of the three towers still standing at Moat Cailin.', grade='text'),
    G('The Drunkard\'s Tower', 'tower', ('in', 'Moat Cailin', -0.9, 0.5), *N, 'ACOK', 'A leaning tower of Moat Cailin, by the edge of the bog.', grade='text'),
    G('The Children\'s Tower', 'tower', ('in', 'Moat Cailin', 0.9, 0.6), *N, 'ACOK', 'A tower of Moat Cailin whose top is broken off.', grade='text'),

    # ------------------------------------------------------------ the Riverlands
    G('Oldstones', 'ruin', ('river', 'The Blue Fork', 0.3), *R, 'ASOS', 'The ruined castle of the old river kings on a hill above the Blue Fork.', grade='text'),
    G('Fairmarket', 'town', ('at', 46, -760), *R, 'ASOS', 'A market town in the north of the riverlands.'),
    G('Lord Harroway\'s Town', 'town', ('river', 'The Green Fork', 0.82), *R, 'AGOT', 'A town on the river near where the forks meet.'),
    G('Pinkmaiden', 'castle', ('near', 'Riverrun', 'W', 42), *R, 'AFFC', 'Seat of House Piper, west of Riverrun.', seat='Piper'),
    G('Atranta', 'castle', ('near', 'Riverrun', 'SSW', 38), *R, 'AFFC', 'Seat of a branch of House Vance.', seat='Vance'),
    G('Wayfarer\'s Rest', 'castle', ('near', 'Riverrun', 'SE', 48), *R, 'AGOT', 'Seat of House Vance of Wayfarer\'s Rest.', seat='Vance'),
    G('Stone Hedge', 'castle', ('at', 70, -861), *R, 'ACOK', 'Seat of House Bracken, rivals of the Blackwoods.', rank=4, seat='Bracken'),
    G('Pennytree', 'village', ('near', 'Raventree Hall', 'S', 16), *R, 'AFFC', 'A village with an ancient tree on its green.'),
    G('Stone Mill', 'landmark', ('near', 'Riverrun', 'E', 13), *R, 'ASOS', 'A mill on the Red Fork where the river was held against the Lannisters.'),
    G('High Heart', 'landmark', ('at', 39, -833), *R, 'ASOS', 'A lone hill crowned with weirwood stumps, sacred to the children of the forest.'),
    G('The Peach', 'inn', ('in', 'Stoney Sept', 0.5, 0.3), *R, 'ASOS', 'A brothel in Stoney Sept.', grade='text'),
    G('The Mummer\'s Ford', 'ford', ('river', 'The Red Fork', 0.25), *R, 'AGOT', 'A ford on the Red Fork where Lord Beric\'s men were ambushed.'),
    G('Sherrer', 'village', ('near', 'The Mummer\'s Ford', 'S', 10), *R, 'AGOT', 'A village burned by Ser Gregor Clegane\'s raiders.'),
    G('Harrentown', 'village', ('in', 'Harrenhal', 3.2, -2.4), *R, 'AFFC', 'The village by the lake under Harrenhal\'s walls.', grade='text'),
    # the five towers of Harrenhal
    G('The Kingspyre Tower', 'tower', ('in', 'Harrenhal', -0.9, 0.7), *R, 'ACOK', 'One of Harrenhal\'s five great towers, half melted by dragonfire.', grade='text'),
    G('The Widow\'s Tower', 'tower', ('in', 'Harrenhal', 0.9, 0.8), *R, 'ACOK', 'One of Harrenhal\'s five great towers.', grade='text'),
    G('The Tower of Dread', 'tower', ('in', 'Harrenhal', 1.1, -0.6), *R, 'ACOK', 'One of Harrenhal\'s five great towers.', grade='text'),
    G('The Wailing Tower', 'tower', ('in', 'Harrenhal', -1.0, -0.7), *R, 'ACOK', 'One of Harrenhal\'s five great towers, where the wind moans.', grade='text'),
    G('The Tower of Ghosts', 'tower', ('in', 'Harrenhal', 0.0, -1.2), *R, 'ACOK', 'The most ruined of Harrenhal\'s five towers.', grade='text'),

    # ------------------------------------------------------------ the Vale, the Fingers and the Three Sisters
    G('Stone', 'castle', ('between', 'Gates of the Moon', 'The Eyrie', 0.3), *V, 'AGOT', 'The lowest of the three waycastles on the climb to the Eyrie.', grade='text'),
    G('Snow', 'castle', ('between', 'Gates of the Moon', 'The Eyrie', 0.6), *V, 'AGOT', 'The middle waycastle on the climb to the Eyrie.', grade='text'),
    G('Sky', 'castle', ('between', 'Gates of the Moon', 'The Eyrie', 0.85), *V, 'AGOT', 'The highest waycastle, a wall around a ledge below the Eyrie.', grade='text'),
    G('Alyssa\'s Tears', 'landmark', ('in', 'The Eyrie', 2.0, 1.2), *V, 'AGOT', 'A waterfall on the Giant\'s Lance that never reaches the ground.', grade='text'),
    G('Heart\'s Home', 'castle', ('at', 468, -784), *V, 'AFFC', 'Seat of House Corbray.', rank=4, seat='Corbray'),
    G('Longbow Hall', 'castle', ('at', 429, -841), *V, 'AFFC', 'Seat of House Hunter.', seat='Hunter'),
    G('Redfort', 'castle', ('at', 437, -726), *V, 'AFFC', 'Seat of House Redfort.', seat='Redfort'),
    G('Ironoaks', 'castle', ('at', 394, -878), *V, 'AFFC', 'Seat of House Waynwood.', seat='Waynwood'),
    G('Strongsong', 'castle', ('at', 303, -705), *V, 'AFFC', 'Seat of House Belmore.', seat='Belmore'),
    G('Ninestars', 'castle', ('at', 502, -715), *V, 'AFFC', 'Seat of House Templeton.', seat='Templeton'),
    G('Sisterton', 'port', ('at', 286, -434), *V, 'ADWD', 'The smugglers\' port of the Three Sisters.', coast=True, seat='Sunderland'),

    # ------------------------------------------------------------ the Iron Islands
    G('Pyke', 'castle', ('at', -304, -718), *I, 'AGOT', 'Seat of House Greyjoy, its towers on stacks off the island\'s cliffs.', rank=2, coast=True, move=True, seat='Greyjoy'),
    G('Lordsport', 'port', ('at', -313, -738), *I, 'ACOK', 'The port of Pyke.', rank=4, coast=True, move=True),
    G('Hammerhorn', 'castle', ('at', -374, -754), *I, 'AFFC', 'Seat of House Goodbrother on Great Wyk.', seat='Goodbrother'),
    G('Pebbleton', 'town', ('at', -341, -776), *I, 'AFFC', 'A town on Great Wyk.', coast=True),
    G('Corpse Lake', 'castle', ('at', -386, -782), *I, 'AFFC', 'A holdfast of the Goodbrothers on Great Wyk.', seat='Goodbrother'),
    G('Harlaw Hall', 'castle', ('at', -288, -754), *I, 'AFFC', 'A holdfast of House Harlaw on Harlaw.', seat='Harlaw'),
    G('Grey Garden', 'castle', ('at', -292, -741), *I, 'AFFC', 'A holdfast of House Harlaw on Harlaw.', seat='Harlaw'),
    G('Volmark', 'castle', ('at', -273, -750), *I, 'AFFC', 'Seat of House Volmark on Harlaw.', seat='Volmark'),
    G('Blacktyde', 'castle', ('at', -337, -702), *I, 'AFFC', 'Seat of House Blacktyde on its island.', seat='Blacktyde'),
    G('Saltcliffe', 'castle', ('at', -381, -810), *I, 'AFFC', 'Seat of House Saltcliffe on its island.', coast=True, seat='Saltcliffe'),

    # ------------------------------------------------------------ the Westerlands
    G('Kayce', 'port', ('at', -382, -1065), *W, 'ACOK', 'A port town held by House Kenning.', coast=True, seat='Kenning'),
    G('Feastfires', 'castle', ('at', -334, -895), *W, 'ACOK', 'Seat of House Prester on the coast.', coast=True, seat='Prester'),
    G('The Banefort', 'castle', ('at', -330, -845), *W, 'ACOK', 'Seat of House Banefort, on the coast facing the Iron Islands.', coast=True, seat='Banefort'),
    G('Faircastle', 'castle', ('at', -375, -1008), *W, 'ACOK', 'Seat of House Farman on Fair Isle.', coast=True, seat='Farman'),
    G('Crakehall', 'castle', ('near', 'Lannisport', 'S', 62), *W, 'AGOT', 'Seat of House Crakehall.', rank=4, seat='Crakehall'),
    G('Hornvale', 'castle', ('at', -218, -1038), *W, 'AGOT', 'Seat of House Brax.', seat='Brax'),
    G('Deep Den', 'castle', ('at', -207, -1195), *W, 'ACOK', 'Seat of House Lydden.', seat='Lydden'),
    G('Silverhill', 'castle', ('at', -344, -1195), *W, 'ACOK', 'Seat of House Serrett.', seat='Serrett'),
    G('Sarsfield', 'castle', ('at', -279, -1158), *W, 'ACOK', 'Seat of House Sarsfield.', seat='Sarsfield'),
    G('Cornfield', 'castle', ('at', -365, -1296), *W, 'AFFC', 'Seat of House Swyft.', seat='Swyft'),
    G('Castamere', 'ruin', ('at', -306, -1028), *W, 'ASOS', 'The drowned ruin of House Reyne, destroyed by Tywin Lannister.', rank=4),
    G('Tarbeck Hall', 'ruin', ('at', -353, -1108), *W, 'ASOS', 'The ruin of House Tarbeck, destroyed with Castamere.'),

    # ------------------------------------------------------------ the Crownlands
    G('The Red Keep', 'landmark', ('in', 'King\'s Landing', 0.9, -0.2), *C, 'AGOT', 'The castle of the kings on Aegon\'s High Hill, above the river.', grade='text', move=True, rank=4),
    G('The Great Sept of Baelor', 'landmark', ('in', 'King\'s Landing', -1.1, 0.9), *C, 'AGOT', 'The great sept on Visenya\'s Hill.', grade='text', move=True),
    G('The Dragonpit', 'landmark', ('in', 'King\'s Landing', 1.6, 1.2), *C, 'AGOT', 'The ruined dome where the Targaryen dragons were kept, on Rhaenys\'s Hill.', grade='text'),
    G('Flea Bottom', 'landmark', ('in', 'King\'s Landing', 0.8, -0.4), *C, 'AGOT', 'The poorest quarter of King\'s Landing.', grade='text'),
    G('Stokeworth', 'castle', ('at', 259, -1226), *C, 'ACOK', 'Seat of House Stokeworth, north-east of King\'s Landing.', seat='Stokeworth'),
    G('Hayford', 'castle', ('near', 'King\'s Landing', 'W', 32), *C, 'ACOK', 'Seat of House Hayford, west of King\'s Landing.', seat='Hayford'),
    G('Spicetown', 'town', ('at', 428, -1123), *C, 'ACOK', 'The trading town of Driftmark, sacked in the Dance.', coast=True),
    G('Claw Isle', 'castle', ('at', 495, -1013), *C, 'ACOK', 'Seat of House Celtigar on its island.', coast=True, seat='Celtigar'),
    G('Sharp Point', 'castle', ('at', 518, -1029), *C, 'ACOK', 'Seat of House Bar Emmon at the tip of Crackclaw Point.', coast=True, seat='Bar Emmon'),
    G('Stonedance', 'castle', ('at', 452, -1220), *C, 'ACOK', 'Seat of House Massey on Massey\'s Hook.', coast=True, seat='Massey'),
    G('Rook\'s Rest', 'castle', ('at', 359, -1084), *C, 'ASOS', 'Seat of House Staunton on the coast north of Duskendale.', coast=True, seat='Staunton'),
    # the seven gates of King's Landing
    G('The Mud Gate', 'landmark', ('in', 'King\'s Landing', 0.4, -1.3), *C, 'ACOK', 'The river gate of King\'s Landing, by the fishmarket and the quays.', grade='text'),
    G('The King\'s Gate', 'landmark', ('in', 'King\'s Landing', 2.2, 1.6), *C, 'AGOT', 'The gate of King\'s Landing where the kingsroad leaves for the north.', grade='text'),
    G('The Lion Gate', 'landmark', ('in', 'King\'s Landing', 2.6, 0.3), *C, 'AGOT', 'A gate on the east side of King\'s Landing.'),
    G('The Old Gate', 'landmark', ('in', 'King\'s Landing', -0.6, 2.2), *C, 'AGOT', 'A gate on the north side of King\'s Landing.'),
    G('The Dragon Gate', 'landmark', ('in', 'King\'s Landing', 1.4, 2.4), *C, 'ACOK', 'A gate on the north-east side of King\'s Landing.'),
    G('The Gate of the Gods', 'landmark', ('in', 'King\'s Landing', -1.8, 1.6), *C, 'AGOT', 'The gate of King\'s Landing where the roseroad leaves.', grade='text'),
    G('The Iron Gate', 'landmark', ('in', 'King\'s Landing', -2.4, 0.2), *C, 'ACOK', 'A gate on the west side of King\'s Landing.'),
    G('The Street of Steel', 'landmark', ('in', 'King\'s Landing', 0.2, 0.9), *C, 'AGOT', 'The smiths\' street of King\'s Landing.', grade='text'),
    G('Maegor\'s Holdfast', 'hall', ('in', 'The Red Keep', 0.15, 0.1), *C, 'AGOT', 'The castle within the Red Keep, behind its dry moat.', grade='text'),
    G('The Tower of the Hand', 'tower', ('in', 'The Red Keep', -0.15, 0.12), *C, 'AGOT', 'The tower of the Red Keep where the King\'s Hand lives.', grade='text'),
    G('The White Sword Tower', 'tower', ('in', 'The Red Keep', 0.2, -0.12), *C, 'AGOT', 'The tower of the Kingsguard in the Red Keep, above the bay.', grade='text'),

    # ------------------------------------------------------------ the Stormlands
    G('Felwood', 'castle', ('at', 239, -1445), *S, 'ACOK', 'Seat of House Fell.', seat='Fell'),
    G('Parchments', 'castle', ('at', 400, -1487), *S, 'ACOK', 'Seat of House Penrose.', seat='Penrose'),
    G('Rain House', 'castle', ('at', 449, -1572), *S, 'ACOK', 'Seat of House Wylde on Shipbreaker Bay.', coast=True, seat='Wylde'),
    G('Stonehelm', 'castle', ('at', 469, -1674), *S, 'ACOK', 'Seat of House Swann near Cape Wrath.', coast=True, seat='Swann'),
    G('Mistwood', 'castle', ('at', 425, -1763), *S, 'ADWD', 'Seat of House Mertyns in the rainwood, taken by the Golden Company.', seat='Mertyns'),
    G('Weeping Town', 'port', ('at', 496, -1802), *S, 'ADWD', 'A port town on the coast of the rainwood.', coast=True),
    G('Harvest Hall', 'castle', ('at', 83, -1768), *S, 'ASOS', 'Seat of House Selmy in the Dornish Marches.', seat='Selmy'),
    G('Blackhaven', 'castle', ('at', 50, -1904), *S, 'AGOT', 'Seat of House Dondarrion in the Dornish Marches.', rank=4, seat='Dondarrion'),
    G('Greenstone', 'castle', ('at', 575, -1651), *S, 'ACOK', 'Seat of House Estermont on the isle of Estermont off Cape Wrath.', coast=True, seat='Estermont'),

    # ------------------------------------------------------------ the Reach
    G('Ashford', 'castle', ('at', -52, -1708), *H, 'AGOT', 'Seat of House Ashford, by a ford on the Cockleswhent.', seat='Ashford'),
    G('Cider Hall', 'castle', ('at', -105, -1678), *H, 'ACOK', 'Seat of House Fossoway, among apple orchards.', seat='Fossoway'),
    G('Longtable', 'castle', ('at', -49, -1584), *H, 'AFFC', 'Seat of House Merryweather.', seat='Merryweather'),
    G('Old Oak', 'castle', ('at', -355, -1719), *H, 'AGOT', 'Seat of House Oakheart, near the mouth of the Mander.', seat='Oakheart'),
    G('Red Lake', 'castle', ('at', -141, -1396), *H, 'ACOK', 'Seat of House Crane.', seat='Crane'),
    G('Uplands', 'castle', ('at', -265, -1926), *H, 'ACOK', 'Seat of House Mullendore.', seat='Mullendore'),
    G('Honeyholt', 'castle', ('at', -395, -1959), *H, 'AFFC', 'Seat of House Beesbury, known for its beehives.', seat='Beesbury'),
    G('Blackcrown', 'castle', ('at', -371, -1953), *H, 'AFFC', 'Seat of House Bulwer.', seat='Bulwer'),
    G('Greenshield', 'castle', ('at', -429, -1680), *H, 'ACOK', 'Seat of House Chester on the northernmost of the Shield Islands.', coast=True, seat='Chester'),
    G('Greyshield', 'castle', ('at', -440, -1715), *H, 'ACOK', 'Seat of House Grimm on the Shield Islands.', coast=True, seat='Grimm'),
    G('Southshield', 'castle', ('at', -447, -1734), *H, 'ACOK', 'Seat of House Serry on the southernmost Shield Island.', coast=True, seat='Serry'),
    G('Vinetown', 'town', ('at', -531, -2520), *H, 'AFFC', 'A town of the Arbor among its vineyards.', coast=True),
    G('Starpike', 'castle', ('at', -539, -2487), *H, 'AFFC', 'A castle of the Arbor.', seat='Redwyne'),
    G('The Starry Sept', 'sept', ('in', 'Oldtown', 0.9, 0.7), *H, 'AFFC', 'The old seat of the High Septon in Oldtown.', grade='text'),
    G('Battle Isle', 'landmark', ('in', 'Oldtown', -1.2, -0.4), *H, 'AFFC', 'The island in the Honeywine\'s mouth where the Hightower stands.', grade='text'),
    G('The Quill and Tankard', 'inn', ('in', 'Oldtown', 0.5, 1.2), *H, 'AFFC', 'An old inn on an island in the Honeywine, where the novices drink.', grade='text'),

    # ------------------------------------------------------------ Dorne
    G('Godsgrace', 'castle', ('river', 'The Greenblood', 0.35), *D, 'AFFC', 'Seat of House Allyrion on the Greenblood.', seat='Allyrion'),
    G('Lemonwood', 'castle', ('at', 519, -2326), *D, 'AFFC', 'Seat of House Dalt, on the coast south of Sunspear.', coast=True, seat='Dalt'),
    G('Ghost Hill', 'castle', ('at', 524, -2112), *D, 'AFFC', 'Seat of House Toland, on Dorne\'s northern coast.', coast=True, seat='Toland'),
    G('Salt Shore', 'castle', ('at', 139, -2530), *D, 'AFFC', 'Seat of House Gargalen on the south coast.', coast=True, seat='Gargalen'),
    G('The Tor', 'castle', ('at', 359, -2202), *D, 'AFFC', 'Seat of House Jordayne, on Dorne\'s northern coast.', coast=True, seat='Jordayne'),
    G('Kingsgrave', 'castle', ('at', 85, -2111), *D, 'AFFC', 'Seat of House Manwoody in the Red Mountains.', seat='Manwoody'),
    G('Blackmont', 'castle', ('at', -73, -2074), *D, 'AFFC', 'Seat of House Blackmont in the Red Mountains.', seat='Blackmont'),
    G('Wyl', 'castle', ('at', 166, -2115), *D, 'AFFC', 'Seat of House Wyl at the Dornish end of the Boneway.', seat='Wyl'),
    G('High Hermitage', 'castle', ('near', 'Starfall', 'E', 40), *D, 'AFFC', 'Seat of a branch of House Dayne.', seat='Dayne'),
    G('Sandstone', 'castle', ('at', -3, -2341), *D, 'AFFC', 'Seat of House Qorgyle in the sands.', seat='Qorgyle'),
    G('The Prince\'s Pass', 'landmark', ('at', -130, -2107), *D, 'AFFC', 'The pass through the Red Mountains from the Reach into Dorne.'),
    G('The Tower of the Sun', 'tower', ('in', 'Sunspear', 0.3, 0.4), *D, 'AFFC', 'The great domed tower of Sunspear.', grade='text'),
    G('The Spear Tower', 'tower', ('in', 'Sunspear', -0.4, 0.2), *D, 'AFFC', 'The slender tower of Sunspear, tipped with a gilded spear.', grade='text'),
    G('The Shadow City', 'landmark', ('in', 'Sunspear', -1.5, -0.8), *D, 'AFFC', 'The town of mud-brick and sandstone in the shadow of Sunspear\'s walls.', grade='text'),
    G('Shandystone', 'ruin', ('near', 'Sandstone', 'E', 70), *D, 'AFFC', 'A dead village in the deep sands, its well long dry.'),
    G('Ghaston Grey', 'castle', ('at', -270, -2520), *D, 'AFFC', 'A crumbling castle on a rock in the sea off Dorne, used as a prison.'),

    # ------------------------------------------------------------ wave three: more of Westeros's seats and holdfasts
    G('Antlers', 'castle', ('near', 'King\'s Landing', 'NW', 60), *C, 'ACOK', 'Seat of House Buckwell in the crownlands.', seat='Buckwell'),
    G('Sow\'s Horn', 'castle', ('near', 'Duskendale', 'W', 40), *C, 'AFFC', 'Seat of House Hogg in the crownlands.', seat='Hogg'),
    G('The Whispers', 'ruin', ('near', 'Sharp Point', 'W', 35), *C, 'AFFC', 'A ruined castle over a cove on Crackclaw Point.', coast=True),
    G('Dyre Den', 'castle', ('near', 'Rook\'s Rest', 'E', 45), *C, 'AFFC', 'Seat of House Brune on Crackclaw Point.', seat='Brune'),
    G('Crow\'s Nest', 'castle', ('near', 'Felwood', 'E', 55), *S, 'TWOIAF', 'Seat of House Morrigen in the stormlands.', seat='Morrigen'),
    G('Haystack Hall', 'castle', ('near', 'Bronzegate', 'S', 55), *S, 'TWOIAF', 'Seat of House Errol in the stormlands.', seat='Errol'),
    G('Grandview', 'castle', ('near', 'Storm\'s End', 'W', 95), *S, 'TWOIAF', 'Seat of House Grandison in the stormlands.', seat='Grandison'),
    G('Gallowsgrey', 'castle', ('near', 'Summerhall', 'E', 70), *S, 'TWOIAF', 'Seat of House Trant in the stormlands.', seat='Trant'),
    G('New Barrel', 'castle', ('near', 'Cider Hall', 'N', 35), *H, 'ASOS', 'Seat of the Fossoways of New Barrel, who broke from the house of Cider Hall.', seat='Fossoway'),
    G('Coldmoat', 'castle', ('near', 'Highgarden', 'NE', 130), *H, 'D&E', 'A castle with a wide moat, seat of the Webbers in the days of Dunk and Egg.', seat='Webber'),
    G('Standfast', 'holdfast', ('near', 'Coldmoat', 'W', 25), *H, 'D&E', 'The small towerhouse of the Osgreys, a day\'s ride from Coldmoat.', rank=6, seat='Osgrey'),
    G('Whitewalls', 'castle', ('near', 'The Isle of Faces', 'S', 70), *R, 'D&E', 'The pale castle of the Butterwells, where a wedding tourney hid a plot.', seat='Butterwell'),
    G('Coldwater Burn', 'castle', ('near', 'Gulltown', 'NW', 70), *V, 'AFFC', 'Seat of House Coldwater in the Vale.', seat='Coldwater'),
    G('Harridan Hill', 'castle', ('near', 'Harlaw Hall', 'E', 8), *I, 'AFFC', 'A holdfast of a branch of House Harlaw on Harlaw.', rank=6, seat='Harlaw'),
    G('The Tower of Glimmering', 'tower', ('near', 'Ten Towers', 'N', 8), *I, 'AFFC', 'A tower of a branch of House Harlaw on Harlaw.', rank=6, seat='Harlaw'),
    G('Crow Spike Keep', 'castle', ('near', 'Hammerhorn', 'N', 12), *I, 'AFFC', 'A holdfast of House Goodbrother on Great Wyk.', rank=6, seat='Goodbrother'),
    G('Downdelving', 'castle', ('near', 'Hammerhorn', 'SW', 14), *I, 'AFFC', 'A holdfast of House Goodbrother on Great Wyk.', rank=6, seat='Goodbrother'),
    G('Shatterstone', 'castle', ('near', 'Corpse Lake', 'S', 12), *I, 'AFFC', 'A holdfast of House Goodbrother on Great Wyk.', rank=6, seat='Goodbrother'),
    G('Sealskin Point', 'castle', ('near', 'Hammerhorn', 'W', 22), *I, 'AFFC', 'A holdfast of House Farwynd on a western point of Great Wyk.', coast=True, rank=6, seat='Farwynd'),
    G('Lonely Light', 'castle', ('at', -640, -500), *I, 'AFFC', 'Seat of House Farwynd on the westernmost of the Iron Islands, far out in the Sunset Sea.', seat='Farwynd'),
]

# ---------------------------------------------------------------- Essos, Sothoryos and the islands of the summer seas
VOL, GHIS, VAL, DOTH, IBB = ('freecity', 'Volantis'), ('ghiscari', 'Slaver\'s Bay'), ('valyria', 'Valyria'), ('dothraki', 'The Dothraki Sea'), ('ib', 'Ib')
PLACES += [
    G('Valysar', 'town', ('on', 'The Rhoyne', 1353, -1939), *VOL, 'ADWD', 'A Volantene town on the Rhoyne below Selhorys.', grade='text'),
    G('Sar Mell', 'ruin', ('on', 'The Rhoyne', 1361, -2010), *VOL, 'TWOIAF', 'A Rhoynar city on the lower Rhoyne, sacked by Valyria in the last war against the Rhoynar.', grade='text'),
    G('Volon Therys', 'town', ('on', 'The Rhoyne', 1356, -2075), *VOL, 'ADWD', 'A Volantene town on the Rhoyne, the last before Volantis.', grade='text'),
    G('Sarhoy', 'ruin', ('on', 'The Rhoyne, the Sarhoy mouth', 1298, -2145), *VOL, 'TWOIAF', 'A Rhoynar port at one of the mouths of the Rhoyne, burned and salted by Volantis and the dragonlords.', coast=True),
    G('Ghoyan Drohe', 'ruin', ('on', 'The Little Rhoyne', 985, -1040), *('freecity', 'Norvos'), 'ADWD', 'A Rhoynar city burned by the dragonlords, on the Little Rhoyne above its meeting with the Upper Rhoyne.', grade='text'),
    G('Ar Noy', 'ruin', ('on', 'The Qhoyne', 1375, -1160), *('freecity', 'Qohor'), 'ADWD', 'A ruined Rhoynar city on the Qhoyne, below Qohor.', grade='text'),
    G('Ny Sar', 'ruin', ('on', 'The Rhoyne', 1200, -1140), *('freecity', 'Norvos'), 'ADWD', 'A ruined Rhoynar city on the Rhoyne, just below where the Noyne joins it.', grade='text'),
    G('Tolos', 'city', ('near', 'New Ghis', 'NW', 95), *GHIS, 'ADWD', 'A city on the Gulf of Grief, famed for its slingers.', rank=4, coast=True),
    G('Elyria', 'city', ('near', 'New Ghis', 'W', 160), *GHIS, 'ADWD', 'A city of the Gulf of Grief, an ally of Yunkai.', rank=5, coast=True),
    G('Old Ghis', 'ruin', ('near', 'New Ghis', 'N', 140), *GHIS, 'ASOS', 'The ruins of the first city of the Ghiscari, sown with salt by Valyria.', rank=4),
    G('Oros', 'ruin', ('near', 'Valyria', 'W', 60), *VAL, 'TWOIAF', 'A city of the Freehold drowned in the Doom.'),
    G('Tyria', 'ruin', ('near', 'Valyria', 'NW', 60), *VAL, 'TWOIAF', 'A city of the Freehold drowned in the Doom.'),
    G('The House of Black and White', 'temple', ('in', 'Braavos', 0.8, -0.6), *('braavos', 'Braavos'), 'AFFC', 'The temple of the Many-Faced God in Braavos, where Arya trains.', rank=4, grade='text'),
    G('Sathar', 'ruin', ('at', 2300, -800), *DOTH, 'TWOIAF', 'The ruined capital of the Tall Men of Sarnor.', rank=4),
    G('Kasath', 'ruin', ('at', 2050, -760), *DOTH, 'TWOIAF', 'A ruined city of Sarnor.'),
    G('Mardosh', 'ruin', ('at', 2560, -790), *DOTH, 'TWOIAF', 'A ruined city of Sarnor.'),
    G('Sallosh', 'ruin', ('at', 2180, -920), *DOTH, 'TWOIAF', 'A ruined city of Sarnor.'),
    G('Hornoth', 'ruin', ('at', 2440, -930), *DOTH, 'TWOIAF', 'A ruined city of Sarnor.'),
    G('Kyth', 'ruin', ('at', 1920, -880), *DOTH, 'TWOIAF', 'A ruined city of Sarnor.'),
    G('Gornath', 'ruin', ('at', 2680, -870), *DOTH, 'TWOIAF', 'A ruined city of Sarnor.'),
    G('Saath', 'ruin', ('at', 1600, -300), *('lorath', 'Lorath'), 'TWOIAF', 'A ruined city on the shore of the Shivering Sea east of Lorath.', coast=True),
    G('Ib Sar', 'town', ('at', 2780, 70), *IBB, 'TWOIAF', 'A town of the hairy men of Ib.'),
    G('New Ibbish', 'town', ('at', 3330, -190), *IBB, 'TWOIAF', 'The colony of Ib on the Axe, on the mainland of Essos.', coast=True),
    G('Bayasabhad', 'city', ('at', 3400, -1350), *('east', 'Hyrkoon'), 'TWOIAF', 'One of the three cities of the Patrimony of Hyrkoon.', rank=4),
    G('Samyriana', 'city', ('at', 3600, -1500), *('east', 'Hyrkoon'), 'TWOIAF', 'One of the three cities of the Patrimony of Hyrkoon.', rank=4),
    G('Kayakayanaya', 'city', ('at', 3500, -1720), *('east', 'Hyrkoon'), 'TWOIAF', 'One of the three cities of the Patrimony of Hyrkoon.', rank=4),
    G('Si Qo', 'city', ('near', 'Yin', 'NE', 320), *('yiti', 'Yi Ti'), 'TWOIAF', 'A great city of Yi Ti.', rank=4),
    G('Stygai', 'ruin', ('near', 'Asshai', 'N', 200), *('shadow', 'Asshai'), 'TWOIAF', 'A dead city deep in the Shadow.'),
    G('Gorosh', 'ruin', ('near', 'Yeen', 'E', 220), *('sothoryos', 'Sothoryos'), 'TWOIAF', 'A ruined city in the jungles of Sothoryos.'),
    G('Gogossos', 'city', ('at', 1700, -2880), *('sothoryos', 'The Basilisk Isles'), 'TWOIAF', 'A city of the Basilisk Isles, a haunt of corsairs and slavers.', rank=5),
    G('Lotus Port', 'port', ('near', 'Tall Trees Town', 'W', 40), *('summer', 'The Summer Isles'), 'TWOIAF', 'A port of the Summer Isles.', coast=True),
    G('Last Lament', 'town', ('near', 'Tall Trees Town', 'S', 15), *('summer', 'The Summer Isles'), 'TWOIAF', 'A town of the Summer Isles.'),
]

# importance: how large each place is drawn and from how far out it shows (1 the great cities ... 5 lesser seats, 6 points)
RANKS = {'Oldtown': 1, 'Volantis': 1, 'Qarth': 1, 'Gulltown': 2, 'Myr': 2, 'Lys': 2, 'Tyrosh': 2, 'Norvos': 2, 'Qohor': 2,
         'Lorath': 2, 'Asshai': 2, 'Yunkai': 2}


def resolve(places, rivers, walls, log=print):
    """-> (new place rows, moved names). places: author.PLACES rows [name, kind, x, y, people, realm, note, opts]."""
    from shapely.geometry import LineString
    at = {p[0]: p for p in places}
    riv = {r['name']: LineString(r['pts']) for r in rivers}
    wall = next(w['pts'] for w in walls if w.get('ice'))
    new, moved = [], []
    for e in PLACES:
        w = e['where']
        if w[0] == 'at': x, y = w[1], w[2]
        elif w[0] in ('near', 'in'):
            a = at[w[1]]
            if w[0] == 'in': x, y = a[2] + w[2], a[3] + w[3]
            else:
                b = math.radians(BEARING[w[2]] if isinstance(w[2], str) else w[2])
                x, y = a[2] + math.cos(b) * w[3], a[3] + math.sin(b) * w[3]
        elif w[0] == 'between':
            a, b = at[w[1]], at[w[2]]; x, y = a[2] + (b[2] - a[2]) * w[3], a[3] + (b[3] - a[3]) * w[3]
        elif w[0] == 'river':
            q = riv[w[1]].interpolate(w[2], normalized=True); x, y = q.x, q.y
        elif w[0] == 'on':
            from shapely.geometry import Point
            q = riv[w[1]].interpolate(riv[w[1]].project(Point(w[2], w[3]))); x, y = q.x, q.y
        elif w[0] == 'wall':
            x = w[1]; y = next(a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]) for a, b in zip(wall, wall[1:]) if a[0] <= x <= b[0])
        else: raise ValueError(w)
        o = {'rank': e['rank'], 'grade': e['grade'], 'src': e['src']}
        for k in ('seat', 'coast', 'label'):
            if k in e: o[k] = e[k]
        if e.get('move') and e['name'] in at:
            p = at[e['name']]; p[2], p[3] = round(x, 1), round(y, 1); p[7].update(o); moved.append(e['name']); continue
        if e['name'] in at: log(f"  gazetteer: {e['name']} is already on the map; left as it is"); continue
        row = [e['name'], KIND.get(e['kind'], e['kind']), round(x, 1), round(y, 1), e['people'], e['realm'], e['note'], o]
        new.append(row); at[e['name']] = row
    for name, r in RANKS.items():
        if name in at: at[name][7]['rank'] = r
    return new, moved
