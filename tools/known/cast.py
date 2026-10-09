"""The Known World's cast: profiles, sprites, journeys, travel modes, scenes and events (used by author.py).

LAWS: facts from the novels in our own words; looks from the text's descriptions (never an actor); the novels
rarely give a day, so every date here is an estimate and the app says so. Places are referred to by name
(author.PLACES) or as [X, Y] in miles from Winterfell; legs follow the authored roads or sea lanes.
"""
import math, re

MOON = 30


def T(s):
    """'Y M D' (AC; D may be fractional) -> days from the start of 1 AC; a whole day is noon."""
    y, m, *d = s.split(); d = float(d[0]) if d else 1.0
    y, m = int(y), int(m); di = math.floor(d); fr = d - di
    return (y - 1 if y > 0 else y) * 365 + (m - 1) * MOON + (di - 1) + (fr or 0.5)


# ------------------------------------------------------------------ the people
# tier: primary | secondary | sidekick | mysterious ; head (C) and body (B) follow avatars.js parts
def H(name, skin, hair, style, **kw): d = {'name': name, 'skin': skin, 'hair': hair, 'style': style}; d.update(kw); return d
BLACK = ['#1e1a1a', '#0e0c0c']; DARK = ['#3a2a22', '#22180f']; AUBURN = ['#a2482a', '#6e2e18']; GOLD = ['#f0d070', '#c8a848']
SILVER = ['#f2eedc', '#cfc8b0']; BROWN = ['#6b4526', '#4a2f19']; GREY = ['#9a9690', '#6a6660']; RED = ['#c03a1e', '#8a2412']; STRAW = ['#e8d48a', '#b8a460']

CHARS = {
    # the Starks and their wolves
    'eddard': dict(tier='primary', house='Stark', head=H('Eddard Stark', '#e8c0a0', ['#4a3a30', '#2e241e'], 'short', beard='short', beardC=['#4a3a30', '#2e241e'], brows=1),
                   body=dict(tunic='#5a5e66', legs='#3a3a3e', cloak='#8a8e96', boots='#2a1f18', belt='#c8ccd4', gear='sword'),
                   bio='Lord of Winterfell and Warden of the North, who goes south as the King\'s Hand.', fate='Executed in King\'s Landing (AGOT).'),
    'catelyn': dict(tier='primary', house='Stark (born Tully)', head=H('Catelyn Stark', '#f4d6c0', AUBURN, 'long'),
                    body=dict(robe='#4a5a8a', belt='#a02020'), bio='Lady of Winterfell, born a Tully of Riverrun; she rides and sails to protect her children.', fate='Slain at the Red Wedding (ASOS).'),
    'robb': dict(tier='primary', house='Stark', head=H('Robb Stark', '#efc8a8', AUBURN, 'short', beard='stubble', beardC=AUBURN),
                 body=dict(tunic='#6a6e76', legs='#3a3a3e', cloak='#8a7a66', boots='#2a1f18', belt='#c8ccd4', gear='sword', mail=1),
                 bio='Eldest son of Winterfell; called King in the North when he takes the field.', fate='Slain at the Red Wedding (ASOS).'),
    'robbking': dict(tier='hidden', house='Stark', head=H('Robb, King in the North', '#efc8a8', AUBURN, 'short', beard='stubble', beardC=AUBURN, hat='crown', hatC=['#a07a40', '#6a4e28']),
                     body=dict(tunic='#6a6e76', legs='#3a3a3e', cloak='#8a7a66', boots='#2a1f18', belt='#c8ccd4', gear='sword', mail=1)),
    'sansa': dict(tier='primary', house='Stark', head=H('Sansa Stark', '#f6dcc8', AUBURN, 'long'), body=dict(robe='#7aa0d0', belt='#e8e0c8'),
                  bio='Elder daughter of Winterfell, held at court in King\'s Landing until she escapes to the Vale.'),
    'arya': dict(tier='primary', house='Stark', head=H('Arya Stark', '#e8c0a0', ['#5a4030', '#3a2a1e'], 'short', brows=1),
                 body=dict(tunic='#6a5a46', legs='#4a3e32', boots='#2a1f18', belt='#3a2a1e', gear='sword'),
                 bio='Younger daughter of Winterfell, sword in hand, who flees the capital and crosses the narrow sea to Braavos.'),
    'bran': dict(tier='primary', house='Stark', head=H('Bran Stark', '#f0c8a8', AUBURN, 'short', blush=1), body=dict(tunic='#6a6e76', legs='#3a3a3e', boots='#2a1f18'),
                 bio='A boy who falls from a tower, cannot walk, and is carried north beyond the Wall to the three-eyed crow.'),
    'rickon': dict(tier='secondary', house='Stark', head=H('Rickon Stark', '#f2ccac', AUBURN, 'shaggy', blush=1), body=dict(tunic='#5a5e66', legs='#3a3a3e', boots='#2a1f18'),
                   bio='The youngest Stark, taken into hiding by the wildling Osha.'),
    'jon': dict(tier='primary', house='Stark (the Night\'s Watch)', head=H('Jon Snow', '#e8c0a0', BLACK, 'shaggy', brows=1),
                body=dict(tunic='#1e1e22', legs='#16161a', cloak='#121216', boots='#141010', belt='#2a2a2e', gear='sword'),
                bio='Lord Eddard\'s bastard son, who takes the black at the Wall and rises to lead the Night\'s Watch.'),
    'ghost': dict(tier='sidekick', house='Stark', wolf=dict(fur=['#f4f4f0', '#c8c8c4'], eye='#c81818'), bio='Jon\'s direwolf: white, silent, with red eyes.'),
    'greywind': dict(tier='sidekick', house='Stark', wolf=dict(fur=['#8a8e96', '#5a5e66'], eye='#e8c040'), bio='Robb\'s direwolf, grey as smoke.', fate='Killed at the Red Wedding (ASOS).'),
    'lady': dict(tier='sidekick', house='Stark', wolf=dict(fur=['#c8ccd4', '#9a9ea8'], eye='#e8c040'), bio='Sansa\'s gentle direwolf.', fate='Killed on the king\'s order on the road south (AGOT).'),
    'nymeria': dict(tier='sidekick', house='Stark', wolf=dict(fur=['#8a7a66', '#5a4e40'], eye='#e8c040'), bio='Arya\'s direwolf, driven off near the Trident; she runs with a great wolf pack in the riverlands.'),
    'summer': dict(tier='sidekick', house='Stark', wolf=dict(fur=['#b8b8b0', '#8a8a84'], eye='#e8b030'), bio='Bran\'s direwolf, whose eyes Bran learns to see through.'),
    'shaggydog': dict(tier='sidekick', house='Stark', wolf=dict(fur=['#1e1c1c', '#0e0c0c'], eye='#60d060'), bio='Rickon\'s direwolf, black and wild.'),
    # the Night's Watch and the North
    'samwell': dict(tier='secondary', house='Tarly (the Night\'s Watch)', head=H('Samwell Tarly', '#f2d0b4', BROWN, 'short', blush=1),
                    body=dict(tunic='#1e1e22', legs='#16161a', cloak='#121216', boots='#141010', fat=1), bio='Jon\'s friend at the Wall, a reader who goes south to the Citadel.'),
    'theon': dict(tier='primary', house='Greyjoy', head=H('Theon Greyjoy', '#e8c0a0', DARK, 'shaggy', beard='stubble', beardC=DARK),
                  body=dict(tunic='#2a2a2a', legs='#1e1e1e', cloak='#c9a03c', boots='#141010', gear='bow'),
                  bio='Ward of Winterfell and heir of the Iron Islands, who takes Winterfell and is broken by the Boltons.'),
    'reek': dict(tier='hidden', house='Greyjoy', head=H('Reek', '#d8c8b8', ['#e8e4dc', '#b8b2a6'], 'sparse'), body=dict(tunic='#5a5048', legs='#4a4038', rags=1)),
    'hodor': dict(tier='sidekick', house='Winterfell', head=H('Hodor', '#e8c0a0', BROWN, 'shaggy', beard='stubble', beardC=BROWN), body=dict(tunic='#6a5a46', legs='#4a3e32', boots='#2a1f18'),
                  bio='The huge, gentle stableboy who carries Bran.'),
    'meera': dict(tier='sidekick', house='Reed', head=H('Meera Reed', '#e0b896', BROWN, 'long'), body=dict(tunic='#4a6a3a', legs='#3a4a2a', boots='#2a1f18', gear='staff', staff='#7a5a3a'),
                  bio='A crannogwoman of the Neck, Bran\'s guardian on the road north.'),
    'jojen': dict(tier='sidekick', house='Reed', head=H('Jojen Reed', '#e0b896', BROWN, 'short'), body=dict(tunic='#4a6a3a', legs='#3a4a2a', boots='#2a1f18'),
                  bio='Meera\'s brother, who dreams true and leads Bran north.'),
    'osha': dict(tier='sidekick', house='the free folk', head=H('Osha', '#e0b896', BROWN, 'long'), body=dict(tunic='#6a5a46', legs='#4a3e32', rags=1, gear='staff', staff='#6b4a2a'),
                 bio='A wildling woman captured at Winterfell who protects Rickon.'),
    # the Lannisters and the court
    'tyrion': dict(tier='primary', house='Lannister', head=H('Tyrion Lannister', '#f0d0b4', ['#f0e6c0', '#cbbf96'], 'shaggy', brows=1),
                   body=dict(tunic='#8a1a1a', legs='#3a2a22', boots='#2a1f18', belt='#e8c060'),
                   bio='A dwarf of keen wit, son of Tywin; Hand of the King in the war, then a fugitive across the narrow sea.'),
    'cersei': dict(tier='primary', house='Lannister', head=H('Cersei Lannister', '#f6dcc8', GOLD, 'long', hat='crown', hatC=['#f0d060', '#c0a030']),
                   body=dict(robe='#a0201e', belt='#e8c060'), bio='Queen to King Robert, mother of Joffrey, and the power behind the Iron Throne.'),
    'jaime': dict(tier='primary', house='Lannister (the Kingsguard)', head=H('Jaime Lannister', '#f2d4b6', GOLD, 'short', beard='stubble', beardC=GOLD),
                  body=dict(tunic='#e8e4dc', legs='#c8c4bc', cloak='#f4f2ec', boots='#8a7a60', belt='#e8c060', gear='sword', mail=1),
                  bio='Cersei\'s twin and a knight of the Kingsguard, captured in the war, who loses his sword hand on the road south.'),
    'tywin': dict(tier='secondary', house='Lannister', head=H('Tywin Lannister', '#ecc8a8', ['#c8b070', '#9a8650'], 'sides', beard='short', beardC=['#c8b070', '#9a8650'], brows=1),
                  body=dict(robe='#8a1a1a', belt='#e8c060'), bio='Lord of Casterly Rock, the realm\'s most feared commander.', fate='Killed by Tyrion (ASOS).'),
    'robert': dict(tier='secondary', house='Baratheon', head=H('King Robert', '#e8b896', BLACK, 'short', beard='short', beardC=BLACK, hat='crown', hatC=['#d8b830', '#a88a20']),
                   body=dict(tunic='#d8b830', legs='#3a3028', boots='#2a1f18', belt='#1e1a1a', fat=1), bio='King of the Seven Kingdoms, Ned Stark\'s old friend.', fate='Killed by a boar on a hunt (AGOT).'),
    'joffrey': dict(tier='secondary', house='Baratheon (Lannister)', head=H('Joffrey', '#f6dcc8', GOLD, 'short', hat='crown', hatC=['#f0d060', '#c0a030']),
                    body=dict(tunic='#a0201e', legs='#3a2a22', boots='#2a1f18', belt='#e8c060'), bio='Robert\'s heir, a cruel boy king.', fate='Poisoned at his wedding feast (ASOS).'),
    'bronn': dict(tier='sidekick', house='sellsword', head=H('Bronn', '#d8a882', BLACK, 'short', beard='stubble', beardC=BLACK),
                  body=dict(tunic='#5a4a3a', legs='#3a3028', boots='#2a1f18', gear='sword', mail=1), bio='A sellsword who fights for Tyrion and rises with him.'),
    'podrick': dict(tier='sidekick', house='Payne', head=H('Podrick Payne', '#f0c8a8', BROWN, 'shaggy'), body=dict(tunic='#8a1a1a', legs='#3a2a22', boots='#2a1f18'),
                    bio='Tyrion\'s shy squire, later Brienne\'s.'),
    'sandor': dict(tier='secondary', house='Clegane', head=H('Sandor Clegane, the Hound', '#c89a7a', BLACK, 'shaggy', brows=1, hat='helm', hatC=['#6a6a70', '#4a4a50']),
                   body=dict(tunic='#4a3a2a', legs='#2a2a2e', cloak='#3a3028', boots='#1a1410', gear='sword', mail=1),
                   bio='Joffrey\'s scarred sworn shield, who deserts at the Blackwater and takes Arya.'),
    'littlefinger': dict(tier='mysterious', house='Baelish', head=H('Petyr Baelish', '#ecc8a8', DARK, 'short', beard='short', beardC=DARK),
                         body=dict(tunic='#2a4a3a', legs='#1e2a24', cloak='#3a5a4a', boots='#1a1410', belt='#c8ccd4'),
                         bio='Master of coin and a schemer in every court, who carries Sansa off to the Vale.'),
    'varys': dict(tier='mysterious', house='the Spider', head=H('Varys', '#f0d8c4', ['#f0d8c4', '#e0c8b4'], 'sparse'), body=dict(robe='#6a4a7a', fat=1),
                  bio='The eunuch master of whisperers, whose little birds are everywhere.'),
    'margaery': dict(tier='secondary', house='Tyrell', head=H('Margaery Tyrell', '#f4d8c0', BROWN, 'curly'), body=dict(robe='#5a9a4a', belt='#e8c060'),
                     bio='Of Highgarden; wed to Renly, then to the crown.'),
    'brienne': dict(tier='primary', house='Tarth', head=H('Brienne of Tarth', '#ecc4a4', STRAW, 'short', brows=1),
                    body=dict(tunic='#4a6aa0', legs='#3a3a3e', cloak='#4a6aa0', boots='#2a1f18', gear='sword', mail=1),
                    bio='A towering knightly woman sworn to Catelyn, who brings Jaime south and searches for the Stark girls.'),
    'gendry': dict(tier='sidekick', house='the forge', head=H('Gendry', '#e8c0a0', BLACK, 'shaggy', brows=1), body=dict(tunic='#5a4030', legs='#3a3028', boots='#2a1f18', gear='axe'),
                   bio='A smith\'s apprentice who flees north with Arya.'),
    'hotpie': dict(tier='sidekick', house='the road', head=H('Hot Pie', '#f0c8a8', BROWN, 'short', blush=1), body=dict(tunic='#8a7050', legs='#4a3e32', fat=1),
                   bio='A baker\'s boy on Arya\'s road, who stays behind at an inn.'),
    # Stannis and the red woman
    'stannis': dict(tier='secondary', house='Baratheon', head=H('Stannis Baratheon', '#e8c0a0', BLACK, 'sides', beard='short', beardC=BLACK, brows=1, hat='crown', hatC=['#c84020', '#8a2a14']),
                    body=dict(tunic='#3a3a40', legs='#2a2a2e', cloak='#d8b830', boots='#1a1410', gear='sword', mail=1), bio='Robert\'s stern brother, who claims the throne from Dragonstone.'),
    'davos': dict(tier='secondary', house='Seaworth', head=H('Davos Seaworth', '#d8a882', GREY, 'short', beard='short', beardC=GREY), body=dict(tunic='#4a4a5a', legs='#2a2a2e', boots='#1a1410'),
                  bio='The Onion Knight, a smuggler raised by Stannis, who sails wherever he is sent.'),
    'melisandre': dict(tier='mysterious', house='the Lord of Light', head=H('Melisandre', '#f4d8c8', ['#c01818', '#800c0c'], 'long', eye='#ff2020'), body=dict(robe='#c01818', belt='#ffd040'),
                       bio='The red priestess at Stannis\'s side, who sees visions in flames.'),
    # across the narrow sea
    'daenerys': dict(tier='primary', house='Targaryen', head=H('Daenerys Targaryen', '#f6e0d0', SILVER, 'long', eye='#8a5ac8'), body=dict(robe='#d8c8b0', belt='#c9a03c'),
                     bio='The last Targaryen princess, wed to a khal, mother of three dragons, queen in Meereen.'),
    'viserys': dict(tier='secondary', house='Targaryen', head=H('Viserys Targaryen', '#f4dccc', SILVER, 'short', eye='#8a5ac8'), body=dict(tunic='#4a1a1a', legs='#2a1414', boots='#1a1010'),
                    bio='Daenerys\'s brother, who sells her to Drogo for an army.', fate='Crowned with molten gold in Vaes Dothrak (AGOT).'),
    'drogo': dict(tier='secondary', house='the Dothraki', head=H('Khal Drogo', '#b07850', BLACK, 'long'), body=dict(tunic='#8a6040', legs='#5a4030', boots='#3a2a1e', belt='#c9a03c', gear='sword'),
                  bio='A great khal of the Dothraki, Daenerys\'s husband.', fate='Dies of a festering wound in Lhazar (AGOT).'),
    'jorah': dict(tier='secondary', house='Mormont', head=H('Jorah Mormont', '#e8c0a0', DARK, 'sides', beard='short', beardC=DARK),
                  body=dict(tunic='#3a5a3a', legs='#2a3a2a', boots='#1a1410', gear='sword', mail=1), bio='An exiled northern knight who serves Daenerys.'),
    'missandei': dict(tier='sidekick', house='Naath', head=H('Missandei', '#8a5a3a', ['#2a1e18', '#140e0a'], 'curly'), body=dict(robe='#f0ece0'),
                      bio='A young scribe from Astapor who becomes Daenerys\'s voice.'),
    'barristan': dict(tier='secondary', house='Selmy (the Kingsguard)', head=H('Barristan Selmy', '#ecc8a8', SILVER, 'short', beard='short', beardC=SILVER),
                      body=dict(tunic='#e8e4dc', legs='#c8c4bc', cloak='#f4f2ec', boots='#8a7a60', gear='sword', mail=1), bio='The old Lord Commander of the Kingsguard, who finds Daenerys and serves her.'),
    'drogon': dict(tier='sidekick', house='Targaryen', dragon=['#1e1416', '#0e0a0a', '#8a1a14'], bio='The largest of the three dragons, black and red.'),
    'rhaegal': dict(tier='sidekick', house='Targaryen', dragon=['#2e6a3a', '#1a4024', '#b08030'], bio='The green and bronze dragon.'),
    'viserion': dict(tier='sidekick', house='Targaryen', dragon=['#e8dcb8', '#b8a880', '#c9a03c'], bio='The cream and gold dragon.'),
    'quaithe': dict(tier='mysterious', house='Asshai', head=H('Quaithe', '#7a1a2a', ['#2a1218', '#140a0c'], 'long', hood=1), body=dict(robe='#3a1a2a'),
                    bio='A masked shadowbinder of Asshai who speaks riddles to Daenerys in Qarth.'),
    'griff': dict(tier='mysterious', house='Connington', head=H('Griff', '#e8c0a0', ['#3a5a9a', '#24407a'], 'short', beard='short', beardC=['#3a5a9a', '#24407a']),
                  body=dict(tunic='#4a4a4a', legs='#2a2a2e', cloak='#5a4a3a', boots='#1a1410', gear='sword', mail=1), bio='A sellsword captain on the Rhoyne with a hidden past, guarding a young man with blue-dyed hair.'),
    # the dark and the mysterious
    'others': dict(tier='mysterious', house='beyond the Wall', head=H('The Others', '#cfe6f4', ['#f0f8ff', '#c8dcec'], 'long', eye='#4ab8ff'),
                   body=dict(robe='#dff0fa', gear='sword'), bio='Pale shapes from the far north, cold as ice, that move again as the long summer ends.'),
    'coldhands': dict(tier='mysterious', house='beyond the Wall', head=H('Coldhands', '#3a4a50', ['#121216', '#08080a'], 'short', hood=1), body=dict(robe='#121216'),
                      bio='A cloaked rider in black whose hands are cold, who guides travellers through the haunted wood.'),
    'threeeyed': dict(tier='mysterious', house='the cave', head=H('The three-eyed crow', '#ece8e0', ['#f4f4f0', '#c8c8c4'], 'long', eye='#c01818'), body=dict(robe='#2a1e18'),
                      bio='An ancient greenseer sitting among weirwood roots in a cave far north, who calls Bran to him.'),
    'jaqen': dict(tier='mysterious', house='Lorath', head=H('Jaqen H\'ghar', '#ecc8a8', ['#b03020', '#f0f0f0'], 'long'), body=dict(tunic='#5a5a60', legs='#3a3a3e', boots='#1a1410'),
                  bio='A prisoner Arya saves on the road, who repays her with three deaths and a coin.'),
    'ramsay': dict(tier='mysterious', house='Bolton', head=H('Ramsay Bolton', '#f0d8cc', DARK, 'short'), body=dict(tunic='#c08080', legs='#3a2a2a', cloak='#c08080', boots='#1a1010', gear='sword'),
                   bio='Lord Bolton\'s cruel bastard, master of the Dreadfort\'s dogs.'),
    'benjen': dict(tier='mysterious', house='Stark (the Night\'s Watch)', head=H('Benjen Stark', '#e8c0a0', ['#4a3a30', '#2e241e'], 'short', beard='stubble', beardC=['#4a3a30', '#2e241e']),
                   body=dict(tunic='#1e1e22', legs='#16161a', cloak='#121216', boots='#141010', gear='sword'), bio='First Ranger of the Night\'s Watch, who rides beyond the Wall and does not come back.'),
    'mance': dict(tier='secondary', house='the free folk', head=H('Mance Rayder', '#e0b896', DARK, 'long', beard='short', beardC=DARK),
                  body=dict(tunic='#4a3a2a', legs='#2a2a2e', cloak='#8a2020', boots='#1a1410'), bio='King-beyond-the-Wall, a deserter of the Watch who unites the free folk.'),
    'ygritte': dict(tier='secondary', house='the free folk', head=H('Ygritte', '#f0ccb0', RED, 'long'), body=dict(tunic='#8a7a66', legs='#5a4e40', boots='#3a2a1e', gear='bow'),
                    bio='A free folk spearwife, kissed by fire, who loves Jon.', fate='Killed at the attack on Castle Black (ASOS).'),
    'tormund': dict(tier='secondary', house='the free folk', head=H('Tormund', '#e8b896', RED, 'shaggy', beard='short', beardC=RED), body=dict(tunic='#8a7a66', legs='#5a4e40', boots='#3a2a1e', fat=1, gear='axe'),
                    bio='A boastful wildling chief and Mance\'s right hand.'),
    'craster': dict(tier='mysterious', house='beyond the Wall', head=H('Craster', '#d8b896', GREY, 'sparse', beard='short', beardC=GREY), body=dict(tunic='#6a5a46', legs='#4a3e32', rags=1),
                    bio='A wildling who keeps a grim holdfast and trades with the Watch.'),
    'gilly': dict(tier='sidekick', house='beyond the Wall', head=H('Gilly', '#f0ccb0', BROWN, 'long'), body=dict(tunic='#8a7a66', legs='#5a4e40', rags=1),
                  bio='Craster\'s daughter, who flees with Sam and a babe.'),
}

