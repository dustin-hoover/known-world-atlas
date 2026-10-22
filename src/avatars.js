/* Pixel-art heads for the travellers, and group badges for parties that travel together.
   A head is composed on a 14×16 grid from parts (hair, beard, hat, ears) in a character's colours, given a
   one-pixel dark outline, and drawn at 3–4× with no smoothing. Parties within a mile or two of each other
   merge into one badge; a set of companions that matches a named group (a lord's party, a king's company…)
   gets that group's own design. The cast itself comes from the world (GEO.CAST). */
const AVATARS = (() => {
const W = 14, H = 16, OUT = '#16110d';
// [skin, hair, hairDark, beard, beardDark, hat, hatDark] — any may be null
const C = {};                                   // heads, filled from the world's cast (GEO.CAST)

// which characters travel in each journey; [id, from, to] limits a companion to part of the journey
const JOURNEY = {};
const P = s => typeof s === 'string' ? WX.parse(s) : s;
function charsOf(story, name, t) {
  const L = (JOURNEY[story] || {})[name] || [];
  return L.filter(c => typeof c === 'string' || ((c[1] == null || t >= P(c[1])) && (c[2] == null || t < P(c[2])))).map(c => typeof c === 'string' ? c : c[0]);
}

// Named companies, most specific first. `when` limits the name to the days it was true.
const has = (S, ...ids) => ids.every(i => S.has(i));
const GROUPS = [];

/* ---- one head on the 14×16 grid ---- */
function grid(id) {
  const c = C[id], g = Array.from({ length: H }, () => Array(W).fill(null));
  const set = (x, y, v) => { if (x >= 0 && x < W && y >= 0 && y < H && v) g[y][x] = v; };
  const rect = (x0, y0, x1, y1, v) => { for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) set(x, y, v); };
  const tex = (x, y, a, b) => ((x * 7 + y * 3) % 5 === 0 ? b : a);           // a little curl texture
  const [h, hd] = c.hair || [null, null];
  // hair behind the face
  if (c.style === 'long') { for (let y = 7; y < 16; y++) { set(2, y, tex(2, y, h, hd)); set(11, y, tex(11, y, h, hd)); } for (let y = 10; y < 16; y++) { set(1, y, h); set(12, y, hd); } }
  if (c.style === 'shaggy') for (let y = 7; y < 13; y++) { set(2, y, tex(2, y, h, hd)); set(11, y, tex(11, y, h, hd)); }
  if (c.style === 'short' || c.style === 'sides') for (let y = 7; y < 12; y++) { set(2, y, h); set(11, y, hd); }
  // face
  for (let y = 6; y <= 13; y++) for (let x = 3; x <= 10; x++) {
    if ((y === 6 || y === 13) && (x === 3 || x === 10)) continue;
    set(x, y, x === 10 || y === 13 ? shade(c.skin, 0.88) : c.skin);
  }
  // hair on top
  if (['curly', 'long', 'shaggy', 'short'].includes(c.style)) {
    rect(4, 3, 9, 3, h); rect(3, 4, 10, 4, h); rect(2, 5, 11, 6, h);
    for (let y = 3; y <= 6; y++) for (let x = 2; x <= 11; x++) if (g[y][x] === h) set(x, y, tex(x, y, h, hd));
    if (c.style === 'curly') { set(4, 2, h); set(6, 2, h); set(8, 2, hd); set(2, 7, h); set(11, 7, hd); set(2, 8, hd); set(11, 8, h); set(4, 7, h); set(6, 7, hd); set(8, 7, h); set(9, 7, h); }
    if (c.style === 'shaggy') { set(3, 7, h); set(4, 7, hd); set(9, 7, h); set(10, 7, hd); set(6, 7, h); }
    if (c.style === 'short') { set(3, 7, h); set(10, 7, hd); }
    if (c.style === 'long') { set(3, 7, h); set(10, 7, hd); }
  }
  // ears
  if (c.style !== 'long') { set(2, 9, c.skin); set(11, 9, shade(c.skin, 0.88)); }
  // eyes, brows, mouth, cheeks
  set(5, 9, c.eye || '#1a1410'); set(8, 9, c.eye || '#1a1410');
  if (c.brows) { const b = (c.beardC || c.hair)[1]; set(4, 8, b); set(5, 8, b); set(8, 8, b); set(9, 8, b); }
  set(6, 11, shade(c.skin, 0.7)); set(7, 11, shade(c.skin, 0.7));
  if (c.blush) { set(4, 10, '#e8968a'); set(9, 10, '#e8968a'); }
  if (c.wrinkles) { set(4, 8, shade(c.skin, 0.8)); set(9, 8, shade(c.skin, 0.8)); }
  // beards
  const [b, bd] = c.beardC || [null, null];
  if (c.beard === 'stubble') { for (let x = 4; x <= 9; x++) if (x % 2) set(x, 12, b); for (let x = 4; x <= 9; x++) set(x, 13, x % 2 ? bd : b); }
  if (c.beard === 'short') { set(5, 11, b); set(8, 11, b); set(3, 12, b); set(10, 12, bd); rect(4, 13, 9, 13, b); rect(5, 14, 8, 14, bd); set(6, 12, b); set(7, 12, b); }
  // hats
  if (c.hat === 'helm') { const m = '#9aa0a8', md = '#6b7078'; rect(5, 2, 8, 2, m); rect(4, 3, 9, 3, m); rect(3, 4, 10, 5, m); set(9, 3, md); set(10, 4, md); set(10, 5, md); rect(2, 6, 11, 6, '#c9a03c'); set(6, 7, md); set(7, 7, md); set(2, 7, b); set(11, 7, bd); set(2, 8, b); set(11, 8, bd); set(2, 9, b); set(11, 9, bd); }
  if (c.hat === 'crown') { const y1 = '#e6c04e', y2 = '#b08a2a'; rect(3, 4, 10, 4, y1); set(3, 3, y1); set(6, 2, y1); set(7, 2, y2); set(6, 3, y1); set(7, 3, y2); set(10, 3, y2); set(6, 4, '#3f8a5a'); set(7, 4, '#3f8a5a'); }
  if (c.hat === 'circlet') { const [a, d] = c.hatC; rect(3, 6, 10, 6, a); set(10, 6, d); set(6, 6, '#bfe3ff'); set(7, 6, '#ffffff'); }
  return g;
}
function shade(hex, f) { const n = parseInt(hex.slice(1), 16); const q = v => Math.min(255, Math.round(v * f)), r = q((n >> 16) & 255), g = q((n >> 8) & 255), b = q(n & 255); return '#' + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1); }

