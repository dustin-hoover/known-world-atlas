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
  ('wall', X)                   on the Wall, where it crosses X
`coast=True` puts a place on the waterline (a port, a castle on a sea cliff); `move=True` moves a place already
in author.py instead of adding one. `seat` names the house that holds it in the novels (phase 5 fills in the rest).
"""
import math

BEARING = {'N': 90, 'NNE': 67.5, 'NE': 45, 'ENE': 22.5, 'E': 0, 'ESE': -22.5, 'SE': -45, 'SSE': -67.5, 'S': -90,
           'SSW': -112.5, 'SW': -135, 'WSW': -157.5, 'W': 180, 'WNW': 157.5, 'NW': 135, 'NNW': 112.5}
KIND = {'castle': 'fortress', 'holdfast': 'fortress', 'inn': 'village', 'sept': 'landmark', 'hall': 'landmark'}


def G(name, kind, where, people, realm, src, note, rank=5, grade='inferred', **o):
    return {'name': name, 'kind': kind, 'where': where, 'people': people, 'realm': realm, 'src': src, 'note': note,
            'rank': rank, 'grade': grade, **o}


N, R, V, I, W, C, S, H, D = ('north', 'The North'), ('river', 'The Riverlands'), ('vale', 'The Vale'), \
    ('iron', 'The Iron Islands'), ('west', 'The Westerlands'), ('crown', 'The Crownlands'), ('storm', 'The Stormlands'), \
    ('reach', 'The Reach'), ('dorne', 'Dorne')
WATCH = ('watch', 'The Wall')

PLACES = [
    # ------------------------------------------------------------ the Wall: its nineteen castles, west to east
    G('Sentinel Stand', 'ruin', ('wall', -98), *WATCH, 'AFFC', 'An abandoned castle of the Night\'s Watch on the Wall.', grade='text'),
    G('Greyguard', 'ruin', ('wall', -86), *WATCH, 'ASOS', 'A castle of the Watch on the Wall, given to the free folk to hold.', grade='text'),
    G('Stonedoor', 'ruin', ('wall', -74), *WATCH, 'ASOS', 'A castle of the Watch at a gate through the Wall, given to the free folk.', grade='text'),
    G('Hoarfrost Hill', 'ruin', ('wall', -63), *WATCH, 'ADWD', 'An abandoned castle of the Watch on the Wall.', grade='text'),
    G('Icemark', 'ruin', ('wall', -52), *WATCH, 'ADWD', 'An abandoned castle of the Watch on the Wall.', grade='text'),
    G('Deep Lake', 'ruin', ('wall', -20), *WATCH, 'ADWD', 'A castle of the Watch on the Wall, reopened in the novels.', grade='text'),
    G('Queensgate', 'ruin', ('wall', 0), *WATCH, 'ADWD', 'A castle of the Watch on the Wall, named for a queen who visited it.', grade='text'),
    G('Oakenshield', 'ruin', ('wall', 38), *WATCH, 'ADWD', 'A castle of the Watch on the Wall, given to the free folk.', grade='text'),
    G('Woodswatch-by-the-Pool', 'ruin', ('wall', 55), *WATCH, 'ADWD', 'An abandoned castle of the Watch by a pool below the Wall.', grade='text'),
    G('Sable Hall', 'ruin', ('wall', 73), *WATCH, 'ADWD', 'A castle of the Watch on the Wall, given to the free folk.', grade='text'),
    G('Rimegate', 'ruin', ('wall', 91), *WATCH, 'ADWD', 'An abandoned castle of the Watch on the Wall.', grade='text'),
    G('The Long Barrow', 'ruin', ('wall', 108), *WATCH, 'ADWD', 'A castle of the Watch built against a great barrow, reopened in the novels.', grade='text'),
    G('The Torches', 'ruin', ('wall', 126), *WATCH, 'ADWD', 'An abandoned castle of the Watch on the Wall.', grade='text'),
    G('Greenguard', 'ruin', ('wall', 143), *WATCH, 'ADWD', 'A castle of the Watch near the Wall\'s eastern end.', grade='text'),

    G('The Bridge of Skulls', 'landmark', ('in', 'Westwatch-by-the-Bridge', -2.0, 3.0), *WATCH, 'ACOK', 'The bridge across the Gorge west of the Shadow Tower.', grade='text'),

    # ------------------------------------------------------------ the North
    G('Wintertown', 'town', ('in', 'Winterfell', 2.5, -2.5), *N, 'AGOT', 'The town under Winterfell\'s walls, which fills in winter.', grade='text'),
    G('Castle Cerwyn', 'castle', ('near', 'Winterfell', 'ESE', 24), *N, 'ACOK', 'Seat of House Cerwyn, within a day\'s ride of Winterfell.', grade='text', seat='Cerwyn'),
    G('Hornwood', 'castle', ('at', 215, -95), *N, 'ACOK', 'Seat of House Hornwood, between the Dreadfort and the White Knife.', rank=4, seat='Hornwood'),
    G('Oldcastle', 'castle', ('at', 330, -205), *N, 'ADWD', 'Seat of House Locke, on the east coast above White Harbor.', coast=True, seat='Locke'),
    G('Flint\'s Finger', 'castle', ('at', -340, -300), *N, 'TWOIAF', 'Seat of a branch of House Flint, on a finger of land on the west coast.', coast=True, seat='Flint'),
    G('The Wolf\'s Den', 'hall', ('in', 'White Harbor', 1.0, 0.6), *N, 'ADWD', 'The old stronghold of White Harbor, older than the city around it.', grade='text'),
    G('The New Castle', 'hall', ('in', 'White Harbor', -0.6, 1.1), *N, 'ADWD', 'The Manderlys\' castle on the hill above White Harbor.', grade='text'),
    G('The Sept of the Snows', 'sept', ('in', 'White Harbor', 0.4, -0.7), *N, 'ADWD', 'The great sept of White Harbor.', grade='text'),
    G('The Great Barrow', 'landmark', ('in', 'Barrowton', 1.6, 0.6), *N, 'ADWD', 'The vast barrow of the First King beside Barrowton.', grade='text'),
    G('The Gatehouse Tower', 'tower', ('in', 'Moat Cailin', 0.0, -0.9), *N, 'ACOK', 'One of the three towers still standing at Moat Cailin.', grade='text'),
    G('The Drunkard\'s Tower', 'tower', ('in', 'Moat Cailin', -0.9, 0.5), *N, 'ACOK', 'A leaning tower of Moat Cailin, by the edge of the bog.', grade='text'),
    G('The Children\'s Tower', 'tower', ('in', 'Moat Cailin', 0.9, 0.6), *N, 'ACOK', 'A tower of Moat Cailin whose top is broken off.', grade='text'),

    # ------------------------------------------------------------ the Riverlands
    G('Oldstones', 'ruin', ('river', 'The Blue Fork', 0.3), *R, 'ASOS', 'The ruined castle of the old river kings on a hill above the Blue Fork.', grade='text'),
    G('Fairmarket', 'town', ('at', 70, -740), *R, 'ASOS', 'A market town in the north of the riverlands.'),
    G('Lord Harroway\'s Town', 'town', ('river', 'The Green Fork', 0.82), *R, 'AGOT', 'A town on the river near where the forks meet.'),
    G('Pinkmaiden', 'castle', ('near', 'Riverrun', 'W', 42), *R, 'AFFC', 'Seat of House Piper, west of Riverrun.', seat='Piper'),
    G('Atranta', 'castle', ('near', 'Riverrun', 'SSW', 38), *R, 'AFFC', 'Seat of a branch of House Vance.', seat='Vance'),
    G('Wayfarer\'s Rest', 'castle', ('near', 'Riverrun', 'SE', 48), *R, 'AGOT', 'Seat of House Vance of Wayfarer\'s Rest.', seat='Vance'),
    G('Stone Hedge', 'castle', ('at', 70, -860), *R, 'ACOK', 'Seat of House Bracken, rivals of the Blackwoods.', rank=4, seat='Bracken'),
    G('Pennytree', 'village', ('near', 'Raventree Hall', 'S', 16), *R, 'AFFC', 'A village with an ancient tree on its green.'),
    G('Stone Mill', 'landmark', ('near', 'Riverrun', 'E', 13), *R, 'ASOS', 'A mill on the Red Fork where the river was held against the Lannisters.'),
    G('High Heart', 'landmark', ('at', 55, -820), *R, 'ASOS', 'A lone hill crowned with weirwood stumps, sacred to the children of the forest.'),
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
    G('Heart\'s Home', 'castle', ('at', 470, -775), *V, 'AFFC', 'Seat of House Corbray.', rank=4, seat='Corbray'),
    G('Longbow Hall', 'castle', ('at', 430, -830), *V, 'AFFC', 'Seat of House Hunter.', seat='Hunter'),
    G('Redfort', 'castle', ('at', 440, -705), *V, 'AFFC', 'Seat of House Redfort.', seat='Redfort'),
    G('Ironoaks', 'castle', ('at', 395, -865), *V, 'AFFC', 'Seat of House Waynwood.', seat='Waynwood'),
    G('Strongsong', 'castle', ('at', 300, -690), *V, 'AFFC', 'Seat of House Belmore.', seat='Belmore'),
    G('Ninestars', 'castle', ('at', 505, -705), *V, 'AFFC', 'Seat of House Templeton.', seat='Templeton'),
    G('Sisterton', 'port', ('at', 330, -300), *V, 'ADWD', 'The smugglers\' port of the Three Sisters.', coast=True, seat='Sunderland'),

    # ------------------------------------------------------------ the Iron Islands
    G('Pyke', 'castle', ('at', -334, -672), *I, 'AGOT', 'Seat of House Greyjoy, its towers on stacks off the island\'s cliffs.', rank=2, coast=True, move=True, seat='Greyjoy'),
    G('Lordsport', 'port', ('at', -347, -700), *I, 'ACOK', 'The port of Pyke.', rank=4, coast=True, move=True),
    G('Hammerhorn', 'castle', ('at', -430, -722), *I, 'AFFC', 'Seat of House Goodbrother on Great Wyk.', seat='Goodbrother'),
    G('Pebbleton', 'town', ('at', -385, -752), *I, 'AFFC', 'A town on Great Wyk.', coast=True),
    G('Corpse Lake', 'castle', ('at', -446, -760), *I, 'AFFC', 'A holdfast of the Goodbrothers on Great Wyk.', seat='Goodbrother'),
    G('Harlaw Hall', 'castle', ('at', -312, -722), *I, 'AFFC', 'A holdfast of House Harlaw on Harlaw.', seat='Harlaw'),
    G('Grey Garden', 'castle', ('at', -318, -704), *I, 'AFFC', 'A holdfast of House Harlaw on Harlaw.', seat='Harlaw'),
    G('Volmark', 'castle', ('at', -292, -716), *I, 'AFFC', 'Seat of House Volmark on Harlaw.', seat='Volmark'),
    G('Blacktyde', 'castle', ('at', -380, -650), *I, 'AFFC', 'Seat of House Blacktyde on its island.', seat='Blacktyde'),
    G('Saltcliffe', 'castle', ('at', -440, -798), *I, 'AFFC', 'Seat of House Saltcliffe on its island.', coast=True, seat='Saltcliffe'),

    # ------------------------------------------------------------ the Westerlands
    G('Kayce', 'port', ('at', -445, -1100), *W, 'ACOK', 'A port town held by House Kenning.', coast=True, seat='Kenning'),
    G('Feastfires', 'castle', ('at', -470, -945), *W, 'ACOK', 'Seat of House Prester on the coast.', coast=True, seat='Prester'),
    G('The Banefort', 'castle', ('at', -455, -880), *W, 'ACOK', 'Seat of House Banefort, on the coast facing the Iron Islands.', coast=True, seat='Banefort'),
    G('Faircastle', 'castle', ('at', -481, -1060), *W, 'ACOK', 'Seat of House Farman on Fair Isle.', coast=True, seat='Farman'),
    G('Crakehall', 'castle', ('near', 'Lannisport', 'S', 62), *W, 'AGOT', 'Seat of House Crakehall.', rank=4, seat='Crakehall'),
    G('Hornvale', 'castle', ('at', -225, -1035), *W, 'AGOT', 'Seat of House Brax.', seat='Brax'),
    G('Deep Den', 'castle', ('at', -185, -1180), *W, 'ACOK', 'Seat of House Lydden.', seat='Lydden'),
    G('Silverhill', 'castle', ('at', -330, -1185), *W, 'ACOK', 'Seat of House Serrett.', seat='Serrett'),
    G('Sarsfield', 'castle', ('at', -265, -1150), *W, 'ACOK', 'Seat of House Sarsfield.', seat='Sarsfield'),
    G('Cornfield', 'castle', ('at', -360, -1265), *W, 'AFFC', 'Seat of House Swyft.', seat='Swyft'),
    G('Castamere', 'ruin', ('at', -345, -1045), *W, 'ASOS', 'The drowned ruin of House Reyne, destroyed by Tywin Lannister.', rank=4),
    G('Tarbeck Hall', 'ruin', ('at', -365, -1120), *W, 'ASOS', 'The ruin of House Tarbeck, destroyed with Castamere.'),

    # ------------------------------------------------------------ the Crownlands
    G('The Red Keep', 'landmark', ('in', 'King\'s Landing', 0.9, -0.2), *C, 'AGOT', 'The castle of the kings on Aegon\'s High Hill, above the river.', grade='text', move=True, rank=4),
    G('The Great Sept of Baelor', 'landmark', ('in', 'King\'s Landing', -1.1, 0.9), *C, 'AGOT', 'The great sept on Visenya\'s Hill.', grade='text', move=True),
    G('The Dragonpit', 'landmark', ('in', 'King\'s Landing', 1.6, 1.2), *C, 'AGOT', 'The ruined dome where the Targaryen dragons were kept, on Rhaenys\'s Hill.', grade='text'),
    G('Flea Bottom', 'landmark', ('in', 'King\'s Landing', 0.8, -0.4), *C, 'AGOT', 'The poorest quarter of King\'s Landing.', grade='text'),
    G('Stokeworth', 'castle', ('at', 262, -1238), *C, 'ACOK', 'Seat of House Stokeworth, north-east of King\'s Landing.', seat='Stokeworth'),
    G('Hayford', 'castle', ('near', 'King\'s Landing', 'W', 32), *C, 'ACOK', 'Seat of House Hayford, west of King\'s Landing.', seat='Hayford'),
    G('Spicetown', 'town', ('at', 358, -1198), *C, 'ACOK', 'The trading town of Driftmark, sacked in the Dance.', coast=True),
    G('Claw Isle', 'castle', ('at', 445, -1068), *C, 'ACOK', 'Seat of House Celtigar on its island.', coast=True, seat='Celtigar'),
    G('Sharp Point', 'castle', ('at', 455, -1102), *C, 'ACOK', 'Seat of House Bar Emmon at the tip of Crackclaw Point.', coast=True, seat='Bar Emmon'),
    G('Stonedance', 'castle', ('at', 392, -1292), *C, 'ACOK', 'Seat of House Massey on Massey\'s Hook.', coast=True, seat='Massey'),
    G('Rook\'s Rest', 'castle', ('at', 330, -1112), *C, 'ASOS', 'Seat of House Staunton on the coast north of Duskendale.', coast=True, seat='Staunton'),
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
    G('Felwood', 'castle', ('at', 230, -1450), *S, 'ACOK', 'Seat of House Fell.', seat='Fell'),
    G('Parchments', 'castle', ('at', 380, -1488), *S, 'ACOK', 'Seat of House Penrose.', seat='Penrose'),
    G('Rain House', 'castle', ('at', 440, -1560), *S, 'ACOK', 'Seat of House Wylde on Shipbreaker Bay.', coast=True, seat='Wylde'),
    G('Stonehelm', 'castle', ('at', 470, -1660), *S, 'ACOK', 'Seat of House Swann near Cape Wrath.', coast=True, seat='Swann'),
    G('Mistwood', 'castle', ('at', 430, -1760), *S, 'ADWD', 'Seat of House Mertyns in the rainwood, taken by the Golden Company.', seat='Mertyns'),
    G('Weeping Town', 'port', ('at', 500, -1800), *S, 'ADWD', 'A port town on the coast of the rainwood.', coast=True),
    G('Harvest Hall', 'castle', ('at', 90, -1760), *S, 'ASOS', 'Seat of House Selmy in the Dornish Marches.', seat='Selmy'),
    G('Blackhaven', 'castle', ('at', 50, -1930), *S, 'AGOT', 'Seat of House Dondarrion in the Dornish Marches.', rank=4, seat='Dondarrion'),
    G('Greenstone', 'castle', ('at', 585, -1640), *S, 'ACOK', 'Seat of House Estermont on the isle of Estermont off Cape Wrath.', coast=True, seat='Estermont'),

    # ------------------------------------------------------------ the Reach
    G('Ashford', 'castle', ('at', -60, -1620), *H, 'AGOT', 'Seat of House Ashford, by a ford on the Cockleswhent.', seat='Ashford'),
    G('Cider Hall', 'castle', ('at', -120, -1565), *H, 'ACOK', 'Seat of House Fossoway, among apple orchards.', seat='Fossoway'),
    G('Longtable', 'castle', ('at', -60, -1520), *H, 'AFFC', 'Seat of House Merryweather.', seat='Merryweather'),
    G('Old Oak', 'castle', ('at', -460, -1650), *H, 'AGOT', 'Seat of House Oakheart, near the mouth of the Mander.', seat='Oakheart'),
    G('Red Lake', 'castle', ('at', -130, -1350), *H, 'ACOK', 'Seat of House Crane.', seat='Crane'),
    G('Uplands', 'castle', ('at', -240, -1800), *H, 'ACOK', 'Seat of House Mullendore.', seat='Mullendore'),
    G('Honeyholt', 'castle', ('at', -360, -1960), *H, 'AFFC', 'Seat of House Beesbury, known for its beehives.', seat='Beesbury'),
    G('Blackcrown', 'castle', ('at', -330, -1925), *H, 'AFFC', 'Seat of House Bulwer.', seat='Bulwer'),
    G('Greenshield', 'castle', ('at', -594, -1733), *H, 'ACOK', 'Seat of House Chester on the northernmost of the Shield Islands.', coast=True, seat='Chester'),
    G('Greyshield', 'castle', ('at', -594, -1772), *H, 'ACOK', 'Seat of House Grimm on the Shield Islands.', coast=True, seat='Grimm'),
    G('Southshield', 'castle', ('at', -594, -1790), *H, 'ACOK', 'Seat of House Serry on the southernmost Shield Island.', coast=True, seat='Serry'),
    G('Vinetown', 'town', ('at', -578, -2242), *H, 'AFFC', 'A town of the Arbor among its vineyards.', coast=True),
    G('Starpike', 'castle', ('at', -588, -2222), *H, 'AFFC', 'A castle of the Arbor.', seat='Redwyne'),
    G('The Starry Sept', 'sept', ('in', 'Oldtown', 0.9, 0.7), *H, 'AFFC', 'The old seat of the High Septon in Oldtown.', grade='text'),
    G('Battle Isle', 'landmark', ('in', 'Oldtown', -1.2, -0.4), *H, 'AFFC', 'The island in the Honeywine\'s mouth where the Hightower stands.', grade='text'),
    G('The Quill and Tankard', 'inn', ('in', 'Oldtown', 0.5, 1.2), *H, 'AFFC', 'An old inn on an island in the Honeywine, where the novices drink.', grade='text'),

    # ------------------------------------------------------------ Dorne
    G('Godsgrace', 'castle', ('river', 'The Greenblood', 0.35), *D, 'AFFC', 'Seat of House Allyrion on the Greenblood.', seat='Allyrion'),
    G('Lemonwood', 'castle', ('at', 520, -2330), *D, 'AFFC', 'Seat of House Dalt, on the coast south of Sunspear.', coast=True, seat='Dalt'),
    G('Ghost Hill', 'castle', ('at', 560, -2385), *D, 'AFFC', 'Seat of House Toland on the coast.', coast=True, seat='Toland'),
    G('Salt Shore', 'castle', ('at', 150, -2520), *D, 'AFFC', 'Seat of House Gargalen on the south coast.', coast=True, seat='Gargalen'),
    G('The Tor', 'castle', ('at', -80, -2480), *D, 'AFFC', 'Seat of House Jordayne on the south coast.', coast=True, seat='Jordayne'),
    G('Kingsgrave', 'castle', ('at', 60, -2145), *D, 'AFFC', 'Seat of House Manwoody in the Red Mountains.', seat='Manwoody'),
    G('Blackmont', 'castle', ('at', -100, -2150), *D, 'AFFC', 'Seat of House Blackmont in the Red Mountains.', seat='Blackmont'),
    G('Wyl', 'castle', ('at', 150, -2125), *D, 'AFFC', 'Seat of House Wyl at the Dornish end of the Boneway.', seat='Wyl'),
    G('High Hermitage', 'castle', ('near', 'Starfall', 'E', 40), *D, 'AFFC', 'Seat of a branch of House Dayne.', seat='Dayne'),
    G('Sandstone', 'castle', ('at', 0, -2350), *D, 'AFFC', 'Seat of House Qorgyle in the sands.', seat='Qorgyle'),
    G('The Prince\'s Pass', 'landmark', ('at', -140, -2170), *D, 'AFFC', 'The pass through the Red Mountains from the Reach into Dorne.'),
    G('The Tower of the Sun', 'tower', ('in', 'Sunspear', 0.3, 0.4), *D, 'AFFC', 'The great domed tower of Sunspear.', grade='text'),
    G('The Spear Tower', 'tower', ('in', 'Sunspear', -0.4, 0.2), *D, 'AFFC', 'The slender tower of Sunspear, tipped with a gilded spear.', grade='text'),
    G('The Shadow City', 'landmark', ('in', 'Sunspear', -1.5, -0.8), *D, 'AFFC', 'The town of mud-brick and sandstone in the shadow of Sunspear\'s walls.', grade='text'),
]


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
    return new, moved