# ------------------------------------------------------------------ roads and sea lanes for legs
SEA = {  # sea lanes as [X, Y] waypoints (open water)
    'white-harbor-kl': [[190, -272], [300, -330], [560, -430], [640, -700], [640, -1000], [520, -1180], [300, -1250], [250, -1300]],
    'gulltown-white-harbor': [[522, -860], [620, -780], [620, -450], [190, -272]],
    'seagard-pyke': [[-110, -690], [-220, -720], [-322, -748]],
    'pyke-stony-shore': [[-322, -748], [-420, -620], [-480, -380], [-440, -250]],
    'qarth-astapor': [[3410, -2590], [3200, -2720], [2700, -2650], [2400, -2400], [2452, -2150]],
    'dragonstone-kl': [[400, -1192], [400, -1205], [385, -1224], [330, -1230], [250, -1300]],
    'dragonstone-eastwatch': [[400, -1192], [640, -800], [520, 120], [400, 400], [157, 458]],
    'eastwatch-white-harbor': [[157, 458], [300, 470], [480, 200], [560, -200], [190, -272]],
    'eastwatch-braavos': [[157, 458], [300, 480], [560, 100], [640, -300], [720, -420], [735, -470], [745, -480], [770, -480]],
    'braavos-oldtown': [[770, -480], [752, -512], [700, -2100], [624, -2392], [-100, -2700], [-470, -2160], [-430, -2120]],
    'kl-pentos': [[250, -1300], [330, -1260], [520, -1180], [700, -1120], [780, -1120], [794, -1120]],
    'volantis-meereen': [[1420, -2200], [1600, -2700], [2100, -2600], [2400, -2380], [2600, -2150], [2690, -1980]],
    'saltpans-braavos': [[324, -927], [330, -930], [620, -880], [640, -600], [720, -420], [735, -470], [745, -480], [770, -480]],
    'kl-fingers': [[250, -1300], [330, -1250], [520, -1150], [630, -800], [585, -560], [536, -584]],
    'pentos-qarth': [[794, -1120], [780, -1120], [984, -1856], [1064, -1992], [1128, -2072], [1700, -2672], [1790, -2672], [2700, -2650], [3200, -2720], [3410, -2590]],
    'dragonstone-storms-end': [[400, -1192], [400, -1208], [464, -1384], [384, -1560], [374, -1576]],
    'tarth-mainland': [[562, -1520], [376, -1560]],
    'volon-therys-cape-wrath': [[1300, -2150], [1272, -2144], [936, -2048], [554, -1699]],
    'bay-of-seals-skagos': [[322, 365], [352, 472], [350, 500]],
}