/* ---- bodies: a front-facing walk in four frames (0, 2 standing; 1 left foot up; 3 right foot up) ---- */
const B = {};                                   // bodies, filled from the world's cast
const FW = W + 4, FH = H + 14, BY = H - 1;   // figure grid: head at (2, 0), body from row BY
// a dragon in flight: wings beating, a golden belly, riders on its back, and a gout of fire when it burns
function dragonGrid(f, fire, pal, riders) {
  const W2 = fire ? 92 : 66, by = 22, g = blank(W2, 40), sc = pal ? pal[0] : '#b8361e', sd = pal ? pal[1] : '#6e1c10', mem = pal ? pal[2] : '#8a2a18', bone = pal ? shade(pal[1], 0.6) : '#3a0e08';
  const up = [-20, -6, 12, -6][f];
  const wing = (rx, tipX, dy, c) => { for (let x = tipX; x <= rx; x++) { const u = (rx - x) / (rx - tipX), y = Math.round(by + dy * u), th = 1 + Math.round(7 * Math.sin(Math.PI * Math.min(1, u * 1.1))); setp(g, x, y - 1, bone); rectp(g, x, y, x, y + th - (x % 6 === 0 ? 2 : 0), c); if (x % 7 === 0) for (let k = 0; k < th; k++) setp(g, x - k / 3, y + k, bone); } };
  wing(40, 10, up - 4, '#5e1a10');
  for (let i = 0; i < 20; i++) rectp(g, 1 + i, by + 4 + Math.round(Math.sin(i / 3 + f) * 2), 1 + i, by + 5 + Math.round(Math.sin(i / 3 + f) * 2) + (i > 12 ? 1 : 0), i % 3 ? sc : sd);
  rectp(g, 0, by + 3 + Math.round(Math.sin(f) * 2), 2, by + 6 + Math.round(Math.sin(f) * 2), sd);     // the tail's spade
  rectp(g, 20, by, 44, by + 7, sc); rectp(g, 22, by + 6, 42, by + 8, '#e0a040'); for (let x = 22; x <= 42; x += 2) setp(g, x, by + 7, '#ffd070');
  for (let i = 0; i < 10; i++) rectp(g, 43 + i, by + 1 - Math.round(i * 0.9), 45 + i, by + 3 - Math.round(i * 0.9), i % 3 ? sc : sd);
  const hx = 53, hy = by - 11;
  rectp(g, hx, hy, hx + 7, hy + 4, sc); rectp(g, hx + 8, hy + 2, hx + 11, hy + 4, sc); setp(g, hx + 5, hy + 1, '#ffd040'); setp(g, hx + 11, hy + 2, '#16110d');
  setp(g, hx + 1, hy - 1, '#e8dcc0'); setp(g, hx, hy - 2, '#e8dcc0'); setp(g, hx + 3, hy - 1, '#e8dcc0'); rectp(g, hx + 7, hy + 5, hx + 10, hy + 5, sd);
  for (const x of [26, 38]) { rectp(g, x, by + 9, x + 1, by + 11, sd); setp(g, x + 2, by + 12, '#e8dcc0'); setp(g, x - 1, by + 12, '#e8dcc0'); }
  if (fire) {
    const L = 26 + (f % 2) * 4;
    for (let i = 0; i < L; i++) { const w = 1 + Math.round(i * 0.28), y0 = hy + 4 + Math.round(i * 0.35); for (let k = -w; k <= w; k++) setp(g, hx + 12 + i, y0 + k, Math.abs(k) < w * 0.35 ? '#fff0a0' : Math.abs(k) < w * 0.7 ? '#ffb030' : ((i + k + f) % 3 ? '#ff6a18' : '#c02010')); }
  }
  (riders || []).forEach((id, i) => paste(g, upper(id, 0), 24 + i * 7, by - (BY + 6) - 1));
  wing(38, 6, up, mem);
  return g;
}
function figGrid(id, f) {
  if (C[id].special === 'direwolf') return direwolfGrid(id, f);
  if (C[id].special === 'kwdragon') return kwDragonGrid(id, f);
  const g = Array.from({ length: FH }, () => Array(FW).fill(null)), b = B[id] || {}, c = C[id];
  const set = (x, y, v) => { if (x >= 0 && x < FW && y >= 0 && y < FH && v) g[y][x] = v; };
  const rect = (x0, y0, x1, y1, v) => { for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) set(x, y, v); };
  const R = r => BY + r, skin = c.skin || '#2a2a33';
  const upL = f === 1 ? 1 : 0, upR = f === 3 ? 1 : 0;          // which foot is lifted
  const armL = f === 1 ? 1 : f === 3 ? -1 : 0, armR = -armL;    // arms swing opposite the legs
  // behind the body: cloak, pack, bow
  if (b.cloak) { rect(5, R(1), 12, R(10), b.cloak); for (let r = 3; r <= 9; r++) { set(3, R(r), shade(b.cloak, 0.8)); set(14, R(r), shade(b.cloak, 0.7)); } rect(4, R(2), 4, R(10), b.cloak); rect(13, R(2), 13, R(10), shade(b.cloak, 0.85)); }
  if (b.gear === 'pack') { rect(13, R(0), 15, R(5), '#7a5a32'); set(15, R(0), '#9aa0a8'); set(16, R(1), '#9aa0a8'); }
  if (b.gear === 'bow') { for (let r = -2; r <= 9; r++) set(r < 1 || r > 6 ? 3 : 2, R(r), '#8a6234'); for (let r = -1; r <= 8; r++) set(4, R(r), '#e8e2d0'); }
  if (b.robe) {
    const o = b.robe, d = shade(o, 0.78);
    rect(6, R(0), 11, R(6), o); rect(5, R(1), 12, R(2), o);
    rect(5, R(7), 12, R(9), o); const sw = f === 1 ? -1 : f === 3 ? 1 : 0;
    rect(4 + sw, R(10), 13 + sw, R(11), o); for (let x = 4 + sw; x <= 13 + sw; x++) set(x, R(11), d);
    for (let r = 1; r <= 10; r++) set(11 + (r > 6 ? 1 : 0), R(r), d);
    if (b.belt) rect(6, R(4), 11, R(4), b.belt);
    // feet peeping out under the hem
    const foot = '#5a4a3a';
    if (f !== 3) rect(6, R(12), 7, R(12), foot); if (f !== 1) rect(10, R(12), 11, R(12), foot);
    // sleeves and hands
    rect(4, R(2 + armL), 5, R(5 + armL), o); set(4, R(6 + armL), skin);
    rect(12, R(2 + armR), 13, R(5 + armR), d); set(13, R(6 + armR), skin);
  } else {
    // legs (behind the tunic's hem), then the tunic, belt and arms
    const legs = b.legs || '#5a4a3a', boot = b.boots;
    rect(6, R(7), 11, R(7), legs);
    rect(6, R(8), 7, R(11 - upL), legs); rect(10, R(8), 11, R(11 - upR), shade(legs, 0.85));
    {
      rect(5, R(12 - upL), 7, R(12 - upL), boot || '#3a2a1a'); rect(10, R(12 - upR), 12, R(12 - upR), boot || '#3a2a1a');
      if (boot) { set(6, R(11 - upL), boot); set(7, R(11 - upL), boot); set(10, R(11 - upR), boot); set(11, R(11 - upR), boot); }
    }
    const t = b.tunic, td = shade(t, 0.8), fx = b.fat ? 1 : 0;
    rect(6 - fx, R(0), 11 + fx, R(7), t); rect(5 - fx, R(1), 12 + fx, R(2), t); for (let r = 1; r <= 7; r++) set(11 + fx, R(r), td);
    if (b.fat) rect(4, R(3), 13, R(5), t);
    if (b.mail) for (let r = 1; r <= 7; r++) for (let x = 6; x <= 11; x++) if ((x + r) % 2) set(x, R(r), shade(t, 0.82));
    rect(6, R(5), 11, R(5), b.belt || shade(t, 0.55));
    rect(4, R(2 + armL), 5, R(5 + armL), t); set(4, R(6 + armL), skin); set(5, R(6 + armL), skin);
    rect(12, R(2 + armR), 13, R(5 + armR), td); set(12, R(6 + armR), shade(skin, 0.9)); set(13, R(6 + armR), shade(skin, 0.9));
  }
  // carried things, in front
  if (b.gear === 'staff') { const y0 = R(6 + armR); for (let y = 4; y <= R(12); y++) set(14, y, b.staff); set(14, 3, shade(b.staff, 1.2)); set(15, 4, b.staff); set(13, 4, b.staff); set(13, y0, skin); }
  if (b.gear === 'axe') { const y0 = R(6 + armR); for (let y = y0 - 7; y <= y0 + 1; y++) set(14, y, '#6b4a2a'); rect(15, y0 - 7, 16, y0 - 4, '#c8ccd4'); set(16, y0 - 7, '#9aa0a8'); set(16, y0 - 4, '#9aa0a8'); set(15, y0 - 3, '#9aa0a8'); }
  if (b.gear === 'sword') { set(5, R(4), '#c9a03c'); set(4, R(4), '#c9a03c'); for (let r = 5; r <= 9; r++) set(4 + (r > 7 ? -1 : 0), R(r), '#d6dae2'); }
  if (b.gear === 'shield') { rect(2, R(2 + armL), 5, R(6 + armL), '#6b2a2a'); set(2, R(2 + armL), null); set(5, R(2 + armL), null); set(2, R(6 + armL), null); set(5, R(6 + armL), null); set(3, R(4 + armL), '#d9d4c8'); set(4, R(4 + armL), '#d9d4c8'); }
    rect(3, R(3 + armL), 3, R(5 + armL), '#f0f0ea'); set(2, R(3 + armL), '#f0f0ea'); set(4, R(3 + armL), '#f0f0ea'); set(2, R(4 + armL), '#f0f0ea'); set(4, R(4 + armL), '#f0f0ea'); set(3, R(2 + armL), '#f0f0ea');   // the White Hand
  // the head on top (beards fall over the chest)
  const hg = GCACHE[id] || (GCACHE[id] = grid(id));
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (hg[y][x]) set(x + 2, y, hg[y][x]);
  return g;
}
// draw a grid with a one-pixel dark outline at (x, y), each grid pixel s×s
function drawGrid(ctx, g, x, y, s) {
  const h = g.length, w = g[0].length;
  ctx.fillStyle = OUT;
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (g[j][i]) for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
    const a = i + dx, b = j + dy; if (a < 0 || a >= w || b < 0 || b >= h || !g[b][a]) ctx.fillRect(x + (a + 1) * s, y + (b + 1) * s, s, s);
  }
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (g[j][i]) { ctx.fillStyle = g[j][i]; ctx.fillRect(x + (i + 1) * s, y + (j + 1) * s, s, s); }
}
const GCACHE = {}, FCACHE = {};
function drawHead(ctx, id, x, y, s) { drawGrid(ctx, GCACHE[id] || (GCACHE[id] = grid(id)), x, y, s); }
function drawFigure(ctx, id, x, y, s, f) { const k = id + f; drawGrid(ctx, FCACHE[k] || (FCACHE[k] = figGrid(id, f)), x, y, s); }
const HW = (W + 2), HH = (H + 2), FIGW = FW + 2, FIGH = FH + 2;    // sizes in grid pixels, outline included

