"""The named anchors of the coast of southern Westeros, from the Rills round to the North's east coast (MAP_V2 §3).

Only features the books name are anchors: a castle or town the novels set on the shore, a cape, a river's mouth,
and the head or mouth of a named water (Blazewater Bay, Ironman's Bay, the Whispering Sound, the Sea of Dorne,
the Bite). Their positions are read from the published maps (graded `map`: positions only). Nothing between them
comes from any map: tools/known/shores.py fills each stretch with a real Earth coastline, turned and scaled to run
from one anchor to the next (Natural Earth, public domain), and that line is ours. The two joins are where this
coast meets the North's (our own, bent from Britain); they are not anchors.

ANCHORS is frozen: tools/known/gate.py checks its count and checksum, and that the built coast passes within 0.1 mi
of every anchor. Change it only with the owner, then update FROZEN below (python3 tools/known/coast_fixed.py).

(name, (X, Y) in miles, X east and Y north of Winterfell, walking with the land on the left; the character of the
shore to the next anchor; why the name qualifies)
"""
SOUTH = [
    ('The Rills (join)', (-435.5, -160.7), 'stony', 'join'),
    ('Blazewater Bay, head', (-72.4, -360.1), 'marsh', 'named water'),
    ("Flint's Finger", (-255.3, -397.9), 'stony', 'castle on the shore'),
    ('Cape Kraken', (-424.8, -490.4), 'marsh', 'cape'),
    ("Ironman's Bay, head", (-57.1, -675.3), 'rocky', 'named water'),
    ('Seagard', (-308.9, -842.8), 'rocky', 'castle on the shore'),
    ('The Crag', (-341.2, -942.5), 'rocky', 'castle on the shore'),
    ('Kayce', (-461.9, -1203.9), 'rocky', 'town on the shore'),
    ('Lannisport', (-425.7, -1237.3), 'beach', 'port'),
    ('Old Oak', (-460.7, -1606.7), 'beach', 'castle on the shore'),
    ('The Mander, mouth', (-385.0, -1715.0), 'beach', 'river mouth'),
    ('Three Towers', (-508.3, -2017.1), 'beach', 'castle on the shore'),
    ('The Whispering Sound, north side', (-526.7, -2223.0), 'beach', 'named water'),
    ('Oldtown', (-442.1, -2202.0), 'beach', 'port at the head of the Whispering Sound'),
    ('The Whispering Sound, south side', (-489.4, -2303.7), 'beach', 'named water'),
    ('The Redwyne Straits', (-476.3, -2368.2), 'rocky', 'named water'),
    ('Starfall', (-234.9, -2404.1), 'dry', 'castle at the Torrentine\'s mouth'),
    ('Salt Shore', (390.3, -2452.1), 'dry', 'castle on the shore'),
    ('Lemonwood', (535.6, -2346.0), 'dry', 'castle on the shore'),
    ('The Greenblood, mouth', (545.2, -2307.3), 'dry', 'river mouth'),
    ('Sunspear', (595.7, -2237.0), 'dry', 'castle on the shore'),
    ('The Broken Arm', (626.1, -2005.7), 'dry', 'cape'),
    ('Ghost Hill', (524.4, -2112.0), 'dry', 'castle on the shore'),
    ('The Tor', (359.0, -2202.0), 'dry', 'castle on the shore'),
    ('The Sea of Dorne, west end', (160.3, -2138.7), 'rocky', 'named water'),
    ('Weeping Town', (452.2, -1946.4), 'rocky', 'town on the shore'),
    ('Cape Wrath', (537.8, -1824.8), 'rocky', 'cape'),
    ("Storm's End", (396.4, -1629.5), 'rocky', 'castle on the shore'),
    ("Massey's Hook", (495.7, -1212.7), 'beach', 'cape'),
    ('Stonedance', (451.4, -1279.2), 'beach', 'castle on the shore'),
    ("King's Landing", (267.7, -1305.7), 'beach', 'city at the Blackwater Rush\'s mouth'),
    ('Duskendale', (337.8, -1165.8), 'rocky', 'town on the shore'),
    ("Rook's Rest", (377.6, -1066.6), 'marsh', 'castle on the shore'),
    ('Crackclaw Point', (528.9, -999.2), 'marsh', 'cape'),
    ('Maidenpool', (294.7, -973.9), 'marsh', 'town on the shore'),
    ('The Trident, mouth', (225.2, -930.0), 'rocky', 'river mouth'),
    ('Gulltown', (515.5, -877.6), 'rocky', 'port'),
    ('Runestone', (568.4, -755.2), 'kerry', 'castle on the shore'),
    ('The Fingers', (590.0, -620.0), 'kerry', 'named peninsulas'),
    ('The Bite, head', (100.3, -515.8), 'rocky', 'named water'),
    ('White Harbor', (176.9, -326.0), 'rocky', 'port at the White Knife\'s mouth'),
    ('The north-east coast (join)', (392.1, -212.1), None, 'join'),
]
ANCHORS = [(n, xy) for n, xy, _, why in SOUTH if why != 'join']
FROZEN = {'count': 40, 'sha256': 'ae69806c4486920c304022baa38e9c4830eb26ae6a793d5ac81c138d09fcfc5e'}


def checksum():
    import hashlib
    return hashlib.sha256(';'.join(f'{n}:{x:.1f},{y:.1f}' for n, (x, y) in ANCHORS).encode()).hexdigest()


if __name__ == '__main__':
    print(len(ANCHORS), checksum())