# ------------------------------------------------------------------ journeys: [point, date] with point = place | [X, Y]
# legs: ('via', road or lane name, from, to, date0, date1) expand along the road or sea lane
def J(*steps): return list(steps)
ROAD = lambda road, a, b, d0, d1: ('road', road, a, b, d0, d1)
LANE = lambda lane, d0, d1, back=False: ('lane', lane, d0, d1, back)

# the march from Astapor to Yunkai and on to Meereen, overland round the bay
SLAVERS = (('Astapor', '299 8 20'), ([2536, -2072], '299 9 13'), ('Yunkai', '299 9 20'), ([2576, -2032], '299 10 13'), ([2656, -1976], '299 12 29'), ('Meereen', '300 2 1'))
# the king's progress home, which the Starks of the south road share
SOUTH = (ROAD('The Kingsroad', 'Winterfell', 'The Inn at the Crossroads', '298 2 20', '298 3 14'), ('Darry', '298 3 16'), ROAD('The Kingsroad', 'Darry', 'King\'s Landing', '298 3 17', '298 4 1'))
PATHS = {
    'eddard': J(('Winterfell', '297 13 1'), ('Winterfell', '298 2 20'), ROAD('The Kingsroad', 'Winterfell', 'The Inn at the Crossroads', '298 2 20', '298 3 14'),
                ('Darry', '298 3 16'), ROAD('The Kingsroad', 'Darry', 'King\'s Landing', '298 3 17', '298 4 1'), ('King\'s Landing', '298 8 1')),
    'catelyn': J(('Winterfell', '297 13 1'), ('Winterfell', '298 2 25'), ('White Harbor', '298 3 3'), LANE('white-harbor-kl', '298 3 4', '298 3 20'),
                 ('King\'s Landing', '298 4 2'), ROAD('The Kingsroad', 'King\'s Landing', 'The Inn at the Crossroads', '298 4 3', '298 5 20'),
                 ROAD('The High Road', 'The Inn at the Crossroads', 'The Eyrie', '298 5 21', '298 6 10'), ('The Eyrie', '298 6 28'), ('Gulltown', '298 7 4'),
                 LANE('gulltown-white-harbor', '298 7 5', '298 7 16'), ('Moat Cailin', '298 7 26'), ('The Twins', '298 8 6'), ('Riverrun', '298 8 22'),
                 ('Riverrun', '299 1 20'), ('Bitterbridge', '299 2 20'), ('Storm\'s End', '299 4 5'), ('Riverrun', '299 5 10'), ('Riverrun', '299 8 20'), ('The Twins', '299 9 1')),
    'robb': J(('Winterfell', '297 13 1'), ('Winterfell', '298 7 1'), ROAD('The Kingsroad', 'Winterfell', 'Moat Cailin', '298 7 2', '298 7 20'), ('The Twins', '298 8 5'),
              ('The Whispering Wood', '298 8 15'), ('Riverrun', '298 8 18'), ('Riverrun', '299 2 15'), ('The Golden Tooth', '299 2 25'), ('Oxcross', '299 3 5'), ('The Crag', '299 3 22'),
              ('Riverrun', '299 6 15'), ('Seagard', '299 8 20'), ('The Twins', '299 9 1')),
    'sansa': J(('Winterfell', '297 13 1'), ('Winterfell', '298 2 20'), ROAD('The Kingsroad', 'Winterfell', 'The Inn at the Crossroads', '298 2 20', '298 3 14'), ('Darry', '298 3 16'),
               ROAD('The Kingsroad', 'Darry', 'King\'s Landing', '298 3 17', '298 4 1'), ('King\'s Landing', '300 1 15'), LANE('kl-fingers', '300 1 16', '300 2 5'),
               ('The Eyrie', '300 2 15'), ('The Eyrie', '300 6 1'), ('Gates of the Moon', '300 6 10'), ('Gates of the Moon', '300 13 5')),
    'arya': J(('Winterfell', '297 13 1'), ('Winterfell', '298 2 20'), SOUTH[0], ('Darry', '298 3 16'),
              ROAD('The Kingsroad', 'Darry', 'King\'s Landing', '298 3 17', '298 4 1'), ('King\'s Landing', '298 8 2'), ROAD('The Kingsroad', 'King\'s Landing', 'The Inn at the Crossroads', '298 8 3', '298 12 20'),
              ([120, -940], '299 1 10'), ('Harrenhal', '299 2 1'), ('Harrenhal', '299 4 15'), ([40, -1010], '299 5 10'), ('Acorn Hall', '299 6 10'), ('Stoney Sept', '299 7 1'),
              ([60, -930], '299 8 1'), ('The Twins', '299 9 1'), ([200, -820], '299 10 20'), ([110, -880], '299 12 10'), ('Saltpans', '300 1 5'), LANE('saltpans-braavos', '300 1 6', '300 2 1'),
              ('The House of Black and White', '300 2 3'), ('The House of Black and White', '300 13 5')),
    'bran': J(('Winterfell', '297 13 1'), ('Winterfell', '299 5 1'), ([-30, 120], '299 5 20'), ([60, 300], '299 7 15'), ('Queenscrown', '299 8 1'), ('The Nightfort', '299 9 1'),
              ([-30, 520], '299 9 10'), ([-20, 700], '299 12 1'), ([20, 880], '300 2 1'), ('The cave of the three-eyed crow', '300 4 1'), ('The cave of the three-eyed crow', '300 13 5')),
    'rickon': J(('Winterfell', '297 13 1'), ('Winterfell', '299 5 1'), ([200, 120], '299 5 25'), ([322, 365], '299 9 1'), ([322, 365], '299 11 20'), LANE('bay-of-seals-skagos', '299 11 21', '299 12 1'), ('Skagos', '300 13 5')),
    'jon': J(('Winterfell', '297 13 1'), ('Winterfell', '298 2 20'), ROAD('The Kingsroad', 'Winterfell', 'Castle Black', '298 2 20', '298 3 20'), ('Castle Black', '299 1 1'),
             ('Craster\'s Keep', '299 1 20'), ('The Fist of the First Men', '299 2 5'), ('The Skirling Pass', '299 3 20'), ([-150, 700], '299 5 1'), ([-60, 520], '299 7 20'),
             ('Queenscrown', '299 8 1'), ('Castle Black', '299 8 20'), ('Castle Black', '300 13 5')),
    'samwell': J(('Horn Hill', '297 12 1'), ROAD('The Roseroad', 'Horn Hill', 'King\'s Landing', '297 12 2', '297 12 20'), ROAD('The Kingsroad', 'King\'s Landing', 'Castle Black', '297 12 21', '298 3 25'),
                 ('Castle Black', '299 1 1'), ('Craster\'s Keep', '299 1 20'), ('The Fist of the First Men', '299 2 5'), ('Craster\'s Keep', '299 6 1'), ([-30, 560], '299 8 20'),
                 ('The Nightfort', '299 9 1'), ('Castle Black', '299 9 10'), ('Castle Black', '300 3 20'), ('Eastwatch-by-the-Sea', '300 4 1'), LANE('eastwatch-braavos', '300 4 2', '300 5 1'),
                 ('Braavos', '300 6 10'), LANE('braavos-oldtown', '300 6 11', '300 8 1'), ('The Citadel', '300 8 2'), ('The Citadel', '300 13 5')),
    'theon': J(('Winterfell', '297 13 1'), ('Winterfell', '298 7 1'), ROAD('The Kingsroad', 'Winterfell', 'Moat Cailin', '298 7 2', '298 7 20'), ('The Twins', '298 8 5'),
               ('The Whispering Wood', '298 8 15'), ('Riverrun', '298 8 18'), ('Riverrun', '299 1 5'), ('Seagard', '299 1 15'), LANE('seagard-pyke', '299 1 16', '299 1 22'),
               ('Pyke', '299 2 25'), LANE('pyke-stony-shore', '299 2 26', '299 3 12'), ([-420, -170], '299 3 15'), ('Torrhen\'s Square', '299 3 25'), ('Winterfell', '299 4 1'),
               ('Winterfell', '299 6 1'), ('The Dreadfort', '299 6 12'), ('The Dreadfort', '300 1 20'), ('Moat Cailin', '300 2 10'), ('Barrowton', '300 3 20'), ('Winterfell', '300 6 1'),
               ('Winterfell', '300 9 1'), ([-40, 30], '300 9 4'), ([-120, 40], '300 9 20'), ([-120, 40], '300 13 5')),
    'tyrion': J(('King\'s Landing', '297 12 1'), ROAD('The Kingsroad', 'King\'s Landing', 'Winterfell', '297 12 2', '298 2 1'), ('Winterfell', '298 2 20'),
                ROAD('The Kingsroad', 'Winterfell', 'Castle Black', '298 2 20', '298 3 20'), ('Castle Black', '298 4 5'), ROAD('The Kingsroad', 'Castle Black', 'Winterfell', '298 4 5', '298 4 25'),
                ROAD('The Kingsroad', 'Winterfell', 'The Inn at the Crossroads', '298 4 26', '298 5 20'), ROAD('The High Road', 'The Inn at the Crossroads', 'The Eyrie', '298 5 21', '298 6 10'),
                ('The Eyrie', '298 6 24'), ([240, -820], '298 7 20'), ([150, -800], '298 8 8'), ([130, -830], '298 8 14'), ('Harrenhal', '298 8 26'), ('Harrenhal', '298 12 20'),
                ROAD('The Kingsroad', 'The Inn at the Crossroads', 'King\'s Landing', '298 12 22', '299 1 5'), ('King\'s Landing', '300 2 10'), LANE('kl-pentos', '300 2 11', '300 3 5'),
                ('Pentos', '300 3 20'), ([1150, -850], '300 4 10'), ('Chroyane', '300 4 25'), ('Selhorys', '300 5 5'), ('Volantis', '300 5 20'), LANE('volantis-meereen', '300 6 1', '300 7 20'), ([2656, -1976], '300 7 21'),
                ([2600, -1990], '300 8 1'), ([2600, -1990], '300 13 5')),
    'cersei': J(('King\'s Landing', '297 12 1'), ROAD('The Kingsroad', 'King\'s Landing', 'Winterfell', '297 12 2', '298 2 1'), ('Winterfell', '298 2 20'),
                *SOUTH, ('King\'s Landing', '300 13 5')),
    'jaime': J(('King\'s Landing', '297 12 1'), ROAD('The Kingsroad', 'King\'s Landing', 'Winterfell', '297 12 2', '298 2 1'), ('Winterfell', '298 2 20'),
               *SOUTH, ('King\'s Landing', '298 5 25'), ('Casterly Rock', '298 6 25'), ('The Golden Tooth', '298 7 10'),
               ('Riverrun', '298 8 1'), ('The Whispering Wood', '298 8 15'), ('Riverrun', '298 8 18'), ('Riverrun', '299 7 1'), ([70, -890], '299 7 10'), ([180, -940], '299 8 5'),
               ('Harrenhal', '299 9 10'), ('Harrenhal', '299 11 1'), ROAD('The Kingsroad', 'The Inn at the Crossroads', 'King\'s Landing', '299 11 3', '300 1 1'), ('King\'s Landing', '300 5 15'),
               ('Riverrun', '300 7 1'), ('Raventree Hall', '300 8 15'), ('Raventree Hall', '300 13 5')),
    'tywin': J(('Casterly Rock', '297 13 1'), ('Casterly Rock', '298 5 20'), ('The Golden Tooth', '298 6 15'), ([150, -800], '298 8 8'), ([130, -830], '298 8 14'), ('Harrenhal', '298 8 26'), ('Harrenhal', '299 4 1'),
               ([-100, -1150], '299 5 15'), ('Bitterbridge', '299 5 25'), ('King\'s Landing', '299 6 1'), ('King\'s Landing', '300 2 10')),
    'robert': J(('King\'s Landing', '297 12 1'), ROAD('The Kingsroad', 'King\'s Landing', 'Winterfell', '297 12 2', '298 2 1'), ('Winterfell', '298 2 20'),
                *SOUTH, ('King\'s Landing', '298 5 10'), ('The Kingswood', '298 5 14')),
    'joffrey': J(('King\'s Landing', '297 12 1'), ROAD('The Kingsroad', 'King\'s Landing', 'Winterfell', '297 12 2', '298 2 1'), ('Winterfell', '298 2 20'),
                 *SOUTH, ('King\'s Landing', '300 1 15')),
    'bronn': J(('The Inn at the Crossroads', '298 5 20'), ROAD('The High Road', 'The Inn at the Crossroads', 'The Eyrie', '298 5 21', '298 6 10'), ('The Eyrie', '298 6 24'), ([240, -820], '298 7 5'),
               ([150, -800], '298 7 12'), ([130, -830], '298 7 15'), ('Harrenhal', '298 8 20'), ('Harrenhal', '298 12 20'), ROAD('The Kingsroad', 'The Inn at the Crossroads', 'King\'s Landing', '298 12 22', '299 1 5'),
               ('King\'s Landing', '300 3 1'), ([-150, -1250], '300 4 1'), ([-150, -1250], '300 13 5')),
    'podrick': J(('King\'s Landing', '299 1 10'), ('King\'s Landing', '300 3 1'), ('Rosby', '300 3 5'), ('Duskendale', '300 3 15'), ('Maidenpool', '300 4 10'), ('Saltpans', '300 5 10'), ([200, -920], '300 7 1'), ([200, -920], '300 13 5')),
    'sandor': J(('King\'s Landing', '297 12 1'), ROAD('The Kingsroad', 'King\'s Landing', 'Winterfell', '297 12 2', '298 2 1'), ('Winterfell', '298 2 20'),
                *SOUTH, ('King\'s Landing', '299 6 1'), ([160, -1200], '299 6 20'), ([60, -930], '299 8 1'),
                ('The Twins', '299 9 1'), ([200, -820], '299 10 20'), ([110, -880], '299 12 10'), ([200, -905], '300 1 1'), ('The Quiet Isle', '300 1 25'), ('The Quiet Isle', '300 13 5')),
    'littlefinger': J(('King\'s Landing', '297 13 1'), ('King\'s Landing', '299 2 1'), ('Bitterbridge', '299 2 20'), ('Highgarden', '299 3 10'), ('King\'s Landing', '299 6 5'),
                      ('King\'s Landing', '300 1 15'), LANE('kl-fingers', '300 1 16', '300 2 5'), ('The Eyrie', '300 2 15'), ('Gates of the Moon', '300 6 10'), ('Gates of the Moon', '300 13 5')),
    'varys': J(('King\'s Landing', '297 13 1'), ('King\'s Landing', '300 13 5')),
    'margaery': J(('Highgarden', '297 13 1'), ('Highgarden', '299 1 20'), ('Bitterbridge', '299 2 15'), ('Storm\'s End', '299 4 5'), ('Bitterbridge', '299 5 10'), ('King\'s Landing', '299 6 10'), ('King\'s Landing', '300 13 5')),
    'brienne': J(('Evenfall Hall', '297 13 1'), ('Evenfall Hall', '299 1 1'), LANE('tarth-mainland', '299 1 2', '299 1 4'), ('Bitterbridge', '299 2 15'), ('Storm\'s End', '299 4 5'), ('Riverrun', '299 5 10'), ('Riverrun', '299 7 1'),
                 ([70, -890], '299 7 10'), ([180, -940], '299 8 5'), ('Harrenhal', '299 9 10'), ('Harrenhal', '299 11 1'), ROAD('The Kingsroad', 'The Inn at the Crossroads', 'King\'s Landing', '299 11 3', '300 1 1'),
                 ('King\'s Landing', '300 3 1'), ('Rosby', '300 3 5'), ('Duskendale', '300 3 15'), ('Maidenpool', '300 4 10'), ('Saltpans', '300 5 10'), ('The Quiet Isle', '300 5 25'), ([200, -920], '300 7 1'), ([200, -920], '300 13 5')),
    'gendry': J(('King\'s Landing', '297 13 1'), ('King\'s Landing', '298 8 2'), ROAD('The Kingsroad', 'King\'s Landing', 'The Inn at the Crossroads', '298 8 3', '298 12 20'), ([120, -940], '299 1 10'),
                ('Harrenhal', '299 2 1'), ('Harrenhal', '299 4 15'), ([40, -1010], '299 5 10'), ('Acorn Hall', '299 6 10'), ('Stoney Sept', '299 7 1'), ([60, -930], '299 7 25'), ([200, -905], '299 8 10'), ([200, -905], '300 13 5')),
    'hotpie': J(('King\'s Landing', '298 8 2'), ROAD('The Kingsroad', 'King\'s Landing', 'The Inn at the Crossroads', '298 8 3', '298 12 20'), ([120, -940], '299 1 10'), ('Harrenhal', '299 2 1'),
                ('Harrenhal', '299 4 15'), ([40, -1010], '299 5 10'), ('The Inn of the Kneeling Man', '299 5 20'), ('The Inn of the Kneeling Man', '300 13 5')),
    'jaqen': J(('King\'s Landing', '298 8 2'), ROAD('The Kingsroad', 'King\'s Landing', 'The Inn at the Crossroads', '298 8 3', '298 12 20'), ([120, -940], '299 1 10'), ('Harrenhal', '299 2 1'), ('Harrenhal', '299 4 10')),
    'stannis': J(('Dragonstone', '297 13 1'), ('Dragonstone', '299 3 15'), LANE('dragonstone-storms-end', '299 3 16', '299 3 25'), ('Storm\'s End', '299 4 5'), ('Storm\'s End', '299 5 20'), ([270, -1320], '299 6 1'), ('King\'s Landing', '299 6 2'), LANE('dragonstone-kl', '299 6 3', '299 6 8', True),
                 ('Dragonstone', '299 6 10'), ('Dragonstone', '299 13 1'), LANE('dragonstone-eastwatch', '299 13 2', '300 2 20'), ('Castle Black', '300 3 1'), ('Castle Black', '300 4 20'),
                 ('Deepwood Motte', '300 5 20'), ([-100, 20], '300 8 15'), ([-120, 40], '300 13 5')),
    'davos': J(('Dragonstone', '297 13 1'), ('Dragonstone', '299 5 20'), LANE('dragonstone-kl', '299 5 21', '299 6 1'), ([330, -1260], '299 6 10'), ('Dragonstone', '299 7 1'), ('Dragonstone', '299 13 1'),
               LANE('dragonstone-eastwatch', '299 13 2', '300 2 20'), ('Castle Black', '300 3 5'), ('Eastwatch-by-the-Sea', '300 3 20'), LANE('eastwatch-white-harbor', '300 3 21', '300 4 10'),
               ('White Harbor', '300 4 12'), ('White Harbor', '300 9 1'), ([400, 300], '300 10 1'), ('Skagos', '300 11 1'), ('Skagos', '300 13 5')),
    'melisandre': J(('Dragonstone', '297 13 1'), ('Dragonstone', '299 3 15'), LANE('dragonstone-storms-end', '299 3 16', '299 3 25'), ('Storm\'s End', '299 4 5'),
                    ('Storm\'s End', '299 5 4'), LANE('dragonstone-storms-end', '299 5 5', '299 5 15', True), ('Dragonstone', '299 13 1'),
                    LANE('dragonstone-eastwatch', '299 13 2', '300 2 20'), ('Castle Black', '300 3 1'), ('Castle Black', '300 13 5')),
    'daenerys': J(('Pentos', '297 13 1'), ('Pentos', '298 2 20'), ([820, -1060], '298 2 25'), ([1300, -800], '298 3 20'), ([2000, -900], '298 4 15'), ('Vaes Dothrak', '298 5 1'), ('Vaes Dothrak', '298 6 15'),
                  ([2500, -1400], '298 7 20'), ('A village of the Lamb Men', '298 8 15'), ('A village of the Lamb Men', '298 12 2'), ([2900, -1900], '298 13 5'), ('Vaes Tolorro', '299 1 15'),
                  ([3300, -2400], '299 2 25'), ('Qarth', '299 3 1'), ('Qarth', '299 7 10'), LANE('qarth-astapor', '299 7 11', '299 8 10'), *SLAVERS,
                  ('Meereen', '300 9 1'), ('Daznak\'s Pit', '300 9 2'), ([2200, -1300], '300 9 12'), ([2200, -1300], '300 13 5')),
    'viserys': J(('Pentos', '297 13 1'), ('Pentos', '298 2 20'), ([820, -1060], '298 2 25'), ([1300, -800], '298 3 20'), ([2000, -900], '298 4 15'), ('Vaes Dothrak', '298 5 1'), ('Vaes Dothrak', '298 5 25')),
    'drogo': J(([820, -1060], '298 2 1'), ([820, -1060], '298 2 25'), ([1300, -800], '298 3 20'), ([2000, -900], '298 4 15'), ('Vaes Dothrak', '298 5 1'), ('Vaes Dothrak', '298 6 15'),
               ([2500, -1400], '298 7 20'), ('A village of the Lamb Men', '298 8 15'), ('A village of the Lamb Men', '298 12 1')),
    'jorah': J(('Pentos', '297 13 1'), ('Pentos', '298 2 20'), ([820, -1060], '298 2 25'), ([1300, -800], '298 3 20'), ([2000, -900], '298 4 15'), ('Vaes Dothrak', '298 5 1'), ('Vaes Dothrak', '298 6 15'),
               ([2500, -1400], '298 7 20'), ('A village of the Lamb Men', '298 8 15'), ('A village of the Lamb Men', '298 12 2'), ([2900, -1900], '298 13 5'), ('Vaes Tolorro', '299 1 15'),
               ([3300, -2400], '299 2 25'), ('Qarth', '299 3 1'), ('Qarth', '299 7 10'), LANE('qarth-astapor', '299 7 11', '299 8 10'), *SLAVERS,
               ('Meereen', '300 2 12'), LANE('volantis-meereen', '300 2 13', '300 3 20', True), ('Selhorys', '300 5 5'), ('Volantis', '300 5 20'), LANE('volantis-meereen', '300 6 1', '300 7 20'), ([2656, -1976], '300 7 21'),
               ([2600, -1990], '300 8 1'), ([2600, -1990], '300 13 5')),
    'missandei': J(('Astapor', '297 13 1'), *SLAVERS, ('Meereen', '300 13 5')),
    'barristan': J(('King\'s Landing', '297 13 1'), ('King\'s Landing', '298 6 1'), LANE('kl-pentos', '298 6 2', '298 7 1'), ('Pentos', '298 9 1'), ('Pentos', '299 5 1'), LANE('pentos-qarth', '299 5 2', '299 7 1'),
                   LANE('qarth-astapor', '299 7 11', '299 8 10'), *SLAVERS, ('Meereen', '300 13 5')),
    'quaithe': J(('Qarth', '297 13 1'), ('Qarth', '300 13 5')),
    'griff': J(('Pentos', '300 3 20'), ([1150, -850], '300 4 10'), ('Chroyane', '300 4 25'), ('Selhorys', '300 5 1'), ([1300, -2150], '300 6 1'), LANE('volon-therys-cape-wrath', '300 6 2', '300 9 1'), ('Griffin\'s Roost', '300 9 5'), ('Griffin\'s Roost', '300 13 5')),
    'others': J(([-30, 900], '297 13 1'), ([-30, 600], '298 1 1'), ([-10, 760], '298 2 1'), ([-10, 760], '299 1 1'), ('The Fist of the First Men', '299 4 1'), ([-30, 600], '299 6 1'),
                ([0, 560], '300 1 1'), ([30, 520], '300 13 5')),
    'coldhands': J(([0, 640], '297 13 1'), ([-30, 560], '299 8 20'), ('The Nightfort', '299 9 2'), ([-30, 520], '299 9 10'), ([-20, 700], '299 12 1'), ([20, 880], '300 2 1'), ('The cave of the three-eyed crow', '300 4 1'), ('The cave of the three-eyed crow', '300 13 5')),
    'threeeyed': J(('The cave of the three-eyed crow', '297 13 1'), ('The cave of the three-eyed crow', '300 13 5')),
    'ramsay': J(([150, 40], '299 2 20'), ([60, 10], '299 3 20'), ('Winterfell', '299 4 10'), ('Winterfell', '299 5 1'), ('The Dreadfort', '299 5 12'), ('Winterfell', '299 6 1'),
                ('The Dreadfort', '299 6 12'), ('The Dreadfort', '300 1 20'), ('Moat Cailin', '300 2 10'), ('Barrowton', '300 3 20'), ('Winterfell', '300 6 1'), ('Winterfell', '300 13 5')),
    'benjen': J(('Winterfell', '298 2 1'), ('Winterfell', '298 2 20'), ROAD('The Kingsroad', 'Winterfell', 'Castle Black', '298 2 20', '298 3 20'), ('Castle Black', '298 3 25'), ([-80, 620], '298 4 20')),
    'mance': J(([-200, 860], '297 13 1'), ([-200, 860], '299 4 1'), ([-150, 700], '299 5 1'), ([-60, 600], '299 9 1'), ([10, 520], '300 3 1'), ('Castle Black', '300 3 10'), ('Castle Black', '300 13 5')),
    'ygritte': J(([-200, 760], '297 13 1'), ([-200, 760], '299 3 20'), ('The Skirling Pass', '299 3 20'), ([-150, 700], '299 5 1'), ([-60, 520], '299 7 20'), ('Queenscrown', '299 8 1'), ([40, 470], '300 3 1')),
    'tormund': J(([-200, 860], '297 13 1'), ([-200, 860], '299 4 1'), ([-150, 700], '299 5 1'), ([-60, 520], '299 7 20'), ('Queenscrown', '299 8 1'), ([40, 470], '300 3 1'), ([80, 600], '300 3 5'), ('Hardhome', '300 8 1'), ('Castle Black', '300 10 1'), ('Castle Black', '300 13 5')),
    'craster': J(('Craster\'s Keep', '297 13 1'), ('Craster\'s Keep', '299 5 20')),
    'gilly': J(('Craster\'s Keep', '297 13 1'), ('Craster\'s Keep', '299 6 1'), ([-30, 560], '299 8 20'), ('The Nightfort', '299 9 1'), ('Castle Black', '299 9 10'), ('Castle Black', '300 3 20'),
               ('Eastwatch-by-the-Sea', '300 4 1'), LANE('eastwatch-braavos', '300 4 2', '300 5 1'), ('Braavos', '300 6 10'), LANE('braavos-oldtown', '300 6 11', '300 8 1'), ([-440, -2113], '300 8 3'), ([-440, -2113], '300 13 5')),
    'hodor': J(('Winterfell', '297 13 1'), ('Winterfell', '299 5 1'), ([-30, 120], '299 5 20'), ([60, 300], '299 7 15'), ('Queenscrown', '299 8 1'), ('The Nightfort', '299 9 1'), ([-30, 520], '299 9 10'),
               ([-20, 700], '299 12 1'), ([20, 880], '300 2 1'), ('The cave of the three-eyed crow', '300 4 1'), ('The cave of the three-eyed crow', '300 13 5')),
    'meera': J(('Greywater Watch', '297 13 1'), ('Greywater Watch', '299 1 15'), ROAD('The Kingsroad', 'Moat Cailin', 'Winterfell', '299 1 20', '299 2 15'), ('Winterfell', '299 5 1'), ([-30, 120], '299 5 20'),
               ([60, 300], '299 7 15'), ('Queenscrown', '299 8 1'), ('The Nightfort', '299 9 1'), ([-30, 520], '299 9 10'), ([-20, 700], '299 12 1'), ([20, 880], '300 2 1'),
               ('The cave of the three-eyed crow', '300 4 1'), ('The cave of the three-eyed crow', '300 13 5')),
    'osha': J(([-40, 120], '297 13 1'), ([-40, 120], '298 4 10'), ('Winterfell', '298 4 12'), ('Winterfell', '299 5 1'), ([200, 120], '299 5 25'), ([322, 365], '299 9 1'), ([322, 365], '299 11 20'), LANE('bay-of-seals-skagos', '299 11 21', '299 12 1'), ('Skagos', '300 13 5')),
}
PATHS['jojen'] = PATHS['meera']
# the wolves keep their people's roads while they are together
PATHS['ghost'] = PATHS['jon']
PATHS['greywind'] = PATHS['robb']
PATHS['summer'] = PATHS['bran']
PATHS['shaggydog'] = PATHS['rickon']
PATHS['lady'] = J(('Winterfell', '297 13 1'), ('Winterfell', '298 2 20'), ROAD('The Kingsroad', 'Winterfell', 'The Inn at the Crossroads', '298 2 20', '298 3 14'), ('Darry', '298 3 16'))
PATHS['nymeria'] = J(('Winterfell', '297 13 1'), ('Winterfell', '298 2 20'), SOUTH[0], ([120, -860], '298 4 1'),
                     ([40, -980], '299 3 1'), ([150, -1000], '299 9 1'), ([60, -930], '300 4 1'), ([60, -930], '300 13 5'))