function roundRect(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
function emblem(g, kind, cx, cy, r, edge) {
  g.save(); g.lineWidth = Math.max(2, r * 0.22);
  if (kind === 'web') {
    g.strokeStyle = edge; g.lineWidth = 1.2; for (let k = 0; k < 6; k++) { const a = k * Math.PI / 3; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r * 0.7); g.stroke(); }
    for (const q of [0.45, 0.85]) { g.beginPath(); g.ellipse(cx, cy, r * q, r * q * 0.7, 0, 0, 7); g.stroke(); }
  } else if (kind === 'hand') {
    g.fillStyle = edge; g.fillRect(cx - r * 0.45, cy - r * 0.2, r * 0.9, r * 0.8); for (let k = 0; k < 4; k++) g.fillRect(cx - r * 0.45 + k * r * 0.24, cy - r * (0.75 - Math.abs(k - 1.5) * 0.12), r * 0.17, r * 0.6); g.fillRect(cx + r * 0.42, cy, r * 0.3, r * 0.17);
  } else if (kind === 'eye') {
    g.fillStyle = '#ff6a2c'; g.beginPath(); g.ellipse(cx, cy, r, r * 0.42, 0, 0, 7); g.fill(); g.fillStyle = '#120a0a'; g.fillRect(cx - 1.5, cy - r * 0.4, 3, r * 0.8);
  } else if (kind === 'star') {
    g.fillStyle = edge; g.beginPath(); for (let k = 0; k < 10; k++) { const a = k * Math.PI / 5 - Math.PI / 2, q = k % 2 ? r * 0.42 : r; g.lineTo(cx + Math.cos(a) * q, cy + Math.sin(a) * q); } g.fill();
  } else if (kind === 'leaf') {
    g.fillStyle = '#7fb84a'; g.beginPath(); g.ellipse(cx, cy, r * 0.55, r, 0.6, 0, 7); g.fill(); g.strokeStyle = '#3d6a22'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(cx - r * 0.45, cy + r * 0.6); g.lineTo(cx + r * 0.45, cy - r * 0.6); g.stroke();
  } else if (kind === 'key') {
    g.strokeStyle = edge; g.beginPath(); g.arc(cx - r * 0.5, cy, r * 0.35, 0, 7); g.moveTo(cx - r * 0.15, cy); g.lineTo(cx + r, cy); g.moveTo(cx + r * 0.7, cy); g.lineTo(cx + r * 0.7, cy + r * 0.35); g.moveTo(cx + r * 0.95, cy); g.lineTo(cx + r * 0.95, cy + r * 0.3); g.stroke();
  } else if (kind === 'horse') {
    g.fillStyle = edge; g.beginPath(); g.moveTo(cx - r, cy + r * 0.5); g.lineTo(cx - r * 0.2, cy - r * 0.2); g.lineTo(cx + r * 0.2, cy - r * 0.8); g.lineTo(cx + r, cy - r * 0.3); g.lineTo(cx + r * 0.4, cy); g.lineTo(cx + r * 0.6, cy + r * 0.5); g.closePath(); g.fill();
  }
  g.restore();
}

/* ---- mounts: side-view sprites facing right (the map mirrors them when a party heads west on screen) ---- */
const HORSES = [['#7a5232', '#50351f'], ['#a0704a', '#6e4a2e'], ['#5a3e2a', '#3a2818'], ['#c8b090', '#9a8466'], ['#5c5c66', '#3a3a42'], ['#eef2f6', '#c4ccd8']];   // bay, chestnut, brown, dun, grey, white
/* ---- the world's own cast (GEO.CAST, written by its author script) ---- */
const CAST = (typeof GEO !== 'undefined' && GEO.CAST) || null;
const WHEEL = new Set(CAST ? CAST.WHEELHOUSE : []), SOLO = new Set();
if (CAST) {
  Object.assign(C, CAST.C); Object.assign(B, CAST.B);
  for (const k in JOURNEY) delete JOURNEY[k]; Object.assign(JOURNEY, CAST.JOURNEY);
  GROUPS.unshift(...CAST.GROUPS.map(g => ({ ...g, test: S => (!g.solo || S.size === 1) && g.all.every(i => S.has(i)) })));
  for (const g of CAST.GROUPS) if (g.solo) g.all.forEach(i => SOLO.add(i));
}
// a direwolf: a great wolf, long-legged and deep-chested, in its own fur and eye colours
function direwolfGrid(id, f) {
  const [w0, w1] = C[id].fur, w2 = shade(w0, 1.12), eye = C[id].eye, Wd = 26, Ht = 16, g = blank(Wd, Ht), a = f % 2;
  rectp(g, 5, 5, 18, 10, w0); rectp(g, 6, 4, 17, 4, w1); for (let x = 6; x <= 17; x += 2) setp(g, x, 3, w1); rectp(g, 6, 10, 17, 10, w1);
  rectp(g, 17, 2, 23, 7, w0); rectp(g, 22, 5, 25, 7, w2); setp(g, 19, 1, w1); setp(g, 21, 1, w1); setp(g, 19, 0, w1); setp(g, 20, 4, eye); setp(g, 25, 5, '#16110d'); rectp(g, 23, 8, 25, 8, w1);
  rectp(g, 16, 7, 18, 10, w2);                                                        // ruff at the throat
  for (let i = 0; i < 5; i++) setp(g, 4 - i, 5 + Math.round(i * 0.6) - (a && i > 2 ? 1 : 0), i % 2 ? w0 : w1); setp(g, 0, 8 - a, w1);
  for (const [x, ph] of [[6, 0], [9, 1], [15, 1], [18, 0]]) rectp(g, x + (ph === a ? 1 : 0), 11, x + 1 + (ph === a ? 1 : 0), 15 - (ph === a ? 1 : 0), w1);
  return g;
}
// a young dragon on the ground, wings half raised, in its own scales (pal: scales, dark, wings)
function kwDragonGrid(id, f) {
  const [sc, sd, ac] = C[id].pal, g = blank(22, 16), a = f % 2;
  for (let i = 0; i < 7; i++) setp(g, i, 12 - Math.round(i * 0.4) + (i < 2 && a ? -1 : 0), i % 2 ? sc : sd);
  for (let x = 7; x <= 13; x++) { const top = 1 + Math.abs(x - 9) + a; rectp(g, x, top, x, 7, x % 3 ? ac : sd); }
  rectp(g, 6, 8, 14, 12, sc); rectp(g, 7, 12, 13, 12, shade(ac, 1.1));
  rectp(g, 14, 5, 15, 9, sc); rectp(g, 15, 3, 19, 6, sc); rectp(g, 20, 5, 21, 6, sc); setp(g, 17, 4, '#ffd040'); setp(g, 15, 2, '#e8dcc0'); setp(g, 16, 1, '#e8dcc0'); setp(g, 21, 5, '#16110d');
  rectp(g, 8, 13, 9, 15 - a, sd); rectp(g, 12, 13, 13, 15 - (1 - a), sd);
  return g;
}
// the queen's great wheelhouse: a long painted carriage on wheels, its passengers at the windows, the team in front
function wheelhouseGrid(ids, f) {
  const horse = horseGrid([], f, 1), Ht = horse.length, n = Math.max(1, Math.min(3, ids.length)), bw = 8 + 17 * n, g = blank(bw + horse[0].length - 2, Ht);
  const wood = '#7a4a24', woodD = '#4e2e14', gold = '#e0b040', red = '#a8281e', top = 4, bot = Ht - 7;
  rectp(g, 1, top - 3, bw - 1, top - 2, red); rectp(g, 0, top - 1, bw, top - 1, gold);
  rectp(g, 1, top, bw - 1, bot, wood); for (let x = 3; x < bw; x += 5) rectp(g, x, bot - 3, x, bot, woodD); rectp(g, 1, bot, bw - 1, bot, gold);
  ids.slice(0, 3).forEach((id, i) => { const wx = 4 + i * 17; rectp(g, wx, top + 1, wx + 15, top + 16, '#2a1a10'); paste(g, GCACHE[id] || (GCACHE[id] = grid(id)), wx + 1, top + 1);
    rectp(g, wx - 1, top + 1, wx - 1, top + 16, gold); rectp(g, wx + 16, top + 1, wx + 16, top + 16, gold); });
  for (const cx of [7, bw - 7]) {                                                     // wheels turning
    const cy = Ht - 5;
    for (let k = 0; k < 24; k++) { const an = k / 24 * Math.PI * 2; setp(g, cx + Math.cos(an) * 4, cy + Math.sin(an) * 4, woodD); }
    for (let k = 0; k < 4; k++) { const an = (k / 4 + f / 16) * Math.PI * 2; for (let r = 0; r < 4; r++) setp(g, cx + Math.cos(an) * r, cy + Math.sin(an) * r, gold); }
  }
  rectp(g, bw, bot - 6, bw + 4, bot - 6, '#3a2a1a');                                  // the traces
  paste(g, horse, bw - 3, 0);
  return g;
}
function blank(w, h) { return Array.from({ length: h }, () => Array(w).fill(null)); }
function paste(g, src, ox, oy, maxRow = 1e9) { for (let y = 0; y < src.length && y <= maxRow; y++) for (let x = 0; x < src[0].length; x++) if (src[y][x]) { const X = x + ox, Y = y + oy; if (Y >= 0 && Y < g.length && X >= 0 && X < g[0].length) g[Y][X] = src[y][x]; } }
function setp(g, x, y, v) { x = Math.round(x); y = Math.round(y); if (y >= 0 && y < g.length && x >= 0 && x < g[0].length && v) g[y][x] = v; }
function rectp(g, x0, y0, x1, y1, v) { for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) setp(g, x, y, v); }
// the rider's head and torso (no legs), from the walking figure
const upper = (id, f) => figGrid(id, f === 1 || f === 3 ? 0 : 0).map((row, y) => y <= BY + 6 ? row : row.map(() => null));

// a horse and its riders: 26 wide; the horse's back is at row BY + 6
function horseGrid(ids, f, k) {
  const W2 = 28, top = BY + 6, g = blank(W2, top + 12), hy = top - 1;           // hy: horse body top row
  const [c0, c1] = HORSES[k % HORSES.length], s = 1, eye = '#16110d';
  // tail
  for (let y = 0; y <= 6; y++) setp(g, 4 - (y > 3 ? 1 : 0) + (f % 2 && y > 4 ? 1 : 0), hy + 1 + y, c1); setp(g, 5, hy + 1, c1);
  // body
  rectp(g, 6, hy + 1, 19 + s, hy + 6, c0); rectp(g, 7, hy, 18 + s, hy, c0); rectp(g, 7, hy + 7, 18 + s, hy + 7, c1);
  // neck and head
  for (let y = 0; y < 6 + s; y++) rectp(g, 17 + s + Math.floor(y / 2), hy - y, 19 + s + Math.floor(y / 2), hy - y, c0);
  const hx = 20 + s + Math.floor((5 + s) / 2), hy2 = hy - 5 - s;
  rectp(g, hx - 1, hy2, hx + 2, hy2 + 2, c0); rectp(g, hx + 1, hy2 + 3, hx + 3, hy2 + 4, c0); setp(g, hx + 3, hy2 + 4, c1);
  setp(g, hx - 1, hy2 - 1, c0); setp(g, hx, hy2 - 1, c1); setp(g, hx + 1, hy2 + 1, eye);
  for (let y = 0; y < 6 + s; y++) setp(g, 17 + s + Math.floor(y / 2) - 1, hy - y, c1);     // mane
  // legs: a trot, diagonal pairs swinging
  const legs = [[7, 1], [9, 3], [16 + s, 3], [18 + s, 1]];
  for (const [lx, ph] of legs) {
    const lift = f === ph ? 1 : 0, sw = f === ph ? 1 : f === (ph + 2) % 4 ? -1 : 0;
    rectp(g, lx + sw, hy + 8, lx + sw, hy + 10 - lift, lx < 12 ? c1 : c0); setp(g, lx + sw, hy + 11 - lift, '#2a2420');
  }
  // tack
  rectp(g, 10, hy, 14, hy + 2, '#7a2a24'); setp(g, hx + 1, hy2 + 2, '#3a2a1a');
  // riders: the last is in front
  ids.forEach((id, i) => {
    const ox = 3 + (ids.length - 1 - i) * -4 + (ids.length > 1 ? 4 : 0), bob = f % 2 ? 0 : 1;
    paste(g, upper(id, 0), ox, bob - 1);
    const b = B[id] || {}; const leg = b.legs || b.robe || '#5a4a3a';
    rectp(g, ox + 9, hy + 2 + bob - 1, ox + 10, hy + 5 + bob - 1, leg); setp(g, ox + 9, hy + 6 + bob - 1, b.boots || '#3a2a1a');
  });
  return g;
}


// boats: a river boat with oars, or a sailing ship with its mast and sail
function boatGrid(ids, f, kind) {
  const n = ids.length, bob = f === 1 ? -1 : f === 3 ? 1 : 0;
  const big = kind !== 'boat', W2 = Math.max(30, 9 * n + 18) + (big ? 6 : 0), deck = BY + 6 + (big ? 6 : 0), g = blank(W2, deck + 9);
  const hull = kind === 'sea' ? ['#8a5a32', '#5e3c1e'] : ['#b8b4a8', '#8e897c'];
  if (big) {           // mast and sail
    const mx = Math.round(W2 / 2), sc = '#f6f4ee';
    rectp(g, mx, 1, mx, deck, '#6b4a2a'); rectp(g, mx - 9, 3, mx + 9, 3, '#6b4a2a');
    for (let y = 4; y <= deck - 6; y++) { const w = 8 + (y < 10 ? 1 : 0) - (f % 2 && y > deck - 9 ? 1 : 0); rectp(g, mx - w, y, mx + w, y, sc); }
  }
  ids.forEach((id, i) => paste(g, upper(id, 0), 4 + i * 9 + (big ? 3 : 0), deck - (BY + 6) + bob + 2));
  // the hull, with a raised stem at the bow
  for (let y = 0; y < 4; y++) rectp(g, 2 + y, deck + y + bob, W2 - 3 - y * 2, deck + y + bob, y < 2 ? hull[0] : hull[1]);
  rectp(g, 1, deck - 1 + bob, W2 - 2, deck - 1 + bob, kind === 'sea' ? '#c9a03c' : hull[1]);
  rectp(g, W2 - 3, deck - 3 + bob, W2 - 2, deck + bob, hull[0]);
  // oars and water
  if (kind === 'boat') for (let i = 0; i < n; i++) { const x = 8 + i * 9; setp(g, x + (f % 2), deck + 2 + bob, '#8a6234'); setp(g, x + 1 + (f % 2), deck + 3 + bob, '#8a6234'); }
  rectp(g, 0, deck + 5, W2 - 1, deck + 5, '#9ac4e0'); for (let x = f % 2; x < W2; x += 3) setp(g, x, deck + 6, '#cfe6f4');
  return g;
}

/* An icon for one party: a single walker on a coin of the journey's colour, or a company on its own
   token. f is the walk frame (0–3); companions step out of time with each other. Canvas pixels are at 2×
   (addImage with pixelRatio 2). Returns { canvas, name, key }. */