for d in ('drogon', 'rhaegal', 'viserion'):
    PATHS[d] = [x for x in PATHS['daenerys'] if not (isinstance(x, tuple) and len(x) == 2 and T(x[1]) < T('298 12 2'))]
    PATHS[d] = [('A village of the Lamb Men', '298 12 2')] + [x for x in PATHS[d] if x[0] != 'lane' and (x[0] == 'lane' or T(x[-1] if x[0] in ('road', 'lane') else x[1]) > T('298 12 2'))]
PATHS['robbking'] = None
PATHS['reek'] = None

# who rides together where the books say so ([id or regex, from, to, mode]); walk is the default
MODES = [
    ['^(robert|cersei|joffrey|jaime|tyrion|sandor|eddard|sansa|arya|jon|benjen|lady|nymeria|ghost)$', '297 12 1', '298 4 2', 'ride'],
    ['^cersei$', '297 12 1', '298 4 2', 'wheelhouse'],                     # the queen's great wheelhouse on the Kingsroad
    ['^catelyn$', '298 2 25', '298 3 3', 'ride'], ['^samwell$', '297 12 1', '298 3 26', 'ride'],
    ['^(catelyn)$', '298 3 4', '298 3 20', 'sea'], ['^(catelyn)$', '298 7 5', '298 7 16', 'sea'],
    ['^(catelyn|tyrion|bronn)$', '298 4 3', '298 6 10', 'ride'],
    ['^(robb|greywind|theon)$', '298 7 2', '299 6 15', 'ride'],
    ['^theon$', '299 1 16', '299 1 22', 'sea'], ['^theon$', '299 2 26', '299 3 12', 'sea'],
    ['^(tyrion|bronn)$', '298 12 22', '299 1 5', 'ride'], ['^tyrion$', '300 2 11', '300 3 5', 'sea'], ['^(tyrion|griff)$', '300 3 21', '300 5 20', 'boat'],
    ['^(tyrion|jorah)$', '300 6 1', '300 7 21', 'sea'],
    ['^(daenerys|viserys|drogo|jorah)$', '298 2 25', '298 8 15', 'ride'], ['^(daenerys|jorah|barristan|drogon|rhaegal|viserion)$', '299 7 11', '299 8 10', 'sea'],
    ['^barristan$', '298 6 2', '298 7 1', 'sea'],
    ['^(stannis|davos|melisandre)$', '299 13 2', '300 2 20', 'sea'], ['^davos$', '299 5 21', '299 7 1', 'sea'], ['^stannis$', '299 6 2', '299 6 8', 'sea'],
    ['^davos$', '300 3 21', '300 4 10', 'sea'], ['^davos$', '300 9 2', '300 11 1', 'sea'],
    ['^(samwell|gilly)$', '300 4 2', '300 5 1', 'sea'], ['^(samwell|gilly)$', '300 6 11', '300 8 1', 'sea'],
    ['^(sansa|littlefinger)$', '300 1 16', '300 2 5', 'sea'],
    ['^arya$', '300 1 6', '300 2 1', 'sea'],
    ['^(arya|sandor)$', '299 8 1', '300 1 1', 'ride'],
    ['^(jaime|brienne)$', '299 7 1', '299 7 10', 'boat'],
    ['^(daenerys|drogon)$', '300 9 2', '300 9 12', 'dragon'],             # Daenerys flies from the pit on Drogon
    ['^(coldhands)$', '299 8 20', '300 4 1', 'ride'],                      # on a great elk in the books' telling
]