const ICACHE = {};
function groupOf(ids, t) {
  const S = new Set(ids);
  return ids.length > 1 || SOLO.has(ids[0]) ? GROUPS.find(G => G.test(S) && (!G.when || (t >= P(G.when[0]) && t <= P(G.when[1])))) : null;
}
// folk who never sit a horse: in a riding party they go on foot beside it
const ON_FOOT = new Set();
if (CAST) CAST.ON_FOOT.forEach(i => ON_FOOT.add(i));
function icon(ids, color, t, f = 0, mode = 'walk', flip = false) {
  if (mode === 'ride' && ids.every(i => ON_FOOT.has(i))) mode = 'walk';
  const S = new Set(ids), grp = groupOf(ids, t);
  const key = (grp ? grp.name : '') + '|' + [...S].sort().join(',') + '|' + color + '|' + mode + (flip ? '|w' : '');
  if (ICACHE[key + f]) return ICACHE[key + f];
  if (mode !== 'walk' && mode !== 'under') return ICACHE[key + f] = mounted(ids, S, grp, color, f, mode, flip, key);
  const cv = document.createElement('canvas'), g = cv.getContext('2d'), s = 3, fw = FIGW * s;
  const show = grp && grp.show ? grp.show.concat([...S].filter(i => !grp.show.includes(i))) : grp && grp.order ? grp.order.filter(i => S.has(i)).concat([...S].filter(i => !grp.order.includes(i))) : [...S];
  const hOf = id => (figGrid(id, 0).length + 2) * s, fh = Math.max(...show.map(hOf)), wOf = id => (figGrid(id, 0)[0].length + 2) * s;
  let two = show.length > 5, back = two ? show.slice(0, Math.floor(show.length / 2)) : [], front = two ? show.slice(back.length) : show;
  if (two && grp && grp.lead) {
    // the scene's leading figures stand front and centre, the rest of the company behind and around them
    const lead = grp.lead.filter(i => S.has(i)), rest = show.filter(i => !lead.includes(i)), nf = Math.max(lead.length, Math.ceil(show.length / 2));
    const side = rest.slice(0, nf - lead.length), half = Math.floor(side.length / 2);
    front = side.slice(0, half).concat(lead, side.slice(half)); back = rest.slice(nf - lead.length);
  }
  // figures overlap their neighbours by a share of their own width (the great ones take more room)
  const xsOf = row => { const xs = [0]; for (let k = 1; k < row.length; k++) xs.push(xs[k - 1] + Math.round(wOf(row[k - 1]) * (C[row[k - 1]].special ? 0.8 : 0.56))); return xs; };
  const step = Math.round(fw * 0.56), rowW = row => row.length ? xsOf(row)[row.length - 1] + wOf(row[row.length - 1]) : 0;
  const lift = two ? Math.round(fh * 0.2) : 0, width = Math.max(rowW(front), rowW(back) + step / 2);
  const padX = show.length === 1 ? 10 : 22, baseH = show.length === 1 ? 22 : 30;
  cv.width = width + padX * 2; cv.height = fh + lift + baseH / 2 + 6;
  const cx = cv.width / 2, by = cv.height - baseH / 2 - 3, rx = cv.width / 2 - 3, ry = baseH / 2;
  const frame = grp ? grp.frame : '#141a22', edge = grp ? grp.edge : color;
  // the token they stand on
  {
    g.fillStyle = show.length === 1 ? color : frame; g.strokeStyle = OUT; g.lineWidth = 3;
    g.beginPath(); g.ellipse(cx, by, rx, ry, 0, 0, 7); g.fill(); g.stroke();
    if (show.length > 1) { g.strokeStyle = edge; g.lineWidth = 2.5; g.beginPath(); g.ellipse(cx, by, rx - 5, ry - 4, 0, 0, 7); g.stroke(); }
    g.fillStyle = 'rgba(255,255,255,0.25)'; g.beginPath(); g.ellipse(cx, by - ry * 0.35, rx * 0.7, ry * 0.3, 0, 0, 7); g.fill();
  }
  const x0 = (cv.width - rowW(back)) / 2, x1 = (cv.width - rowW(front)) / 2, foot = by + ry * (two ? 0.35 : 0.15), xb = xsOf(back), xf = xsOf(front);
  back.forEach((id, k) => drawFigure(g, id, x0 + xb[k], foot - hOf(id) - lift, s, (f + k * 2 + 1) % 4));
  front.forEach((id, k) => drawFigure(g, id, x1 + xf[k], foot - hOf(id), s, (f + k * 2) % 4));
  if (grp && grp.emblem) emblem(g, grp.emblem, cx, by + ry * 0.35, 8, edge);
  const name = grp ? grp.name : show.length === 1 ? C[show[0]].name : listNames(show);
  return ICACHE[key + f] = { canvas: cv, name, key };
}
// riders, dragons and sailors: one horse per rider, a dragon with its riders, a boat's crew in boats of three or
// five; a company's name and colours as on foot
function mounted(ids, S, grp, color, f, mode, flip, key) {
  const show = grp && grp.show ? grp.show.concat([...S].filter(i => !grp.show.includes(i))) : (grp && grp.order ? grp.order.filter(i => S.has(i)).concat([...S].filter(i => !grp.order.includes(i))) : [...S]);
  let units = [];
  if (mode === 'ride') {
    const walkers = show.filter(i => ON_FOOT.has(i));
    const rest = show.filter(i => !ON_FOOT.has(i));
    units = units.concat(rest.map(i => [i])).map((u, k) => horseGrid(u, (f + k) % 4, k)).concat(walkers.map((i, k) => Object.assign(figGrid(i, (f + k + 1) % 4).slice(), { walker: true })));
  } else if (mode === 'dragon') {     // a dragon with its rider; the other dragons fly alongside
    const drag = show.filter(i => C[i].special === 'kwdragon'), riders = show.filter(i => C[i].special !== 'kwdragon');
    units = (drag.length ? drag : ['drogon']).map((d, k) => dragonGrid((f + k) % 4, false, C[d] && C[d].pal, k === 0 ? riders : []));
  } else if (mode === 'wheelhouse') {
    const inside = show.filter(i => WHEEL.has(i)), out = show.filter(i => !WHEEL.has(i) && !ON_FOOT.has(i)), walkers = show.filter(i => ON_FOOT.has(i));
    units = [wheelhouseGrid(inside.length ? inside : show.slice(0, 1), f)].concat(out.filter(i => !inside.includes(i)).map((i, k) => horseGrid([i], (f + k + 1) % 4, k)), walkers.map((i, k) => Object.assign(figGrid(i, (f + k + 1) % 4).slice(), { walker: true })));
  }
  else if (mode === 'boat') {
    const crews = [], per = show.length > 8 ? 5 : 3; for (let i = 0; i < show.length; i += per) crews.push(show.slice(i, i + per));
    units = crews.map((c, k) => boatGrid(c, (f + k) % 4, 'boat'));
  } else units = [boatGrid(show, f, 'sea')];
  const s = 3, ws = units.map(u => (u[0].length + 2) * s), hs = units.map(u => (u.length + 2) * s), many = units.length > 5;
  const step = units.length > 1 ? Math.round(Math.max(...ws) * (many ? (mode === 'fly' ? 0.42 : 0.32) : mode === 'fly' ? 0.5 : 0.62)) : 0, lift = units.length > 1 ? (many ? 12 : 10) : 0;
  const liftOf = j => units[j].walker ? 0 : many ? ((units.length - 1 - j) % 2) * lift : (units.length - 1 - j) * lift;
  const cv = document.createElement('canvas'), g = cv.getContext('2d');
  cv.width = Math.max(...ws) + step * (units.length - 1) + 16; cv.height = Math.max(...hs) + (many ? lift : lift * (units.length - 1)) + (mode === 'fly' || mode === 'fire' || mode === 'dragon' ? 26 : 12);
  const cx = cv.width / 2, by = cv.height - 8;
  // ground under a rider: a small token; under a flyer: its shadow far below
  if (mode === 'ride' || mode === 'wheelhouse') { g.fillStyle = grp ? grp.frame : color; g.strokeStyle = OUT; g.lineWidth = 3; g.beginPath(); g.ellipse(cx, by, cv.width / 2 - 4, 7, 0, 0, 7); g.fill(); g.stroke(); }
  if (mode === 'fly' || mode === 'fire' || mode === 'dragon') { g.fillStyle = 'rgba(0,0,0,0.28)'; g.beginPath(); g.ellipse(cx, by, cv.width * 0.3, 5, 0, 0, 7); g.fill(); g.fillStyle = color; g.beginPath(); g.arc(cx, by, 4, 0, 7); g.fill(); }
  g.save(); if (flip) { g.translate(cv.width, 0); g.scale(-1, 1); }
  units.forEach((_, k) => { const j = units.length - 1 - k; drawGrid(g, units[j], 8 + j * step, by - (mode === 'fly' || mode === 'fire' || mode === 'dragon' ? 20 : 4) - hs[j] - liftOf(j) + (mode === 'fly' || mode === 'fire' || mode === 'dragon' ? 0 : 6), s); });
  g.restore();
  const name = grp ? grp.name : show.length === 1 ? C[show[0]].name : listNames(show);
  return { canvas: cv, name, key };
}