# ------------------------------------------------------------------ the lords of the Seven Kingdoms, their kings, and the khalasar
CHARS.update({
    'roose': dict(tier='secondary', house='Bolton', head=H('Roose Bolton', '#f2e4dc', ['#3a3030', '#221c1c'], 'short', eye='#d8e8f0'),
                  body=dict(tunic='#3a2a2a', legs='#2a2020', cloak='#d89a9a', boots='#1a1010', gear='sword', mail=1),
                  bio='Lord of the Dreadfort, a quiet man with pale eyes who leeches his own blood; he leads Robb\'s foot south.', fate='Warden of the North after the Red Wedding.'),
    'hoster': dict(tier='secondary', house='Tully', head=H('Hoster Tully', '#ecd0bc', ['#e8e4dc', '#b8b2a6'], 'sparse', wrinkles=1, beard='short', beardC=['#e8e4dc', '#b8b2a6']),
                   body=dict(robe='#4a6aa0', belt='#a83a2a'), bio='Lord of Riverrun and Lord Paramount of the Trident, Catelyn\'s father, dying in his bed.', fate='Dies at Riverrun (ASOS).'),
    'edmure': dict(tier='secondary', house='Tully', head=H('Edmure Tully', '#f0d0b8', AUBURN, 'short', beard='short', beardC=AUBURN),
                   body=dict(tunic='#3a5aa8', legs='#2a2a3a', cloak='#a83a2a', boots='#2a1f18', gear='sword', mail=1), bio='Catelyn\'s brother, heir and then Lord of Riverrun, wed at the Twins.', fate='A captive after the Red Wedding.'),
    'lysa': dict(tier='secondary', house='Arryn (born Tully)', head=H('Lysa Arryn', '#f2d6c4', AUBURN, 'long', blush=1), body=dict(robe='#7a9ac8', belt='#e8e0c8'),
                 bio='Lady of the Eyrie, Catelyn\'s sister, ruling the Vale for her sickly son.', fate='Thrown from the Moon Door (ASOS).'),
    'sweetrobin': dict(tier='secondary', house='Arryn', head=H('Robert Arryn', '#f4e4dc', ['#8a6a4a', '#5e4630'], 'sparse', blush=1), body=dict(robe='#e8e4f0', belt='#7a9ac8'),
                       bio='The boy Lord of the Eyrie and Defender of the Vale, frail and given to shaking fits.'),
    'balon': dict(tier='secondary', house='Greyjoy', head=H('Balon Greyjoy', '#d8b896', GREY, 'long', beard='short', beardC=GREY, brows=1),
                  body=dict(tunic='#2a2a2a', legs='#1a1a1e', cloak='#c8a040', boots='#141414', gear='sword'), bio='Lord of the Iron Islands, who crowns himself again and sends his longships against the North.', fate='Falls from a bridge at Pyke (ACOK).'),
    'euron': dict(tier='mysterious', house='Greyjoy', head=H('Euron Greyjoy', '#e8d0c0', BLACK, 'short', beard='short', beardC=BLACK, eye='#2a58c8'),
                  body=dict(tunic='#1a1a2a', legs='#141418', cloak='#3a1a4a', boots='#101010', gear='sword', mail=1), bio='The Crow\'s Eye, Balon\'s brother, back from strange seas to claim the Seastone Chair.'),
    'mace': dict(tier='secondary', house='Tyrell', head=H('Mace Tyrell', '#f0c8a8', BROWN, 'short', beard='short', beardC=BROWN),
                 body=dict(tunic='#3a8a3a', legs='#2a4a2a', boots='#2a1f18', belt='#e0c040', fat=1), bio='Lord of Highgarden and Warden of the South, who backs Renly and then the Lannisters.'),
    'renly': dict(tier='secondary', house='Baratheon', head=H('Renly Baratheon', '#f0c8a8', BLACK, 'short', hat='crown', hatC=['#3a8a3a', '#2a6a2a']),
                  body=dict(tunic='#3a6a3a', legs='#2a3a2a', cloak='#e0c040', boots='#2a1f18', gear='sword'), bio='Robert\'s youngest brother, Lord of Storm\'s End, who claims the crown with the Reach behind him.', fate='Slain by a shadow in his tent (ACOK).'),
    'doran': dict(tier='secondary', house='Martell', head=H('Doran Martell', '#b8885e', GREY, 'sparse'), body=dict(robe='#c8783a', belt='#e8c040'),
                  bio='Prince of Dorne, gouty and patient, who watches from the Water Gardens and keeps his own counsel.'),
    'tommen': dict(tier='secondary', house='Baratheon (Lannister)', head=H('Tommen Baratheon', '#f6dcc8', GOLD, 'short', blush=1), body=dict(tunic='#c8302a', legs='#3a2a2a', boots='#2a1f18'),
                   bio='Cersei\'s gentle younger son, who becomes king after his brother.'),
    'dothraki': dict(tier='secondary', house='the Dothraki', head=H('The khalasar', '#b07850', BLACK, 'long'), body=dict(tunic='#a87048', legs='#5a4030', boots='#3a2a1e', belt='#c9a03c', gear='sword'),
                     bio='Khal Drogo\'s horde of horse lords, tens of thousands strong, riding the grass sea between the cities.'),
    'bloodriders': dict(tier='sidekick', house='the Dothraki', head=H('Aggo, Jhogo and Rakharo', '#b48058', BLACK, 'long'), body=dict(tunic='#8a6040', legs='#5a4030', boots='#3a2a1e', gear='bow'),
                        bio='The young riders who stay with Daenerys when the khalasar leaves her: her bloodriders.'),
})
ROOSE = J(('The Dreadfort', '297 13 1'), ('The Dreadfort', '298 6 20'), ('Winterfell', '298 7 1'), ROAD('The Kingsroad', 'Winterfell', 'Moat Cailin', '298 7 2', '298 7 20'), ('The Twins', '298 8 5'),
          ([150, -800], '298 8 12'), ([130, -830], '298 8 14'), ([90, -700], '298 8 25'), ('The Twins', '298 9 10'), ('The Twins', '299 5 1'), ('Harrenhal', '299 6 10'), ('Harrenhal', '299 8 20'),
          ('The Twins', '299 8 30'), ('The Twins', '299 12 1'), ('Moat Cailin', '300 2 10'), ('Barrowton', '300 3 20'), ('Winterfell', '300 6 1'), ('Winterfell', '300 13 5'))