/* ---- the dead: a body lying where it fell, a dark pool beneath, and a death mark above ---- */
const SKULL = ['.#####.', '#######', '#..#..#', '#######', '.##.##.', '.#.#.#.'];
const pale = v => { if (!v) return v; const n = parseInt(v.slice(1, 7), 16), r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255, m = (r + g + b) / 3;
  const q = c => Math.round(c * 0.62 + m * 0.38).toString(16).padStart(2, '0'); return '#' + q(r) + q(g) + q(b); };
function lying(g, special) {
  if (special) return g.map(row => row.map(pale)).reverse();          // a beast on its back
  const h = g.length, w = g[0].length, out = blank(h, w);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (g[y][x]) out[w - 1 - x][y] = pale(g[y][x]);
  return out;
}
function deathMark(g, cx, cy, r) {
  g.fillStyle = 'rgba(10,6,6,0.88)'; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.fill();
  g.strokeStyle = '#c8b8a8'; g.lineWidth = 1.5; g.stroke();
  const u = r * 0.22; g.fillStyle = '#f0ece0';
  for (let y = 0; y < 6; y++) for (let x = 0; x < 7; x++) if (SKULL[y][x] === '#') g.fillRect(cx + (x - 3.5) * u, cy + (y - 3.2) * u, u, u);
}
function pool(g, cx, cy, rx, ry) { g.fillStyle = 'rgba(110,8,8,0.75)'; g.beginPath(); g.ellipse(cx, cy, rx, ry, 0, 0, 7); g.fill(); g.fillStyle = 'rgba(160,20,16,0.6)'; g.beginPath(); g.ellipse(cx - rx * 0.2, cy - 1, rx * 0.5, ry * 0.5, 0, 0, 7); g.fill(); }
const DCACHE = {};
function corpse(id) {
  if (DCACHE[id]) return DCACHE[id];
  const sp = C[id] && C[id].special, gr = lying(figGrid(id, 0), sp), s = 3;
  const w = (gr[0].length + 2) * s, h = (gr.length + 2) * s, cv = document.createElement('canvas'), g = cv.getContext('2d');
  cv.width = w + 16; cv.height = h + 34;
  pool(g, cv.width / 2 + 4, cv.height - 9, w * 0.42, 6);
  drawGrid(g, gr, 8, cv.height - h - 6, s);
  deathMark(g, cv.width / 2, 13, 11);
  return DCACHE[id] = cv;
}
// a field of the fallen: soldiers of each kind lying where they fell (seeded, so the same each time)
function fallen(F, key) {
  if (DCACHE[key]) return DCACHE[key];
  const list = []; for (const [k, n] of F.units) for (let i = 0; i < n; i++) list.push(k);
  const many = list.length, W2 = Math.min(560, 150 + many * 15), H2 = Math.min(190, 60 + many * 4.5), s = 3;
  const cv = document.createElement('canvas'), g = cv.getContext('2d'); cv.width = W2; cv.height = H2 + 22;
  g.fillStyle = 'rgba(70,40,26,0.35)'; g.beginPath(); g.ellipse(W2 / 2, 22 + H2 / 2, W2 / 2 - 2, H2 / 2 - 2, 0, 0, 7); g.fill();
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const spots = list.map(k => { const a = rnd() * Math.PI * 2, r = Math.sqrt(rnd()) * 0.86; return [k, W2 / 2 + Math.cos(a) * r * (W2 / 2 - 22), 22 + H2 / 2 + Math.sin(a) * r * (H2 / 2 - 10), rnd() < 0.5]; }).sort((p, q) => p[2] - q[2]);
  for (const [k, x, y, flip] of spots) {
    const gr = lying(KIND[k] ? soldier(k, 0, false) : BEASTS.has(k) ? beast(k, 0) : figGrid(k, 0)), w = (gr[0].length + 2) * s, h = (gr.length + 2) * s;
    pool(g, x, y + h / 2 - 2, w * 0.4, 3);
    g.save(); if (flip) { g.translate(x, 0); g.scale(-1, 1); g.translate(-x, 0); } drawGrid(g, gr, x - w / 2, y - h / 2, s); g.restore();
  }
  for (let i = 0; i < Math.min(6, 1 + many / 6); i++) { const x = 20 + rnd() * (W2 - 40), y = 26 + rnd() * (H2 - 10);   // crows
    g.fillStyle = '#121014'; g.fillRect(x, y, 4, 2); g.fillRect(x + 1, y - 1, 2, 1); g.fillRect(x - 2, y - 1, 2, 1); g.fillRect(x + 4, y - 1, 2, 1); }
  deathMark(g, W2 / 2, 11, 10);
  return DCACHE[key] = cv;
}
/* ---- battles: two small armies under their banners, and the clash between them ---- */
const KIND = {
  stark:     { skin: '#e8c0a0', helm: '#8a8e96', body: '#5a5e66', legs: '#3a3a3e', shield: '#c8ccd4', mark: '#5a5e66', arm: 'sword' },
  bolton:    { skin: '#f0d8cc', helm: '#5a4a4a', body: '#d89a9a', legs: '#3a2a2a', shield: '#c06a6a', mark: '#3a1a1a', arm: 'spear' },
  tully:     { skin: '#e8c0a0', helm: '#9aa0a8', body: '#3a5aa8', legs: '#a83a2a', shield: '#3a5aa8', mark: '#c8ccd4', arm: 'spear' },
  lannister: { skin: '#f0c8a8', helm: '#d8b040', body: '#a8281e', legs: '#5a1a14', shield: '#a8281e', mark: '#e8c040', arm: 'sword' },
  clansman:  { skin: '#d8a880', helm: '#5a4a3a', body: '#7a6a50', legs: '#4a3e32', arm: 'axe' },
  tyrell:    { skin: '#f0c8a8', helm: '#d8b040', body: '#3a8a3a', legs: '#2a4a2a', shield: '#3a8a3a', mark: '#e8c040', arm: 'spear' },
  baratheon: { skin: '#e8c0a0', helm: '#2a2a2e', body: '#d8b830', legs: '#2a2a2e', shield: '#d8b830', mark: '#1a1a1e', arm: 'sword' },
  greyjoy:   { skin: '#d8b896', helm: '#2a2a2e', body: '#1e1e22', legs: '#2a2a2e', shield: '#c8a040', mark: '#1a1a1e', arm: 'axe' },
  ironborn:  { skin: '#d8b896', helm: '#2a2a2e', body: '#3a3a40', legs: '#2a2a2e', arm: 'axe' },
  frey:      { skin: '#e8c0a0', helm: '#8a8a90', body: '#5a6a8a', legs: '#3a3a40', shield: '#5a6a8a', mark: '#c8ccd4', arm: 'sword' },
  watch:     { skin: '#e8c0a0', helm: '#1e1e22', body: '#141418', legs: '#1a1a1e', arm: 'sword' },
  freefolk:  { skin: '#e0b896', helm: '#8a7a66', body: '#7a6a56', legs: '#5a4e40', arm: 'spear' },
  wight:     { skin: '#a8c0c8', helm: '#3a3a40', body: '#4a4e54', legs: '#3a3e44', arm: 'club', eye: '#4ab8ff' },
  other:     { skin: '#dff0fa', helm: '#c8e4f4', body: '#e8f6ff', legs: '#c8e0f0', arm: 'sword', eye: '#4ab8ff' },
  dothraki:  { skin: '#b07850', helm: '#1e1a1a', body: '#a87048', legs: '#5a4030', arm: 'scimitar' },
  lhazareen: { skin: '#c89a70', helm: '#e8e4dc', body: '#d8d0c0', legs: '#a89a80', arm: 'club', short: 1 },
  unsullied: { skin: '#c89a70', helm: '#a8823a', body: '#4a3a2a', legs: '#3a2e24', shield: '#6a5a3a', mark: '#a8823a', arm: 'spear' },
  ghiscari:  { skin: '#c89a70', helm: '#a02828', body: '#e0d8c8', legs: '#a89a80', arm: 'scimitar' },
};
// riders of the Known World on their horses: [horse, horse dark, helm, skin, body]
const RIDERS = { rider: ['#8a5a30', '#5a3a1a', '#c9a03c', '#e8b892', '#3f6a3a'], starkrider: ['#6a6a6e', '#4a4a4e', '#8a8e96', '#e8c0a0', '#5a5e66'],
  dothrakirider: ['#5a3a22', '#3a2412', '#1e1a1a', '#b07850', '#a87048'], baratheonrider: ['#2a2a2e', '#141416', '#2a2a2e', '#e8c0a0', '#d8b830'] };