PATHS.update({
    'roose': ROOSE,
    'hoster': J(('Riverrun', '297 13 1'), ('Riverrun', '299 7 1')),
    'edmure': J(('Riverrun', '297 13 1'), ('Riverrun', '299 8 20'), ('The Twins', '299 8 30'), ('The Twins', '300 6 15'), ('Riverrun', '300 7 1'), ('Riverrun', '300 8 10'), ('Casterly Rock', '300 9 10'), ('Casterly Rock', '300 13 5')),
    'lysa': J(('The Eyrie', '297 13 1'), ('The Eyrie', '300 2 20')),
    'sweetrobin': J(('The Eyrie', '297 13 1'), ('The Eyrie', '300 6 1'), ('Gates of the Moon', '300 6 10'), ('Gates of the Moon', '300 13 5')),
    'balon': J(('Pyke', '297 13 1'), ('Pyke', '299 10 1')),
    'euron': J(([-760, -980], '299 11 1'), ([-420, -760], '299 12 10'), ('Pyke', '299 12 15'), ([-300, -700], '300 1 20'), ('Pyke', '300 2 1'), ([-560, -1300], '300 4 1'), ([-470, -1720], '300 5 1'), ([-470, -1720], '300 13 5')),
    'mace': J(('Highgarden', '297 13 1'), ('Highgarden', '299 1 20'), ('Bitterbridge', '299 2 15'), ('Bitterbridge', '299 5 20'), ('King\'s Landing', '299 6 1'), ('King\'s Landing', '300 4 1'), ('Storm\'s End', '300 5 1'), ('Storm\'s End', '300 13 5')),
    'renly': J(('King\'s Landing', '297 13 1'), ('King\'s Landing', '298 5 15'), ('Highgarden', '298 7 1'), ('Highgarden', '299 1 20'), ('Bitterbridge', '299 2 15'), ('Storm\'s End', '299 4 5'), ([380, -1570], '299 4 7')),
    'doran': J(('The Water Gardens', '297 13 1'), ('The Water Gardens', '300 3 1'), ('Sunspear', '300 3 10'), ('Sunspear', '300 13 5')),
    'tommen': J(('King\'s Landing', '297 12 1'), ROAD('The Kingsroad', 'King\'s Landing', 'Winterfell', '297 12 2', '298 2 1'), ('Winterfell', '298 2 20'), *SOUTH, ('King\'s Landing', '299 5 20'),
                ('Rosby', '299 5 25'), ('Rosby', '299 6 3'), ('King\'s Landing', '299 6 6'), ('King\'s Landing', '300 13 5')),
    'dothraki': J(([820, -1060], '297 13 1'), ([820, -1060], '298 2 25'), ([1300, -800], '298 3 20'), ([2000, -900], '298 4 15'), ('Vaes Dothrak', '298 5 1'), ('Vaes Dothrak', '298 6 15'),
                  ([2500, -1400], '298 7 20'), ('A village of the Lamb Men', '298 8 15'), ('A village of the Lamb Men', '298 12 1'), ([2650, -1300], '298 12 20')),
})
PATHS['drogo'] = [(([820, -1060], '297 13 1'))] + PATHS['drogo'][1:]
MODES[:0] = [['^(dothraki|drogo)$', '297 13 1', '298 12 25', 'ride'], ['^roose$', '298 7 2', '298 8 25', 'ride'], ['^tommen$', '297 12 1', '298 4 2', 'ride'],
             ['^renly$', '298 5 15', '298 7 1', 'ride'], ['^euron$', '299 11 1', '300 5 1', 'sea'], ['^bloodriders$', '299 7 11', '299 8 10', 'sea'],
             ['^bloodriders$', '298 12 2', '300 13 5', 'ride'], ['^mace$', '299 5 20', '299 6 1', 'ride']]

# who rules each kingdom, and who wears (or claims) its crown: [role, character or None, from, to, title]; dates estimated
RULERS = {
    'The North': [['lord', 'eddard', None, '298 8 1', 'Lord of Winterfell, Warden of the North'], ['lord', 'robb', '298 8 1', '298 9 1', 'Lord of Winterfell'], ['lord', 'robbking', '298 9 1', '299 9 1', 'Lord of Winterfell and King in the North'],
                  ['claim', 'robbking', '298 9 1', '299 9 1', 'King in the North'], ['lord', 'roose', '299 9 1', None, 'Warden of the North (for the Iron Throne)'],
                  ['claim', 'balon', '299 4 1', '299 10 1', 'King of the Isles and the North'], ['claim', 'stannis', '300 4 1', None, 'King (claimant), marching on Winterfell']],
    'The Riverlands': [['lord', 'hoster', None, '299 7 1', 'Lord Paramount of the Trident'], ['lord', 'edmure', '299 7 1', '299 9 1', 'Lord Paramount of the Trident'],
                       ['lord', 'littlefinger', '299 9 1', None, 'Lord Paramount of the Trident (by the Iron Throne\'s grant)'], ['claim', 'robbking', '298 9 1', '299 9 1', 'King in the North and of the Trident']],
    'The Vale': [['lord', 'sweetrobin', None, None, 'Lord of the Eyrie, Defender of the Vale'], ['regent', 'lysa', None, '300 2 20', 'Lady Regent'], ['regent', 'littlefinger', '300 2 20', None, 'Lord Protector of the Vale']],
    'The Iron Islands': [['lord', 'balon', None, '299 10 1', 'Lord Reaper of Pyke'], ['claim', 'balon', '299 1 1', '299 10 1', 'King of the Iron Islands'], ['claim', 'euron', '300 1 20', None, 'King of the Iron Islands, by the kingsmoot']],
    'The Westerlands': [['lord', 'tywin', None, '300 2 10', 'Lord of Casterly Rock, Warden of the West'], ['lord', None, '300 2 10', None, 'Casterly Rock unclaimed: Jaime of the Kingsguard will not take it']],
    'The Reach': [['lord', 'mace', None, None, 'Lord of Highgarden, Warden of the South'], ['claim', 'renly', '298 7 1', '299 4 7', 'King, crowned at Highgarden']],
    'The Stormlands': [['lord', 'renly', None, '299 4 7', 'Lord of Storm\'s End'], ['lord', 'stannis', '299 4 7', None, 'Lord of Storm\'s End (held for him)'], ['claim', 'renly', '298 7 1', '299 4 7', 'King, crowned at Highgarden']],
    'Dorne': [['lord', 'doran', None, None, 'Prince of Dorne']],
    'The Crownlands': [['lord', 'robert', None, '298 5 15', 'the King holds the crownlands'], ['lord', 'joffrey', '298 5 15', '300 1 15', 'the King holds the crownlands'],
                       ['lord', 'tommen', '300 1 15', None, 'the King holds the crownlands'], ['claim', 'stannis', '298 7 1', None, 'King (claimant), from Dragonstone']],
}
CROWN = [['robert', None, '298 5 15', 'King of the Andals and the First Men, on the Iron Throne'], ['joffrey', '298 5 15', '300 1 15', 'King on the Iron Throne'],
         ['tommen', '300 1 15', None, 'King on the Iron Throne']]
SEVEN = ['The North', 'The Vale', 'The Riverlands', 'The Iron Islands', 'The Westerlands', 'The Reach', 'The Stormlands', 'Dorne', 'The Crownlands']

# deaths: [character, date, place or [X, Y], how] -- the body lies where it fell for a time, under a death mark
DEATHS = [
    ['lady', '298 3 16', 'Darry', 'killed on the king\'s order'], ['robert', '298 5 15', [251.0, -1299.0], 'dies of the boar\'s wound'],
    ['viserys', '298 5 25', 'Vaes Dothrak', 'crowned with molten gold'], ['eddard', '298 8 1', [249.4, -1300.8], 'beheaded before the Great Sept'],
    ['drogo', '298 12 1', 'A village of the Lamb Men', 'dies of a festering wound'], ['renly', '299 4 7', [380, -1570], 'slain by a shadow in his tent'],
    ['craster', '299 5 20', 'Craster\'s Keep', 'killed in the mutiny at his keep'], ['hoster', '299 7 1', 'Riverrun', 'dies in his bed'],
    ['robbking', '299 9 1', [38.6, -621.4], 'murdered at the Red Wedding'], ['catelyn', '299 9 1', [41.4, -621.3], 'murdered at the Red Wedding'],
    ['greywind', '299 9 1', [40.0, -622.4], 'killed at the Red Wedding'], ['balon', '299 10 1', 'Pyke', 'falls from a bridge in a storm'],
    ['joffrey', '300 1 15', [250.6, -1299.5], 'poisoned at his wedding feast'], ['tywin', '300 2 10', [250.4, -1299.3], 'killed by his son'],
    ['lysa', '300 2 20', 'The Eyrie', 'pushed through the Moon Door'], ['ygritte', '300 3 1', 'Castle Black', 'killed by an arrow in the attack'],
]
BODY_DAYS = 24

# battles in our own words (dates estimated): sides with banners and soldier kinds, as in the Arda engine
def BT(name, at, d0, d1, src, sides, outcome, **kw): return dict(name=name, at=at, frm=d0, to=d1, src=src, sides=sides, outcome=outcome, **kw)
def SIDE(name, note, banner, units): return dict(name=name, note=note, banner=banner, units=units)
BATTLES = [
    BT('The Battle of the Green Fork', [130, -830], '298 8 14', '298 8 14.6', 'AGOT', [SIDE('The North', 'Roose Bolton with Robb\'s foot', 'stark', [['stark', 6], ['bolton', 2]]),
       SIDE('The Lannisters', 'Lord Tywin, with Tyrion and the hill clans', 'lannister', [['lannister', 6], ['clansman', 3]])], 'The northmen are thrown back, but the battle holds Tywin while Robb crosses the river.'),
    BT('The Battle in the Whispering Wood', 'The Whispering Wood', '298 8 15', '298 8 15.4', 'AGOT', [SIDE('The North', 'Robb Stark\'s horse, Grey Wind among them', 'stark', [['starkrider', 3], ['stark', 4]]),
       SIDE('The Lannisters', 'Jaime Lannister\'s host besieging Riverrun', 'lannister', [['lannister', 6]])], 'Jaime Lannister is taken captive.'),
    BT('The Battle of the Camps', [-30, -890], '298 8 18', '298 8 18.5', 'AGOT', [SIDE('The North and the Trident', 'Robb\'s host and the Tully men from the castle', 'stark', [['stark', 4], ['tully', 3]]),
       SIDE('The Lannisters', 'the camps around Riverrun', 'lannister', [['lannister', 6]])], 'The siege of Riverrun is broken.'),
    BT('The raid on the Lamb Men', 'A village of the Lamb Men', '298 8 15', '298 8 15.6', 'AGOT', [SIDE('The Dothraki', 'Khal Drogo\'s khalasar', 'dothraki', [['dothrakirider', 5]]),
       SIDE('The Lhazareen', 'shepherds of a village of the Lamb Men', 'lamb', [['lhazareen', 5]])], 'The village burns; Daenerys claims the captive women.'),
    BT('The Battle of Oxcross', 'Oxcross', '299 3 5', '299 3 5.4', 'ACOK', [SIDE('The North', 'Robb Stark, by night, through the hills', 'stark', [['starkrider', 3], ['stark', 4]]),
       SIDE('The Lannisters', 'Stafford Lannister\'s new levies', 'lannister', [['lannister', 6]])], 'Stafford Lannister is slain and his host scattered.'),
    BT('The Fist of the First Men', 'The Fist of the First Men', '299 4 1', '299 4 1.5', 'ASOS', [SIDE('The Night\'s Watch', 'the Lord Commander\'s great ranging', 'watch', [['watch', 6]]),
       SIDE('The Others', 'the dead and the white walkers in the snow', 'others', [['wight', 6], ['other', 2]])], 'The Watch is broken; a few fight their way out.'),
    BT('The Battle of the Blackwater', [252, -1306], '299 6 1', '299 6 1.6', 'ACOK', [SIDE('Stannis Baratheon', 'his fleet and host before King\'s Landing', 'baratheon', [['baratheon', 6], ['baratheon', 2]]),
       SIDE('The Iron Throne', 'the city, wildfire, then Tywin and the Tyrells in the flank', 'lannister', [['lannister', 4], ['tyrell', 3]])], 'Wildfire burns Stannis\'s ships and the Lannister and Tyrell host routs him.'),
    BT('The sack of Winterfell', 'Winterfell', '299 6 1', '299 6 1.4', 'ACOK', [SIDE('The ironborn', 'Theon Greyjoy\'s few men in the castle', 'greyjoy', [['ironborn', 4]]),
       SIDE('The Bastard\'s men', 'Ramsay Snow\'s riders, posing as rescuers', 'bolton', [['bolton', 6]])], 'Winterfell is put to the torch and Theon is taken.'),
    BT('The taking of Astapor', 'Astapor', '299 8 20', '299 8 20.4', 'ASOS', [SIDE('Daenerys Targaryen', 'her new Unsullied, at her word', 'targaryen', [['unsullied', 6]]),
       SIDE('The Good Masters', 'the slavers of Astapor', 'ghiscari', [['ghiscari', 5]])], 'The Unsullied kill the masters; Daenerys frees the city\'s slaves.'),
    BT('The Red Wedding', 'The Twins', '299 9 1', '299 9 1.5', 'ASOS', [SIDE('The North', 'Robb Stark and his men, guests under the Freys\' roof', 'stark', [['stark', 6]]),
       SIDE('The Freys and the Boltons', 'Walder Frey\'s men and Roose Bolton', 'frey', [['frey', 6], ['bolton', 2]])], 'Robb Stark, his mother and his host are murdered at the feast.'),
    BT('The attack on Castle Black', 'Castle Black', '300 3 1', '300 3 2', 'ASOS', [SIDE('The Night\'s Watch', 'Jon Snow and a few score brothers', 'watch', [['watch', 5]]),
       SIDE('The free folk', 'Mance Rayder\'s host, giants and mammoths', 'freefolk', [['freefolk', 6], ['giant', 1]])], 'The Watch holds the gate.'),
    BT('The battle beneath the Wall', [30, 440], '300 3 10', '300 3 10.5', 'ASOS', [SIDE('Stannis Baratheon', 'his knights, come by sea from Dragonstone', 'baratheon', [['baratheonrider', 4], ['baratheon', 3]]),
       SIDE('The free folk', 'Mance Rayder\'s host', 'freefolk', [['freefolk', 6]])], 'The free folk are routed and Mance Rayder is taken.'),
]
# the fallen lie where the fighting was, for a time; at the Red Wedding the dead are everywhere
FALLEN = {'The Red Wedding': ('299 9 1', 30, [['stark', 30], ['frey', 3]], 3.2)}
FALLEN_DEFAULT = (12, 0.5, 1.6)        # days, share of each side's figures that lies dead, spread in miles