// one foot soldier facing right, 8×12 (short folk 8×10)
function soldier(k, f, lunge) {
  const K = KIND[k], g = blank(9, 12), top = K.short ? 2 : 0, a = (f % 2) ? 1 : 0;
  const al = K.ghost ? 'cc' : '';
  const c = v => v && K.ghost ? v + al : v;
  rectp(g, 2, top, 5, top + 1, c(K.helm)); rectp(g, 2, top + 2, 5, top + 3, c(K.skin)); setp(g, 5, top + 2, c(K.eye || '#16110d'));
  if (K.beard) rectp(g, 3, top + 3, 6, top + 5, K.beard);
  rectp(g, 2, top + 4, 5, 8, c(K.body)); if (K.mark && !K.shield) setp(g, 4, 6, K.mark);
  rectp(g, 2, 9, 3, 11 - (a ? 0 : 1), c(K.legs)); rectp(g, 4, 9, 5, 11 - a, c(shade(K.legs, 0.8)));
  if (K.shield) { rectp(g, 0, top + 4, 2, 8, c(K.shield)); setp(g, 1, 6, K.mark); }
  const r = lunge && a ? 1 : 0, hx = 6 + r;
  setp(g, hx, 6 - a, c(K.skin));
  if (K.arm === 'spear' || K.arm === 'fork') { for (let y = 0; y <= 10; y++) setp(g, hx + 1, y - a, '#8a6a44'); setp(g, hx + 1, -a, '#d6dae2'); if (K.arm === 'fork') { setp(g, hx, 0, '#8a8a90'); setp(g, hx + 2, 0, '#8a8a90'); } }
  if (K.arm === 'sword' || K.arm === 'scimitar') { for (let i = 0; i < 4; i++) setp(g, hx + 1 + (K.arm === 'scimitar' && i > 2 ? 1 : 0), 5 - a - i, '#d6dae2'); setp(g, hx, 6 - a, '#c9a03c'); }
  if (K.arm === 'axe') { for (let y = 2; y <= 7; y++) setp(g, hx + 1, y - a, '#6b4a2a'); rectp(g, hx + 2, 2 - a, hx + 2, 4 - a, '#c8ccd4'); }
  if (K.arm === 'club') { for (let y = 3; y <= 7; y++) setp(g, hx + 1, y - a, '#6b4a2a'); rectp(g, hx + 1, 2 - a, hx + 2, 3 - a, '#5a3a22'); }
  if (K.arm === 'bow') { for (let y = 2; y <= 9; y++) setp(g, hx + (y < 4 || y > 7 ? 0 : 1), y, '#8a6234'); }
  return g;
}
// the great beasts: a giant of the far north, and riders on their horses
function beast(k, f) {
  const a = f % 2;
  if (k === 'giant') {         // a giant of the far north: twice a man's height, shaggy, with a club
    const g = blank(14, 24), fur = '#7a6a56', fd = '#5a4e40', sk = '#c8a888';
    rectp(g, 4, 0, 9, 4, sk); setp(g, 8, 2, '#16110d'); rectp(g, 3, 5, 10, 15, fur); for (let y = 6; y <= 15; y += 2) setp(g, 4 + (y % 4), y, fd);
    rectp(g, 4, 16, 5, 23 - a, fd); rectp(g, 8, 16, 9, 23 - (1 - a), fd); rectp(g, 11, 4 + a, 12, 14 + a, '#5a3a22'); rectp(g, 10, 2 + a, 13, 5 + a, '#4a2e1a');
    return g;
  }
  if (RIDERS[k]) {
    const [h0, h1, hm, sk, bd] = RIDERS[k], g = blank(16, 15);
    rectp(g, 2, 7, 11, 10, h0); rectp(g, 11, 4, 13, 8, h0); rectp(g, 13, 3, 15, 5, h0); setp(g, 0, 8, h1); setp(g, 1, 7, h1); setp(g, 1, 9, h1);
    for (const [x, ph] of [[3, 0], [5, 1], [9, 1], [11, 0]]) rectp(g, x + (ph === a ? 1 : 0), 11, x + (ph === a ? 1 : 0), 14 - (ph === a ? 1 : 0), h1);
    rectp(g, 5, 0, 7, 1, hm); rectp(g, 5, 2, 7, 3, sk); setp(g, 7, 2, '#16110d'); rectp(g, 5, 4, 7, 7, bd); setp(g, 6, 8, '#5a4a30');
    for (let y = 0; y <= 7; y++) setp(g, 9 + (a ? 1 : 0), y - 1 + Math.round(y / 3), '#8a6a44'); setp(g, 9 + (a ? 1 : 0), -1, '#d6dae2');
    return g;
  }
  if (k === 'rider') {
    const g = blank(16, 15), h0 = '#8a5a30', h1 = '#5a3a1a';
    rectp(g, 2, 7, 11, 10, h0); rectp(g, 11, 4, 13, 8, h0); rectp(g, 13, 3, 15, 5, h0); setp(g, 0, 8, h1); setp(g, 1, 7, h1); setp(g, 1, 9, h1);
    for (const [x, ph] of [[3, 0], [5, 1], [9, 1], [11, 0]]) rectp(g, x + (ph === a ? 1 : 0), 11, x + (ph === a ? 1 : 0), 14 - (ph === a ? 1 : 0), h1);
    rectp(g, 5, 0, 7, 1, '#c9a03c'); rectp(g, 5, 2, 7, 3, '#e8b892'); setp(g, 7, 2, '#16110d'); rectp(g, 5, 4, 7, 7, '#3f6a3a'); setp(g, 6, 8, '#5a4a30');
    for (let y = 0; y <= 7; y++) setp(g, 9 + (a ? 1 : 0), y - 1 + Math.round(y / 3), '#8a6a44'); setp(g, 9 + (a ? 1 : 0), -1, '#d6dae2');
    return g;
  }
  return soldier(k, f, true);
}
const BEASTS = new Set(['rider', 'giant', ...Object.keys(RIDERS)]);
const BANNER = {
  stark: ['#e8e8ea', '#5a5e66', 'wolf'], lannister: ['#a8281e', '#e8c040', 'lion'], baratheon: ['#e0c030', '#141414', 'stag'], tully: ['#3a5aa8', '#c8ccd4', 'fish'],
  greyjoy: ['#141414', '#e0c040', 'kraken'], tyrell: ['#3a8a3a', '#e8c040', 'rose'], bolton: ['#d89a9a', '#a8281e', 'man'], frey: ['#8a8a90', '#3a5aa8', 'towers'],
  targaryen: ['#141414', '#c8281e', 'dragon'], martell: ['#e08a2a', '#c8281e', 'sun'], watch: ['#141414', '#141414', 'none'], freefolk: ['#7a6a56', '#c8b898', 'none'],
  others: ['#c8e4f4', '#4ab8ff', 'none'], dothraki: ['#a87048', '#e8c040', 'horse'], lamb: ['#e8e4dc', '#a89a80', 'none'], ghiscari: ['#a02828', '#e8c040', 'none'],
};
// small charges for the houses' banners, 7×6, one character per cell ('#' = charge colour)
const GLYPH = {
  wolf: ['#.....#', '##...##', '.#####.', '.#.#.#.', '..###..', '...#...'], lion: ['.###...', '#####..', '##.###.', '.#####.', '..#..#.', '.##.##.'],
  stag: ['#.#.#.#', '.#####.', '...#...', '..###..', '..#.#..', '..###..'], fish: ['.......', '.####.#', '#######', '.####.#', '.......', '.......'],
  kraken: ['..###..', '.#####.', '.#.#.#.', '#.#.#.#', '#.#.#.#', '.#...#.'], rose: ['..#.#..', '.#####.', '#######', '.#####.', '...#...', '..###..'],
  man: ['...#...', '..###..', '.#.#.#.', '...#...', '..#.#..', '.#...#.'], towers: ['#.#.#.#', '###.###', '##...##', '##...##', '#######', '#######'],
  dragon: ['.#.#.#.', '#######', '#.###.#', '..###..', '.##.##.', '#.....#'], sun: ['#..#..#', '.#####.', '#######', '.#####.', '#..#..#', '...#...'],
};
function banner(g, kind, x, y, s, f, flip) {
  const [bg, fg] = BANNER[kind] || ['#333', '#ccc'];
  g.fillStyle = OUT; g.fillRect(x - 1, y - 1, s + 2, 30 * s / 2 + 2); g.fillStyle = '#8a6a44'; g.fillRect(x, y, s, 30 * s / 2);
  const fx = flip ? x - 12 * s : x + s, wave = f % 2 ? s : 0;
  g.fillStyle = OUT; g.fillRect(fx - 1, y - 1, 12 * s + 2, 9 * s + 2 + wave);
  g.fillStyle = bg; g.fillRect(fx, y, 12 * s, 9 * s + wave); g.fillStyle = fg;
  const cx = fx + 6 * s, cy = y + 4.5 * s;
  const gl = GLYPH[(BANNER[kind] || [])[2]];
  if (gl) { for (let r = 0; r < 6; r++) for (let c = 0; c < 7; c++) if (gl[r][c] === '#') g.fillRect(cx + (c - 3.5) * s * 1.2, cy + (r - 3) * s * 1.2, s * 1.2, s * 1.2); return; }
  if ((BANNER[kind] || [])[2] === 'none') return;
  if ((BANNER[kind] || [])[2] === 'eye') { g.fillRect(cx - 3 * s, cy - s, 6 * s, 2 * s); g.fillStyle = '#16110d'; g.fillRect(cx - 0.5 * s, cy - s, s, 2 * s); }
  else if ((BANNER[kind] || [])[2] === 'tree') { g.fillRect(cx - 0.5 * s, cy - 2 * s, s, 5 * s); g.fillRect(cx - 2.5 * s, cy - 2 * s, 5 * s, s); g.fillRect(cx - 1.5 * s, cy - 3 * s, 3 * s, s); }
  else if ((BANNER[kind] || [])[2] === 'hand') { g.fillRect(cx - 2 * s, cy - s, 4 * s, 3 * s); for (let k = 0; k < 4; k++) g.fillRect(cx - 2 * s + k * s, cy - 3 * s, s * 0.8, 2 * s); }
  else if ((BANNER[kind] || [])[2] === 'horse') { g.fillRect(cx - 3 * s, cy, 4 * s, 2 * s); g.fillRect(cx, cy - 2 * s, 2 * s, 3 * s); g.fillRect(cx + 2 * s, cy - 2 * s, s, s); g.fillRect(cx - 3 * s, cy + 2 * s, s, s); g.fillRect(cx, cy + 2 * s, s, s); }
  else { g.fillRect(cx - s, cy - 2 * s, 2 * s, 4 * s); g.fillRect(cx - 2 * s, cy - s, 4 * s, 2 * s); }
}
const BCACHE2 = {};
function battle(b, f) {
  const key = b.name + f; if (BCACHE2[key]) return BCACHE2[key];
  const s = 2, half = 150, W2 = half * 2 + 20, H2 = 120, cv = document.createElement('canvas'), g = cv.getContext('2d');
  cv.width = W2; cv.height = H2; const mid = W2 / 2, ground = H2 - 14;
  // dust of the field
  g.fillStyle = 'rgba(70,52,30,0.35)'; g.beginPath(); g.ellipse(mid, ground - 6, half + 4, 16, 0, 0, 7); g.fill();
  if (b.muster) {
    // tents on the Firienfeld behind, then the Riders in ranks facing east, the banner and a horn-blower
    for (let i = 0; i < 6; i++) { const tx = 40 + i * 44 + (i % 2) * 10, ty = ground - 44 - (i % 2) * 8;
      g.fillStyle = OUT; g.beginPath(); g.moveTo(tx - 15, ty + 17); g.lineTo(tx, ty - 3); g.lineTo(tx + 15, ty + 17); g.closePath(); g.fill();
      g.fillStyle = i % 2 ? '#e8e2d0' : '#d8d0b8'; g.beginPath(); g.moveTo(tx - 12, ty + 15); g.lineTo(tx, ty); g.lineTo(tx + 12, ty + 15); g.closePath(); g.fill();
      g.fillStyle = '#2a5a2a'; g.fillRect(tx - 1, ty - 9, 2, 8); g.fillRect(tx + 1, ty - 9, 6, 3 + (f + i) % 2); }
    const side = b.sides[0], list = []; for (const [k, n] of side.units) for (let i = 0; i < n; i++) list.push(k);
    list.forEach((k, i) => { const col = i % 7, row = Math.floor(i / 7), gr = k === 'rider' ? beast('rider', f + i) : soldier(k, f + i, false);
      const w = (gr[0].length + 2) * s, h = (gr.length + 2) * s; drawGrid(g, gr, 30 + col * 36 + row * 14 - w / 2, ground - 8 + row * 8 - h, s); });
    banner(g, side.banner, W2 - 30, 22, s, f, false);
    return BCACHE2[key] = cv;
  }
  b.sides.forEach((side, si) => {
    const dir = si === 0 ? 1 : -1, list = [];
    for (const [k, n] of side.units) for (let i = 0; i < n; i++) list.push(k);
    const big = list.filter(k => k === 'giant'), foot = list.filter(k => !big.includes(k));
    const place = [];
    // foot and riders in ranks, front rank nearest the clash
    foot.forEach((k, i) => { const col = Math.floor(i / 3), row = i % 3; place.push([k, mid - dir * (18 + col * 15 + (row % 2) * 7), ground - 30 + row * 9, i < 3]); });
    const footBack = foot.length ? 18 + Math.floor((foot.length - 1) / 3) * 15 + 7 : 0;
    big.forEach((k, i) => place.push([k, mid - dir * ((foot.length ? footBack + 10 : 24) + i * (foot.length ? 22 : 17)), ground - 12 + (foot.length ? 0 : (i % 2) * 6), !foot.length && i === 0]));
    place.sort((p, q) => p[2] - q[2]);
    const reach = Math.max(30, ...place.map(p => Math.abs(p[1] - mid)));
    banner(g, side.banner, Math.max(8, Math.min(W2 - 8, mid - dir * (reach + 16))), 22, s, f + si, dir < 0);
    for (const [k, x, y, front] of place) {
      const gr = BEASTS.has(k) ? beast(k, f + (x | 0) % 2) : soldier(k, f + (x | 0) % 2, front);
      const w = (gr[0].length + 2) * s, h = (gr.length + 2) * s, bob = front && f % 2 ? dir * 2 : 0;
      g.save(); if (dir < 0) { g.translate(x + w / 2 + bob, 0); g.scale(-1, 1); g.translate(-w / 2, 0); } else g.translate(x - w / 2 + bob, 0);
      drawGrid(g, gr, 0, y - h + (gr.length > 14 ? 10 : 0), s); g.restore();
    }
  });
  // the clash: sparks along the line, changing each frame
  for (let i = 0; i < 3; i++) {
    const y = ground - 40 + i * 12 + ((f + i) % 2) * 3, x = mid + ((f * 7 + i * 5) % 9) - 4, r = (f + i) % 2 ? 7 : 4;
    g.fillStyle = '#fff6c8'; g.beginPath(); for (let k = 0; k < 8; k++) { const ang = k * Math.PI / 4 + f, q = k % 2 ? r * 0.35 : r; g.lineTo(x + Math.cos(ang) * q, y + Math.sin(ang) * q); } g.fill();
    g.fillStyle = '#ffb030'; g.beginPath(); g.arc(x, y, r * 0.3, 0, 7); g.fill();
  }
  return BCACHE2[key] = cv;
}
function listNames(ids) {
  const n = [...new Set(ids.map(i => C[i].name))];
  return n.length <= 2 ? n.join(' & ') : n.length <= 4 ? n.slice(0, -1).join(', ') + ' & ' + n[n.length - 1] : n.slice(0, 3).join(', ') + ` & ${n.length - 3} more`;
}
function dataURL(ids, color, t) { return icon(ids, color, t).canvas.toDataURL(); }
// one soldier, rider or beast of a battle as its own canvas (for the ground view's armies)
const UCACHE = {};
function unitCanvas(kind, f, flip) {
  const key = kind + f + (flip ? 'w' : ''); if (UCACHE[key]) return UCACHE[key];
  const gr = BEASTS.has(kind) ? beast(kind, f) : soldier(kind, f, f % 2 === 1);
  const s = 3, cv = document.createElement('canvas'); cv.width = (gr[0].length + 2) * s; cv.height = (gr.length + 2) * s;
  const g = cv.getContext('2d'); if (flip) { g.translate(cv.width, 0); g.scale(-1, 1); } drawGrid(g, gr, 0, 0, s);
  return UCACHE[key] = cv;
}
return { C, B, JOURNEY, GROUPS, charsOf, icon, dataURL, drawHead, drawFigure, battle, unitCanvas, corpse, fallen };
})();
if (typeof self !== 'undefined') self.AVATARS = AVATARS;