# casts: who appears in each journey and when (looks change: Robb crowned, Theon broken)
CASTS = {k: [k] for k in PATHS if PATHS[k]}
CASTS['robb'] = [['robb', None, '298 9 1'], ['robbking', '298 9 1', None]]
CASTS['theon'] = [['theon', None, '299 6 12'], ['reek', '299 6 12', None]]

# scenes: named companies (first match wins)
GROUPS = [
    dict(name='The Red Wedding', all=['robbking', 'catelyn'], when=['299 8 30', '299 9 2'], frame='#3a0e0e', edge='#e04040', emblem='star'),
    dict(name='The direwolf pups', all=['eddard', 'robb', 'jon', 'bran'], when=['297 13 1', '298 1 30'], frame='#2a3440', edge='#c8ccd4', emblem='star', lead=['bran', 'jon', 'robb']),
    dict(name='The Starks of Winterfell', all=['eddard', 'catelyn', 'robb', 'sansa'], when=['298 1 30', '298 2 21'], frame='#2a3440', edge='#c8ccd4', emblem='star', lead=['eddard', 'catelyn']),
    dict(name='The King\'s Progress', all=['robert', 'cersei'], frame='#3a2a10', edge='#e8c060', emblem='key', lead=['robert', 'cersei', 'eddard']),
    dict(name='The Hand\'s Household', all=['eddard', 'sansa', 'arya'], frame='#2a3440', edge='#c8ccd4', emblem='star'),
    dict(name='Yoren\'s recruits', all=['arya', 'gendry', 'jaqen'], frame='#1e1e22', edge='#9a9ea8', emblem='key'),
    dict(name='Arya and Gendry', all=['arya', 'gendry'], frame='#2a2a2e', edge='#c8ccd4', emblem='key'),
    dict(name='The Hound and the wolf girl', all=['arya', 'sandor'], frame='#2a2218', edge='#c89a5a', emblem='hand'),
    dict(name='Bran\'s company', all=['bran', 'hodor', 'meera'], frame='#1e2a20', edge='#7aa06a', emblem='leaf', lead=['bran', 'hodor']),
    dict(name='Osha and Rickon', all=['rickon', 'osha'], frame='#2a2a2e', edge='#c8ccd4', emblem='star'),
    dict(name='The Night\'s Watch', all=['jon', 'samwell'], frame='#121216', edge='#9a9ea8', emblem='key', lead=['jon', 'samwell']),
    dict(name='The free folk', all=['mance', 'tormund'], frame='#2a2218', edge='#8a2020', emblem='star'),
    dict(name='Jon among the free folk', all=['jon', 'ygritte'], frame='#2a2218', edge='#c03a1e', emblem='star'),
    dict(name='Tyrion and Bronn', all=['tyrion', 'bronn'], frame='#3a1414', edge='#e8c060', emblem='hand'),
    dict(name='Jaime and Brienne', all=['jaime', 'brienne'], frame='#2a3a5a', edge='#e8e4dc', emblem='star'),
    dict(name='Mother of Dragons', all=['daenerys', 'drogon'], frame='#2a1414', edge='#e04030', emblem='eye', lead=['daenerys', 'drogon']),
    dict(name='The khalasar of Drogo', all=['daenerys', 'drogo'], frame='#3a2a18', edge='#c9a03c', emblem='horse', lead=['drogo', 'daenerys']),
    dict(name='Stannis and the red woman', all=['stannis', 'melisandre'], frame='#3a0e0e', edge='#ff4020', emblem='eye'),
    dict(name='Bran and Coldhands', all=['bran', 'coldhands'], frame='#0e1216', edge='#6a8aa0', emblem='leaf'),
    dict(name='The Others', all=['others'], frame='#0e1a24', edge='#4ab8ff', emblem='star', solo=1, show=['others', 'others', 'others']),
    dict(name='Sam and Gilly', all=['samwell', 'gilly'], frame='#1e1e22', edge='#c8ccd4', emblem='leaf'),
    dict(name='The Spider', all=['varys'], frame='#1e1424', edge='#8a6aa0', emblem='web', solo=1),
]

GROUPS[:0] = [
    dict(name='The khalasar of Drogo', all=['drogo', 'dothraki'], frame='#3a2a18', edge='#c9a03c', emblem='horse', show=['dothraki', 'dothraki', 'drogo', 'dothraki'], lead=['drogo']),
    dict(name='The Dothraki', all=['dothraki'], solo=1, frame='#3a2a18', edge='#c9a03c', emblem='horse', show=['dothraki', 'dothraki', 'dothraki']),
    dict(name='Daenerys and her bloodriders', all=['daenerys', 'bloodriders'], frame='#2a1414', edge='#e04030', emblem='horse', lead=['daenerys']),
    dict(name='Renly\'s court', all=['renly', 'margaery'], frame='#1e3a1e', edge='#e0c040', emblem='leaf'),
]

# events in our own words; dates are estimates
EVENTS = {
    'agot': [['298 1 1', 'Beyond the Wall, rangers of the Night\'s Watch meet the Others (date est.)', -30, 600],
             ['298 1 5', 'A deserter of the Night\'s Watch is executed near Winterfell; the Stark children find six direwolf pups (date est.)', -10, 20],
             ['298 2 1', 'King Robert comes to Winterfell and asks Eddard Stark to be his Hand (date est.)', 0, 0], ['298 2 10', 'Bran falls from a tower at Winterfell (date est.)', 0, 0],
             ['298 2 20', 'Eddard rides south with the king; Jon sets out for the Wall with Tyrion and Benjen (date est.)', 0, 0],
             ['298 2 25', 'Across the narrow sea, Daenerys Targaryen is wed to Khal Drogo near Pentos (date est.)', 820, -1060],
             ['298 3 12', 'At the Trident, Arya drives Nymeria away to save her (date est.)', 160, -890], ['298 3 16', 'Lady is killed on the king\'s order at Darry (date est.)', 190, -1010],
             ['298 4 25', 'Benjen Stark rides beyond the Wall and does not return (date est.)', -80, 620],
             ['298 5 14', 'King Robert is mortally wounded by a boar in the Kingswood (date est.)', 330, -1450],
             ['298 5 20', 'Catelyn Stark seizes Tyrion Lannister at the Inn at the Crossroads (date est.)', 175, -935],
             ['298 5 25', 'Viserys is crowned with molten gold in Vaes Dothrak (date est.)', 2700, -1040],
             ['298 6 24', 'Bronn wins Tyrion\'s trial by combat at the Eyrie (date est.)', 362, -756],
             ['298 8 14', 'The Battle of the Green Fork: Roose Bolton\'s foot meet Tywin Lannister\'s host (date est.)', 130, -830], ['298 8 1', 'Eddard Stark is executed before the Great Sept of Baelor (date est.)', 244, -1301],
             ['298 8 15', 'Robb Stark takes Jaime Lannister in the Whispering Wood (date est.)', -15, -870],
             ['298 12 1', 'Drogo dies; Daenerys walks into his pyre and three dragons are born (date est.)', 2400, -1720]],
    'acok': [['299 1 15', 'A red comet hangs in the sky (date est.)', 0, 0], ['299 2 1', 'Arya comes to Harrenhal; Jaqen H\'ghar owes her three deaths (date est.)', 130, -960],
             ['299 3 1', 'Daenerys reaches Qarth (date est.)', 3410, -2590], ['299 3 5', 'Robb wins at Oxcross in the westerlands (date est.)', -330, -1100],
             ['299 4 1', 'Theon Greyjoy takes Winterfell (date est.)', 0, 0], ['299 6 1', 'The Battle of the Blackwater: wildfire burns Stannis\'s fleet before King\'s Landing (date est.)', 250, -1300],
             ['299 6 1', 'Winterfell is sacked and burned (date est.)', 0, 0], ['299 4 1', 'The Others come to the Fist of the First Men (date est.)', -40, 600]],
    'asos': [['299 7 1', 'Catelyn frees Jaime; Brienne takes him south (date est.)', -30, -900], ['299 8 1', 'Daenerys takes Astapor and its Unsullied (date est.)', 2452, -2150],
             ['299 8 1', 'Jon and Bran pass within a mile of each other at Queenscrown, unknowing (date est.)', 70, 390],
             ['299 9 1', 'The Red Wedding at the Twins (date est.)', 40, -620], ['299 9 2', 'Sam and Gilly meet Bran beneath the Nightfort; Bran goes beyond the Wall (date est.)', -40, 452],
             ['299 9 10', 'Jaime loses his sword hand on the road; he and Brienne come to Harrenhal (date est.)', 130, -960],
             ['300 1 15', 'King Joffrey dies at his wedding feast; Sansa escapes the city (date est.)', 256, -1296], ['300 2 1', 'Daenerys takes Meereen (date est.)', 2702, -1965],
             ['300 2 10', 'Tyrion kills his father and flees (date est.)', 256, -1296], ['300 3 1', 'The free folk attack Castle Black; Stannis comes to the Wall (date est.)', 20, 452]],
    'feastdance': [['300 2 1', 'Arya reaches Braavos and the House of Black and White (date est.)', 775, -470], ['300 4 2', 'Samwell sails from Eastwatch for Oldtown (date est.)', 157, 458],
                   ['300 4 1', 'Bran reaches the cave of the three-eyed crow (date est.)', 40, 1000], ['300 5 20', 'Tyrion comes to Volantis on his way east (date est.)', 1420, -2200],
                   ['300 6 1', 'Theon, as Reek, comes back to Winterfell with the Boltons (date est.)', 0, 0], ['300 8 1', 'Jon sends men to the free folk at Hardhome (date est.)', 300, 640],
                   ['300 9 2', 'Drogon comes to Daznak\'s Pit; Daenerys flies away on his back (date est.)', 2705, -1962],
                   ['300 9 1', 'Winter comes: the Citadel sends out its white ravens (date est.)', -432, -2116]],
}

EXTRA_PLACES = [  # name, kind, x, y, people, realm, note, opts
    ('Darry', 'fortress', 190, -1010, 'river', 'The Riverlands', 'A castle on the Kingsroad south of the Trident.', {'rank': 5}),
    ('The Whispering Wood', 'landmark', -15, -870, 'river', 'The Riverlands', 'A wooded valley near Riverrun.', {'rank': 5}),
    ('Oxcross', 'landmark', -330, -1100, 'west', 'The Westerlands', 'A battlefield in the westerlands.', {'rank': 5}),
    ('Queenscrown', 'ruin', 70, 390, 'north', 'The Gift', 'A village with a tower on a lake island in the Gift.', {'rank': 5}),
    ('The cave of the three-eyed crow', 'cave', 40, 1000, 'free', 'Beyond the Wall', 'A cave beneath a hill of weirwoods, far beyond the Wall.', {'rank': 4}),
    ('The Quiet Isle', 'landmark', 290, -945, 'river', 'The Riverlands', 'An island of silent brothers at the mouth of the Trident.', {'rank': 5}),
    ('Gates of the Moon', 'fortress', 335, -778, 'vale', 'The Vale', 'The castle at the foot of the Giant\'s Lance.', {'rank': 5}),
    ('The Inn of the Kneeling Man', 'village', 205, -900, 'river', 'The Riverlands', 'An inn by the Trident.', {'rank': 5}),
    ('Acorn Hall', 'fortress', 40, -1040, 'river', 'The Riverlands', 'A castle in the southern riverlands.', {'rank': 5}),
    ('The House of Black and White', 'landmark', 775, -470, 'braavos', 'Braavos', 'A temple in Braavos.', {'rank': 4}),
    ('Daznak\'s Pit', 'landmark', 2705, -1962, 'ghiscari', 'Slaver\'s Bay', 'The great fighting pit of Meereen.', {'rank': 5}),
    ('A village of the Lamb Men', 'village', 2400, -1720, 'lhazar', 'The Dothraki Sea', 'A village of Lhazar.', {'rank': 5}),
    ('Skagos', 'landmark', 350, 500, 'north', 'The North', 'A wild island in the Bay of Seals.', {'rank': 5}),
    ('The Kingswood', 'landmark', 330, -1450, 'storm', 'The Stormlands', 'The royal forest south of the Blackwater.', {'rank': 5}),
]


# ------------------------------------------------------------------ building GEO.CAST, JOURNEYS, MODES and EVENTS
WOLF_NAMES = {'ghost': 'Ghost', 'greywind': 'Grey Wind', 'lady': 'Lady', 'nymeria': 'Nymeria', 'summer': 'Summer', 'shaggydog': 'Shaggydog'}
DRAGON_NAMES = {'drogon': 'Drogon', 'rhaegal': 'Rhaegal', 'viserion': 'Viserion'}
HOUSE_COLORS = [('Stark', '#c8ccd4'), ('Lannister', '#e0b040'), ('Baratheon', '#f0d030'), ('Targaryen', '#e04030'), ('Greyjoy', '#d8c060'), ('Tyrell', '#6ac050'),
                ('Tully', '#4a8ad8'), ('Bolton', '#e08a8a'), ('Night', '#6a6e76'), ('free folk', '#c87a4a'), ('beyond the Wall', '#7ad0ff'), ('Lord of Light', '#ff4020'),
                ('Seaworth', '#9aa0b0'), ('Tarth', '#5a8ae0'), ('Reed', '#7aa06a'), ('Dothraki', '#c9a03c'), ('Clegane', '#a0a090'), ('Baelish', '#6ab0a0'), ('Spider', '#a080c0')]
# dragons follow their mother from the pyre; Rhaegal and Viserion stay chained in Meereen when she flies off on Drogon
DERIVED = {'drogon': ('daenerys', '298 12 2', None), 'rhaegal': ('daenerys', '298 12 2', '300 9 1'), 'viserion': ('daenerys', '298 12 2', '300 9 1')}
DERIVED['bloodriders'] = ('daenerys', '298 12 2', None)
WHEELHOUSE = ['cersei']            # who rides in the queen's wheelhouse on the Kingsroad (the rest of the party rides beside it)


def name_of(k):
    c = CHARS[k]
    return WOLF_NAMES.get(k) or DRAGON_NAMES.get(k) or c['head']['name']


def color_of(k):
    h = CHARS[k]['house']
    for key, col in HOUSE_COLORS:
        if key in h: return col
    return '#d8c8a8'


def _poly_param(pl, P):
    """Nearest point on polyline pl to P -> (segment index, fraction, distance)."""
    best = (0, 0.0, 1e18)
    for i in range(len(pl) - 1):
        (ax, ay), (bx, by) = pl[i], pl[i + 1]; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9
        f = max(0.0, min(1.0, ((P[0] - ax) * dx + (P[1] - ay) * dy) / L2)); qx, qy = ax + dx * f, ay + dy * f
        d = math.hypot(P[0] - qx, P[1] - qy)
        if d < best[2]: best = (i, f, d)
    return best


def _sub(pl, a, b):
    """The stretch of polyline pl from parameter a to parameter b (either direction), ends included."""
    pt = lambda i, f: [pl[i][0] + (pl[i + 1][0] - pl[i][0]) * f, pl[i][1] + (pl[i + 1][1] - pl[i][1]) * f]
    (ia, fa, _), (ib, fb, _) = a, b
    if (ia, fa) <= (ib, fb): return [pt(ia, fa)] + [pl[i] for i in range(ia + 1, ib + 1)] + [pt(ib, fb)]
    return [pt(ia, fa)] + [pl[i] for i in range(ia, ib, -1)] + [pt(ib, fb)]


def _timed(pts, t0, t1):
    """Spread t0..t1 over the polyline by distance."""
    d = [0.0]
    for i in range(1, len(pts)): d.append(d[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    L = d[-1] or 1.0
    return [(p[0], p[1], t0 + (t1 - t0) * d[i] / L) for i, p in enumerate(pts)]


def expand(steps, XY, roads):
    out = []
    for s in steps:
        if s[0] == 'road':
            _, road, a, b, d0, d1 = s; pl = roads[road]; A, Bp = XY(a), XY(b)
            pts = [A] + _sub(pl, _poly_param(pl, A), _poly_param(pl, Bp)) + [Bp]
            out += _timed(pts, T(d0), T(d1))
        elif s[0] == 'lane':
            _, lane, d0, d1, back = s; out += _timed(SEA[lane][::-1] if back else SEA[lane], T(d0), T(d1))
        else:
            P = XY(s[0]); out.append((P[0], P[1], T(s[1])))
    # strictly increasing time; drop exact repeats
    res = []
    for x, y, t in out:
        if res and abs(res[-1][0] - x) < 1e-6 and abs(res[-1][1] - y) < 1e-6 and abs(res[-1][2] - t) < 1e-6: continue
        if res and t <= res[-1][2]: t = res[-1][2] + 0.01
        res.append((x, y, t))
    return res


def _clip(pts, a, b):
    """The part of a timed path inside [a, b], with the positions at the window's edges."""
    if not pts or pts[-1][2] < a or pts[0][2] > b: return []
    def at(t):
        for i in range(len(pts) - 1):
            if pts[i][2] <= t <= pts[i + 1][2]:
                f = (t - pts[i][2]) / ((pts[i + 1][2] - pts[i][2]) or 1)
                return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f, t)
        return pts[-1] if t >= pts[-1][2] else pts[0]
    s, e = max(a, pts[0][2]), min(b, pts[-1][2])
    mid = [p for p in pts if s < p[2] < e]
    res = [at(s)] + mid + ([at(e)] if e > s else [])
    return res


def build(places, roads, stories):
    """-> (CAST, JOURNEYS, MODES, EVENTS) for geo.js."""
    where = {p[0]: (p[2], p[3]) for p in places}
    def XY(v):
        if isinstance(v, str):
            if v not in where: raise SystemExit('cast: no place named ' + v)
            return list(where[v])
        return list(v)
    road = {r['name']: r['pts'] for r in roads}
    full = {}
    for k, steps in PATHS.items():
        if steps: full[k] = expand(steps, XY, road)
    for k, (src, d0, d1) in DERIVED.items():
        a, b = T(d0), T(d1) if d1 else 1e9
        pts = [p for p in full[src] if a <= p[2] <= b]
        if d1: pts.append((pts[-1][0], pts[-1][1], T('300 13 5')))
        full[k] = pts
    last = max(T(s['end']) for s in stories.values())
    JOURNEYS, JCAST = {}, {}
    for sk, st in stories.items():
        a, b = T(st['start']) - 0.5, T(st['end']) + 0.5
        JOURNEYS[sk], JCAST[sk] = [], {}
        for k in CHARS:
            if k not in full: continue
            pts = _clip(full[k], a, b)
            if len(pts) < 1: continue
            if len(pts) == 1: pts = pts + [(pts[0][0], pts[0][1], pts[0][2] + 0.01)]
            nm = name_of(k)
            j = {'name': nm, 'color': color_of(k), 'pts': [[round(x, 1), round(y, 1), round(t, 2)] for x, y, t in pts]}
            if full[k][-1][2] < last - 1: j['hide'] = 1         # dead or gone: no dot left behind
            JOURNEYS[sk].append(j)
            JCAST[sk][nm] = [c if isinstance(c, str) else [c[0], c[1], c[2]] for c in CASTS.get(k, [k])]
    # every sea lane is sailed: the leg along a LANE is 'sea' whatever else the traveller is doing that season
    lanes = [['^' + re.escape(k) + '$', s[2], s[3], 'sea'] for k, steps in PATHS.items() if 'dragon' not in CHARS[k]
             for s in (steps or []) if s[0] == 'lane']
    # MODES name journeys, not ids; the app takes the first match, so the narrowest window comes first
    # (a voyage inside a season on horseback), and the wheelhouse before the riders beside it
    modes = []
    for rx, d0, d1, mode in sorted(lanes + MODES, key=lambda m: (T(m[2]) - T(m[1]), m[3] != 'wheelhouse')):
        ids = [k for k in CHARS if k in full and re.search(rx, k)]
        if not ids: continue
        modes.append(['^(' + '|'.join(re.escape(name_of(k)) for k in ids) + ')$', d0, d1, mode])
    C, B, prof = {}, {}, {}
    for k, c in CHARS.items():
        if 'wolf' in c: C[k] = {'name': name_of(k), 'special': 'direwolf', 'fur': c['wolf']['fur'], 'eye': c['wolf']['eye']}
        elif 'dragon' in c: C[k] = {'name': name_of(k), 'special': 'kwdragon', 'pal': c['dragon']}
        else:
            C[k] = dict(c['head'])
            if c.get('body'): B[k] = c['body']
        if c['tier'] == 'hidden': continue
        prof[k] = {'name': name_of(k), 'tier': c['tier'], 'house': c['house'], 'bio': c.get('bio', ''), 'fate': c.get('fate', ''), 'color': color_of(k)}
    # where each character is, sampled daily, for the interactions panel (computed in the app)
    groups = []
    for g in GROUPS:
        g = dict(g)
        if 'when' in g: g['when'] = [T(g['when'][0]), T(g['when'][1])]
        groups.append(g)
    # the kingdoms' rulers, the dead, the battles and the fallen
    tt = lambda d: T(d) if d else None
    rulers = {r: [[role, cid, tt(a), tt(b), title] for role, cid, a, b, title in L] for r, L in RULERS.items()}
    crown = [[cid, tt(a), tt(b), title] for cid, a, b, title in CROWN]
    deaths = []
    for cid, d, spot, how in DEATHS:
        X, Y = XY(spot); deaths.append({'id': cid, 't': T(d), 'X': X, 'Y': Y, 'how': how, 'days': BODY_DAYS})
    battles = []
    for b in BATTLES:
        at = XY(b['at']); t0, t1 = T(b['frm']), T(b['to'])
        for sk, st in stories.items():
            if T(st['start']) - 0.5 <= t0 <= T(st['end']) + 0.5:
                battles.append({'name': b['name'], 'story': sk, 'at': at, 'from': t0, 'to': t1, 'src': b['src'], 'sides': b['sides'], 'outcome': b['outcome']})
    fallen = []
    for b in BATTLES:
        at = XY(b['at'])
        if b['name'] in FALLEN:
            d, days, units, spread = FALLEN[b['name']]
        else:
            days, share, spread = FALLEN_DEFAULT; d = b['to']
            units = [[k, max(1, round(n * share))] for sd in b['sides'] for k, n in sd['units'] if k not in ('giant', 'other')]
        fallen.append({'name': b['name'], 'X': at[0], 'Y': at[1], 't': T(d) if isinstance(d, str) else T(b['frm']), 'days': days, 'units': [u for u in units if u[1] > 0], 'spread': spread})
    onfoot = [k for k in CHARS if 'wolf' in CHARS[k] or 'dragon' in CHARS[k]] + ['others', 'threeeyed']
    CAST = {'C': C, 'B': B, 'JOURNEY': JCAST, 'GROUPS': groups, 'PROFILES': prof, 'ON_FOOT': onfoot, 'WHEELHOUSE': WHEELHOUSE,
            'RULERS': rulers, 'CROWN': crown, 'SEVEN': SEVEN, 'DEATHS': deaths, 'FALLEN': fallen,
            'IDS': {name_of(k): k for k in CHARS if k in full}}
    return CAST, JOURNEYS, modes, EVENTS, battles
