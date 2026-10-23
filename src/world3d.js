/* ============================================================================
   WORLD3D — castles, town detail and people for the ground view.
   Appended to ground.js by build.js, so it shares that module's THREE, MI, G and groundAt.
   ========================================================================== */

/* ---------------- geometry helpers ---------------- */
const lin = c => (typeof c === 'number' ? new THREE.Color(c) : new THREE.Color().setRGB(c[0], c[1], c[2], THREE.SRGBColorSpace));
const bx = (w, h, d) => new THREE.BoxGeometry(w, h, d).translate(0, h / 2, 0);
const cy = (rt, rb, h, seg = 8) => new THREE.CylinderGeometry(rt, rb, h, seg).translate(0, h / 2, 0);
const cn = (r, h, seg = 8) => new THREE.ConeGeometry(r, h, seg).translate(0, h / 2, 0);
const sph = (r, ws = 8, hs = 6) => new THREE.SphereGeometry(r, ws, hs);
// a geometry placed in a house's frame: local offset (lx, ly, lz), then turned by ang about the house centre
const at = (g, cx, y, cz, ang, lx = 0, ly = 0, lz = 0) => g.translate(lx, ly, lz).rotateY(ang).translate(cx, y, cz);

/* Merge geometries into one, painting each part a flat colour. Parts: [geometry, colour, extra?].
   extra = { part, pivot } fills the aPart/aPivot attributes used by the walking shader. */
function merge(parts, withParts) {
  let n = 0;
  const gs = parts.map(([g]) => { const q = g.index ? g.toNonIndexed() : g; if (!q.attributes.normal) q.computeVertexNormals(); n += q.attributes.position.count; return q; });
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), col = new Float32Array(n * 3);
  const prt = withParts ? new Float32Array(n) : null, piv = withParts ? new Float32Array(n) : null;
  let o = 0;
  gs.forEach((g, k) => {
    const c = lin(parts[k][1]), ex = parts[k][2] || {}, cnt = g.attributes.position.count;
    pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3);
    for (let i = 0; i < cnt; i++) { col[(o + i) * 3] = c.r; col[(o + i) * 3 + 1] = c.g; col[(o + i) * 3 + 2] = c.b; if (prt) { prt[o + i] = ex.part || 0; piv[o + i] = ex.pivot || 0; } }
    o += cnt;
  });
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  out.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  out.setAttribute('color', new THREE.BufferAttribute(col, 3));
  if (prt) { out.setAttribute('aPart', new THREE.BufferAttribute(prt, 1)); out.setAttribute('aPivot', new THREE.BufferAttribute(piv, 1)); }
  return out;
}
function glowTexture(inner, outer) {
  const cv = document.createElement('canvas'); cv.width = cv.height = 128;
  const g = cv.getContext('2d'), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, inner); gr.addColorStop(0.25, inner); gr.addColorStop(1, outer);
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
}
function glow(inner, outer, size) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTexture(inner, outer), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, fog: false }));
  s.scale.setScalar(size); return s;
}
const vcMat = (o = {}) => new THREE.MeshStandardMaterial(Object.assign({ vertexColors: true, roughness: 0.85 }, o));

/* ---------------- castles of the Known World, as the books describe them ----------------
   Built from simple solids at a man's scale (metres). Walls and towers run 15 m below their base so they sit on
   uneven ground. Kinds come from a place's `castle` option (tools/known/author.py). */
const KB = (w, h, d) => bx(w, h + 15, d).translate(0, -15, 0);
const KC = (rt, rb, h, seg = 12) => cy(rt, rb, h + 15, seg).translate(0, -15, 0);
function kWall(P, pts, h, t, col, closed = true, step = 4) {
  const n = closed ? pts.length : pts.length - 1;
  for (let i = 0; i < n; i++) {
    const [x0, z0] = pts[i], [x1, z1] = pts[(i + 1) % pts.length], L = Math.hypot(x1 - x0, z1 - z0), a = Math.atan2(z1 - z0, x1 - x0);
    P.push([KB(L + t, h, t).rotateY(-a).translate((x0 + x1) / 2, 0, (z0 + z1) / 2), col]);
    for (let d = step / 2; d < L; d += step) { const f = d / L; P.push([bx(step * 0.45, 1.8, t * 0.3).rotateY(-a).translate(x0 + (x1 - x0) * f, h, z0 + (z1 - z0) * f), col]); }
  }
}
function kDrum(P, x, z, r, h, col, roof, seg = 12) {
  P.push([KC(r, r * 1.06, h, seg).translate(x, 0, z), col]);
  const segM = Math.max(seg, Math.round(r * 1.2)); for (let i = 0; i < segM; i += 2) { const a = i / segM * Math.PI * 2; const mw = Math.min(r * 0.42, 3.2); P.push([bx(mw, 1.8, Math.min(r * 0.3, 2)).rotateY(-a).translate(x + Math.cos(a) * (r - 1), h, z + Math.sin(a) * (r - 1)), col]); }
  if (roof) P.push([cn(r * 1.12, r * 1.6, seg).translate(x, h, z), roof]);
}
function kSquare(P, x, z, w, h, col, roof) {
  P.push([KB(w, h, w).translate(x, 0, z), col]);
  for (const [dx, dz] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) P.push([bx(w * 0.22, 2.2, w * 0.22).translate(x + dx * w * 0.39, h, z + dz * w * 0.39), col]);
  if (roof) P.push([cn(w * 0.75, w * 0.9, 4).rotateY(Math.PI / 4).translate(x, h, z), roof]);
}
const ring = (r, n, a0 = 0, sx = 1, sz = 1) => Array.from({ length: n }, (_, i) => [Math.cos(a0 + i / n * Math.PI * 2) * r * sx, Math.sin(a0 + i / n * Math.PI * 2) * r * sz]);
function kTree(P, x, z, h, trunk, leaf) { P.push([cy(0.5, 0.8, h * 0.45, 6).translate(x, 0, z), trunk], [cn(h * 0.22, h * 0.7, 7).translate(x, h * 0.3, z), leaf]); }
function weirwood(P, x, z) { P.push([cy(1.4, 2.2, 9, 7).translate(x, 0, z), 0xeeebe2], [sph(7, 9, 6).scale(1, 0.55, 1).translate(x, 11, z), 0xa8201a], [sph(4, 8, 6).scale(1, 0.6, 1).translate(x + 3, 13, z - 2), 0xc0301e]); }
function castleMesh(P, opts = {}) {
  const g = new THREE.Group(), m = new THREE.Mesh(merge(P), vcMat(Object.assign({ roughness: 0.9 }, opts)));
  m.castShadow = m.receiveShadow = true; g.add(m); return g;
}
const CASTLE = {
  // two curtain walls of grey granite, the outer 80 feet and the inner 100, with a moat between; the round First Keep,
  // the Great Keep, the Broken Tower, the glass gardens warmed by the hot springs, and the godswood with its heart tree
  winterfell() {
    const gr = 0x7a7a80, gr2 = 0x66666e, roof = 0x4a4e58, P = [];
    const outer = [[-170, -150], [170, -150], [170, 150], [-170, 150]], inner = [[-130, -112], [130, -112], [130, 112], [-130, 112]];
    kWall(P, outer, 24, 7, gr2); kWall(P, inner, 30, 8, gr);
    for (const [x, z] of outer) kDrum(P, x, z, 11, 30, gr2);
    for (const [x, z] of inner) kDrum(P, x, z, 13, 38, gr);
    for (const [x, z] of [[0, -150], [0, 150], [-170, 0], [170, 0]]) kSquare(P, x, z, 16, 28, gr2);
    P.push([bx(372, 0.6, 26).translate(0, -1.6, -131), 0x2a3a44], [bx(372, 0.6, 26).translate(0, -1.6, 131), 0x2a3a44], [bx(26, 0.6, 236).translate(-150, -1.6, 0), 0x2a3a44], [bx(26, 0.6, 236).translate(150, -1.6, 0), 0x2a3a44]);
    P.push([KB(64, 30, 36).translate(-20, 0, -40), gr], [cn(46, 14, 4).rotateY(Math.PI / 4).scale(1, 1, 0.6).translate(-20, 30, -40), roof]);     // the Great Keep
    kDrum(P, 40, -60, 16, 26, gr2);                                                                                                     // the First Keep
    for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2; P.push([bx(2, 3, 2).translate(40 + Math.cos(a) * 15, 26, -60 + Math.sin(a) * 15), 0x4e4e54]); }   // its gargoyles
    P.push([KC(7, 8, 42, 10).translate(95, 0, -80), gr]); for (let i = 0; i < 7; i++) { const a = i / 7 * Math.PI * 2; P.push([bx(2.4, 2 + (i * 5) % 7, 2.4).translate(95 + Math.cos(a) * 6, 42, -80 + Math.sin(a) * 6), gr]); }  // the Broken Tower
    kDrum(P, -95, -70, 6, 34, gr, roof); kDrum(P, 70, 60, 5, 30, gr, roof);                                                           // bell tower and rookery
    P.push([KB(46, 9, 22).translate(-70, 0, 70), 0x5a6a70], [bx(44, 4, 20).translate(-70, 9, 70), 0xa8d4dc]);                         // the glass gardens
    for (let i = 0; i < 26; i++) { const x = -110 + (i * 37) % 80, z = -100 + (i * 23) % 70; kTree(P, x + 70, z + 150 - 60, 14 + (i % 4) * 3, 0x3a2a1a, 0x2a4a30); }
    weirwood(P, 20, 70);
    P.push([cy(9, 9, 0.5, 14).translate(34, -0.2, 84), 0x4a7a84], [cy(6, 6, 0.5, 12).translate(4, -0.2, 92), 0x4a7a84]);   // the hot pools in the godswood
    const g = castleMesh(P);
    // steam off the hot springs: soft plumes rising and thinning over the pools and the glass gardens
    const puffs = [];
    for (let i = 0; i < 14; i++) {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTexture('rgba(240,244,248,0.55)', 'rgba(240,244,248,0)'), depthWrite: false, transparent: true }));
      const [x0, z0] = [[34, 84], [4, 92], [-70, 70]][i % 3];
      sp.userData = { x0: x0 + (i * 7) % 9 - 4, z0: z0 + (i * 5) % 7 - 3, ph: i / 14 };
      g.add(sp); puffs.push(sp);
    }
    g.userData.update = (dt, t) => {
      for (const sp of puffs) {
        const u = ((t * 0.06 + sp.userData.ph) % 1 + 1) % 1;              // each puff rises 40 m over its life, swelling
        sp.position.set(sp.userData.x0 + 6 * u, 3 + 40 * u, sp.userData.z0 - 3 * u);
        sp.scale.setScalar(8 + 26 * u); sp.material.opacity = 0.75 * Math.sin(Math.PI * u);
      }
    };
    return g;
  },
  // no walls: towers, halls and barracks of stone and timber at the foot of the Wall, and a timber stair zig-zagging up its face
  castleblack() {
    const st = 0x5a5a5e, tb = 0x5a4632, P = [];
    kSquare(P, -30, 30, 18, 30, st, 0x2e2e34); kDrum(P, 30, 20, 8, 34, st); kDrum(P, 70, 50, 6, 22, st);
    P.push([KB(14, 26, 12).rotateZ(0.06).translate(-80, 0, 60), st]);                    // Hardin's Tower, leaning
    P.push([KB(60, 10, 16).translate(10, 0, 80), st], [cn(36, 6, 4).rotateY(Math.PI / 4).scale(1, 1, 0.35).translate(10, 10, 80), 0x3a3a40]);   // the common hall
    P.push([KB(70, 8, 14).translate(-20, 0, 120), 0x6a625a]);                             // the Flint Barracks
    for (let k = 0; k < 9; k++) { const y = k * 22, dir = k % 2 ? 1 : -1; P.push([bx(70, 1.2, 5).rotateZ(dir * 0.3).translate(0, y + 11, -6), tb], [bx(3, y + 22, 3).translate(dir * 35, 0, -6), tb]); }
    P.push([bx(18, 6, 12).translate(30, 205, -10), tb]);                                   // the winch cage at the top
    return castleMesh(P);
  },
  // seven slender white towers crowded on a shoulder of the mountain, high above the valley
  eyrie() {
    const w = 0xf2f0ea, bl = 0x8ab0d0, rock = 0x8a8072, P = [[KC(34, 60, 120, 9), rock], [KC(30, 30, 10, 14).translate(0, 120, 0), 0xe6e2d8]];
    const tw = [[0, 0, 7, 46], [-18, 10, 4.5, 34], [16, 12, 4.5, 36], [-14, -16, 4, 30], [14, -15, 4, 32], [0, 22, 4, 28], [-24, -2, 3.5, 26]];
    for (const [x, z, r, h] of tw) P.push([cy(r, r * 1.05, h, 10).translate(x, 128, z), w], [cn(r * 1.15, r * 2.2, 10).translate(x, 128 + h, z), bl]);
    return castleMesh(P, { roughness: 0.6 });
  },
  // the greatest castle in Westeros: walls like cliffs and five monstrous towers whose tops dragonfire melted like candles
  harrenhal() {
    const d = 0x45403c, d2 = 0x34302c, glass = 0x241e1c, P = [];
    const wall = [[-420, -300], [380, -320], [440, 260], [-380, 300]];
    kWall(P, wall, 42, 14, d, true, 6);
    const tw = [[-380, -260, 30, 120], [340, -280, 26, 100], [400, 220, 34, 140], [-340, 260, 24, 90], [-40, -10, 30, 110]];
    for (const [x, z, r, h] of tw) {
      P.push([KC(r * 0.9, r, h, 14).translate(x, 0, z), d]);
      for (let k = 0; k < 6; k++) { const a = k * 1.1; P.push([sph(r * 0.45, 8, 6).scale(1, 1.6, 1).translate(x + Math.cos(a) * r * 0.55, h - 6 - (k % 3) * 9, z + Math.sin(a) * r * 0.55), glass]); }   // stone run like wax
      P.push([sph(r * 0.8, 10, 6).scale(1, 0.45, 1).translate(x, h, z), d2]);
    }
    P.push([KB(160, 24, 70).translate(-60, 0, 150), d2]);                                  // the Hall of a Hundred Hearths
    return castleMesh(P, { roughness: 0.75, metalness: 0.08 });
  },
  // two castles facing each other across the Green Fork, joined by a bridge with the Water Tower at its middle
  twins() {
    const g1 = 0x8a8680, g2 = 0x77736c, P = [];
    for (const s of [-1, 1]) {
      const cx = s * 150, sq = [[cx - 60, -60], [cx + 60, -60], [cx + 60, 60], [cx - 60, 60]];
      kWall(P, sq, 18, 6, g2); for (const [x, z] of sq) kDrum(P, x, z, 8, 24, g2);
      kSquare(P, cx + s * 10, 0, 28, 46, g1, 0x4a4e58);
    }
    P.push([bx(180, 4, 16).translate(0, 10, 0), g2]); for (const x of [-60, -30, 30, 60]) P.push([KB(8, 10, 14).translate(x, 0, 0), g2]);
    kDrum(P, 0, 0, 12, 34, g1, 0x4a4e58);
    return castleMesh(P);
  },
  // red stone on Aegon's High Hill: seven great drum towers with iron ramparts, and Maegor's Holdfast within its dry moat
  redkeep() {
    const r1 = 0xa0483a, r2 = 0x8a3a2e, iron = 0x2a2626, P = [];
    const wall = ring(150, 7, 0.3, 1.1, 0.9);
    kWall(P, wall, 26, 9, r2);
    for (const [x, z] of wall) { kDrum(P, x, z, 15, 38, r1); P.push([cy(15.5, 15.5, 2.5, 12).translate(x, 38, z), iron]); }
    P.push([cy(52, 52, 0.6, 20).translate(0, -3, 0), 0x2a2420]); kSquare(P, 0, 0, 52, 40, r1);                 // Maegor's Holdfast and its moat
    kSquare(P, 70, -50, 16, 44, r2); P.push([KB(70, 22, 30).translate(-60, 0, 50), r1]);                         // the Tower of the Hand; the throne room
    return castleMesh(P);
  },
  // one immense drum tower behind a curtain wall without a corner, built to stand against the storms
  stormsend() {
    const g = 0x6a6e74, P = [];
    kWall(P, ring(95, 28), 30, 12, 0x5e6268, true, 5);
    kDrum(P, 0, 0, 45, 92, g, null, 24);
    for (let k = 0; k < 6; k++) P.push([bx(5, 7, 1).rotateY(k).translate(Math.cos(k) * 45, 40 + (k % 3) * 14, Math.sin(k) * 45), 0x1a1a1e]);
    return castleMesh(P);
  },
  // black stone fused by dragonfire into dragon shapes: towers with dragon heads, gargoyles on every wall
  dragonstone() {
    const b = 0x24222a, b2 = 0x302c34, P = [];
    const wall = ring(120, 9, 0.2, 1.2, 0.9); kWall(P, wall, 22, 8, b2);
    for (const [x, z] of wall) { kDrum(P, x, z, 9, 30, b); P.push([bx(5, 5, 9).translate(x, 30, z + 4), b2], [cn(1.2, 6, 5).rotateX(-0.6).translate(x - 2, 33, z), b2], [cn(1.2, 6, 5).rotateX(-0.6).translate(x + 2, 33, z), b2]); }
    kDrum(P, 0, 0, 26, 52, b);                                                                    // the Stone Drum
    P.push([KC(8, 10, 74, 10).translate(60, 0, -40), b], [bx(9, 7, 18).translate(60, 74, -36), b2], [cn(2, 9, 5).rotateX(-0.5).translate(57, 80, -42), b2], [cn(2, 9, 5).rotateX(-0.5).translate(63, 80, -42), b2]);   // the Sea Dragon Tower
    for (let k = 0; k < 18; k++) { const [x, z] = wall[k % 9], [x2, z2] = wall[(k + 1) % 9], f = (k % 2 ? 0.33 : 0.66); P.push([bx(3, 4, 3).translate(x + (x2 - x) * f, 22, z + (z2 - z) * f), b2]); }
    return castleMesh(P, { roughness: 0.5 });
  },
  // towers on sea stacks, linked by bridges of stone and of rope that sway over the surf
  pyke() {
    const rock = 0x4a4844, st = 0x5a5a5c, P = [], stacks = [[0, 0, 28, 40], [80, 30, 20, 34], [140, -20, 18, 30], [-70, 40, 22, 36]];
    for (const [x, z, r, h] of stacks) { P.push([KC(r * 0.85, r, h, 9).translate(x, -20, z), rock]); kDrum(P, x, z, r * 0.45, h - 20 + 32, st, 0x2e3034); }
    for (let i = 0; i < stacks.length - 1; i++) {
      const [x0, z0, , h0] = stacks[i === 2 ? 0 : i], [x1, z1, , h1] = stacks[i + 1], L = Math.hypot(x1 - x0, z1 - z0), a = Math.atan2(z1 - z0, x1 - x0);
      P.push([bx(L, 1.2, 2.4).rotateY(-a).translate((x0 + x1) / 2, Math.min(h0, h1) - 14, (z0 + z1) / 2), i % 2 ? 0x5a4632 : st]);
    }
    return castleMesh(P);
  },
  // the tallest tower in Westeros, in stepped tiers on its island, with a beacon fire at the top
  hightower() {
    const w = 0xd8d6d0, w2 = 0xc4c2bc, P = [[KB(120, 18, 120), 0x8a8478]];
    const tiers = [[60, 60], [48, 50], [38, 45], [30, 40], [22, 36], [15, 30]]; let y = 18;
    for (const [r, h] of tiers) { P.push([cy(r * 0.92, r, h, 16).translate(0, y, 0), y % 2 ? w : w2]); y += h; }
    P.push([cy(9, 9, 10, 12).translate(0, y, 0), 0x6a6460]);
    const g = castleMesh(P, { roughness: 0.6 });
    const fire = glow('rgba(255,200,90,1)', 'rgba(255,90,20,0)', 70); fire.position.y = y + 14; g.add(fire);
    const light = new THREE.PointLight(0xffa040, 3e5, 6000, 2); light.position.y = y + 14; g.add(light);
    g.userData.update = (dt, t) => { fire.scale.setScalar(60 + 12 * Math.sin(t * 5.1) * Math.sin(t * 1.7)); };
    return g;
  },
  // a triangle of sandstone walls where the Tumblestone joins the Red Fork; the rivers fill its moat
  riverrun() {
    const s = 0xc8a070, s2 = 0xb08a5c, P = [], tri = [[0, -120], [130, 90], [-130, 90]];
    kWall(P, tri, 22, 8, s2); for (const [x, z] of tri) kDrum(P, x, z, 12, 32, s, 0x4a6a9a);
    kSquare(P, 0, 20, 30, 40, s, 0x4a6a9a); P.push([bx(300, 0.6, 30).translate(0, -1.6, 110), 0x3a5a6a]);
    return castleMesh(P);
  },
  // the Rock: a great stone mountain above the sea, its halls delved within, towers on its crown
  casterlyrock() {
    const rk = 0xa08a68, rk2 = 0x8a7458, P = [[sph(260, 18, 10).scale(1.4, 0.75, 0.8).translate(0, -40, 0), rk], [sph(140, 14, 8).scale(1, 0.9, 0.9).translate(-120, 40, 40), rk2]];
    for (let i = 0; i < 40; i++) P.push([bx(4, 6, 1).translate(-200 + (i * 47) % 400, 20 + (i * 29) % 120, 205 - (i % 5) * 4), 0x2a2018]);
    for (const [x, z, h] of [[-40, 0, 40], [30, 30, 30], [90, -20, 26]]) kDrum(P, x, z, 8, 150 + h, 0xc8b490, 0xa83020);
    return castleMesh(P);
  },
  // the Tower of the Sun with its dome of gold and glass, the slender Spear Tower, and the Winding Walls
  sunspear() {
    const sd = 0xd8c8a0, P = [];
    kWall(P, [[-160, -60], [-80, -110], [20, -90], [120, -130], [170, -40], [120, 60], [0, 90], [-120, 70]], 14, 6, 0xc8b890);
    P.push([KC(22, 24, 36, 16), sd], [new THREE.SphereGeometry(22, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2).translate(0, 36, 0), 0xe0b040]);
    P.push([KC(5, 6, 66, 10).translate(60, 0, -20), sd], [cn(1.5, 16, 6).translate(60, 66, -20), 0xe8d070]);
    return castleMesh(P, { roughness: 0.55 });
  },
};
/* Castles and town details for one near patch.
   B = { list, special } from GEN.buildingsNear; coordinates relative to the patch centre (X0, Y0). */
function W3town(B, X0, Y0, hAt) {
  const grp = new THREE.Group(), up = [], solids = [];
  const P = [], lamps = [];
  const toXZ = (X, Y) => [(X - X0) * MI, -(Y - Y0) * MI];
  for (const s of B.special) {
    const [x, z] = toXZ(s.x, s.y);
    if (Math.hypot(x - G.px, z - G.pz) > 60000) continue;
    const y = hAt(x, z);
    let m = null;
    if (s.type === 'castle' && CASTLE[s.kind]) m = CASTLE[s.kind]();
    if (m) { m.position.set(x, y - 1, z); grp.add(m); if (m.userData.update) up.push(m.userData.update); }
  }
  for (const b of B.list) {
    const [x, z] = toXZ(b.x, b.y), y0 = hAt(x, z) - 0.4;
    if (b.ruin) continue;
    houseDetails(P, b, x, y0, z);
  }
  if (P.length) {
    // pre-coloured merges stay as they are; everything else is a flat-coloured part
    const pre = P.filter(p => p[0].attributes.color), flat = P.filter(p => !p[0].attributes.color);
    const geos = [];
    if (flat.length) geos.push(merge(flat));
    for (const [g] of pre) geos.push(g);
    for (const g of geos) { const m = new THREE.Mesh(g, vcMat({ roughness: 0.82 })); m.castShadow = m.receiveShadow = true; grp.add(m); }
  }
  if (lamps.length) {
    const lm = new THREE.InstancedMesh(sph(0.32, 6, 4), new THREE.MeshBasicMaterial({ color: 0xffffff }), lamps.length), m4 = new THREE.Matrix4(), c = new THREE.Color();
    const tints = [0xd8f0ff, 0xfff0b0, 0xc8ffd8, 0xffffff];
    lamps.forEach(([x, y, z, i], k) => { m4.makeTranslation(x, y, z); lm.setMatrixAt(k, m4); lm.setColorAt(k, c.set(tints[(k + i) % 4])); });
    grp.add(lm);
  }
  grp.userData.update = (dt, t) => up.forEach(f => f(dt, t)); grp.userData.solids = solids;
  return grp;
}
const DOOR = { northern: 0x4a3420, stone: 0x2a2620, sunbaked: 0x6a4020, lakeside: 0x3a2a1e, roundhut: 0x4a3420 };
function houseDetails(P, b, x, y, z) {
  const d = b.d, w = b.w, a = b.a, h = b.h, dc = DOOR[b.culture];
  if (dc === undefined) return;
  const door = bx(1.2, 2.1, 0.12);
  P.push([at(door, x, y, z, a, 0, 0.1, d / 2 + 0.06), dc]);
  const win = 0x26282a, nw = Math.max(1, Math.floor(w / 4.5)), floors = h > 9 ? 2 : 1;
  for (let f = 0; f < floors; f++) for (let k = 0; k < nw; k++) {
    const lx = (k - (nw - 1) / 2) * (w / nw);
    if (f === 0 && Math.abs(lx) < 1.3) continue;
    P.push([at(bx(0.9, 1.1, 0.1), x, y, z, a, lx, 1.4 + f * 3.3, d / 2 + 0.05), win]);
  }
  if (['northern', 'lakeside'].includes(b.culture) && Math.sin(b.x * 3e4) > -0.3)
    P.push([at(bx(0.8, 2.2, 0.8), x, y, z, a, w * 0.3, h + Math.min(w, d) * 0.25, 0), 0x6e6258]);
}

/* ---------------- people ---------------- */
// Proportions in metres; c = tunic choices, legs, skin, hair, cloak (null = none).
const KIN = {
  northman: { h: 1.78, skin: 0xd8a884, hair: [0x4a3020, 0x2a1e14, 0x8a6a3a], c: [0x6a5a3a, 0x4a5a3a, 0x5a5e66, 0x5a4a5a], legs: 0x3e3a30, cloak: 0x5a5048, beardP: 0.5 },
  southron: { h: 1.78, skin: 0xd8a884, hair: [0x3a2a1e, 0x6a3a1e, 0xa0702a, 0x1e1814], c: [0x8a2a24, 0x2a4a7a, 0x6a5a2a, 0x3a6a5a, 0xc8a050], legs: 0x3a3430 },
  sunfolk: { h: 1.76, skin: 0xa8704a, hair: [0x14100c, 0x2a1e14], c: [0xd8a038, 0xe8d8b0, 0xb03a24, 0x8a6a3a], legs: 0x6a4a2a, robe: 1 },
  lakefolk: { h: 1.74, skin: 0xd09a7a, hair: [0x3a2a1e, 0x4a3a2a], c: [0x4a5a32, 0x5a4a30, 0x3a4a2a], legs: 0x3a3028 },
};
const FOLK = { northern: [['northman', 1]], stone: [['southron', 1]], sunbaked: [['sunfolk', 1]], lakeside: [['lakefolk', 1]], roundhut: [['sunfolk', 1]] };
// Built once per kin at 1.8 m and scaled. aPart: 1 tunic (per-person tint), 2 legs, 5 arms; aPivot = hip/shoulder height.
function figure(k) {
  const S = KIN[k], wd = S.wd || 1, legH = 0.82 * (S.leg ? S.leg / 0.46 : 1), torso = 0.62, hip = legH, sh = hip + torso, head = 0.12 * (S.head || 1);
  const hairC = S.hair[0], P = [];
  const L = (g, c, part, pivot) => P.push([g, c, { part, pivot }]);
  for (const s of [-1, 1]) {
    L(bx(0.15 * wd, legH, 0.17).translate(s * 0.1 * wd, 0, 0), S.legs, 2, hip);
    L(bx(0.16 * wd, 0.08, 0.26).translate(s * 0.1 * wd, 0, 0.04), S.feet || 0x2a2018, 2, hip);
    L(bx(0.11, torso * 0.92, 0.12).translate(s * (0.25 * wd + 0.03), hip + torso * 0.08, 0), 0xffffff, 5, sh);
    L(sph(0.06, 5, 4).translate(s * (0.25 * wd + 0.03), hip + torso * 0.04, 0), S.skin, 5, sh);
  }
  const body = bx(0.44 * wd, torso, 0.25);
  if (S.robe) L(cy(0.2 * wd, 0.3 * wd, hip * 0.9, 8).translate(0, hip * 0.08, 0), 0xffffff, 1, 0);
  L(body.translate(0, hip, 0), 0xffffff, 1, 0);
  L(bx(0.46 * wd, 0.06, 0.27).translate(0, hip + 0.02, 0), 0x3a2a1e, 0, 0);
  L(sph(head, 9, 7).translate(0, sh + head + 0.04, 0.02), S.skin, 0, 0);
  if (S.turban) L(sph(head * 1.15, 8, 6).scale(1, 0.7, 1).translate(0, sh + head * 1.6, 0.01), 0xe8e0c8, 0, 0);
  else if (S.helm) L(sph(head * 1.12, 8, 5, 0, Math.PI * 2, 0, Math.PI / 2).translate(0, sh + head + 0.06, 0.01), S.helm, 0, 0);
  else if (S.hood) L(cn(head * 1.15, head * 2.2, 7).translate(0, sh + head * 0.7, -0.02), 0x5a3a2a, 0, 0);
  else L(sph(head * 1.08, 8, 5, 0, Math.PI * 2, 0, Math.PI * 0.55).translate(0, sh + head + 0.05, -0.01), hairC, 0, 0);
  if (S.longHair) L(bx(0.2, 0.42, 0.06).translate(0, sh - 0.3, -0.12), hairC, 0, 0);
  if (S.beard) L(bx(0.22 * wd, 0.36, 0.1).translate(0, sh - 0.26, 0.13), hairC, 0, 0);
  if (S.cloak) L(bx(0.48 * wd, torso + hip * 0.55, 0.04).translate(0, hip * 0.45, -0.15), S.cloak, 0, 0);
  const g = merge(P, true);
  if (S.hunch) { const p = g.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i); if (y > hip) p.setZ(i, p.getZ(i) + (y - hip) * S.hunch); } }
  g.scale(S.h / 1.8 * wd, S.h / 1.8, S.h / 1.8);
  const pv = g.attributes.aPivot; for (let i = 0; i < pv.count; i++) pv.setX(i, pv.getX(i) * S.h / 1.8);
  return g;
}
function folkMaterial(time) {
  const m = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9 });
  m.onBeforeCompile = sh => {
    sh.uniforms.uTime = time;
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nattribute float aPart; attribute float aPivot; attribute vec3 aTint; attribute vec3 aWalk; uniform float uTime;')
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        float sw = sin(uTime * aWalk.y + aWalk.x) * aWalk.z;
        if (aPart > 1.5) { float side = position.x > 0.0 ? 1.0 : -1.0; float a = (aPart > 4.5 ? -0.8 : 1.0) * sw * side; float d = transformed.y - aPivot; transformed.y = aPivot + d * cos(a); transformed.z += d * sin(a); }
        transformed.y += abs(sw) * 0.025;`)
      .replace('#include <color_vertex>', '#include <color_vertex>\nif ((aPart > 0.5 && aPart < 1.5) || aPart > 4.5) vColor = aTint;');
  };
  return m;
}
/* Townsfolk for one near patch: everyone walks between doors, pausing now and then. */
function W3people(B, X0, Y0, hAt, opts = {}) {
  const grp = new THREE.Group(), time = { value: 0 };
  const doors = [];
  for (const b of B.list) {
    if (!FOLK[b.culture]) continue;
    const x = (b.x - X0) * MI, z = -(b.y - Y0) * MI, off = b.round ? b.w * 0.8 + 2 : b.d / 2 + 1.8;
    doors.push({ x: x + Math.sin(b.a) * off, z: z + Math.cos(b.a) * off, culture: b.culture, d: Math.hypot(x - G.px, z - G.pz) });
  }
  doors.sort((a, b) => a.d - b.d);
  const near = doors.filter(d => d.d < 1800).slice(0, opts.max || (innerWidth < 760 ? 140 : 320));
  const byKin = {}, agents = [];
  let seed = 1;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (const d of near) {
    const mix = FOLK[d.culture]; let r = rnd(), kin = mix[0][0];
    for (const [k, p] of mix) { if ((r -= p) <= 0) { kin = k; break; } }
    const n = d.culture === 'sunbaked' ? 2 : 1;
    for (let i = 0; i < n; i++) (byKin[kin] = byKin[kin] || []).push({ x: d.x + (rnd() - 0.5) * 4, z: d.z + (rnd() - 0.5) * 4, home: d });
  }
  for (const k in byKin) {
    const list = byKin[k], S = KIN[k];
    const geo = figure(k);
    const tint = new Float32Array(list.length * 3), walk = new Float32Array(list.length * 3);
    list.forEach((a, i) => { const c = lin(S.c[Math.floor(rnd() * S.c.length)]); tint.set([c.r, c.g, c.b], i * 3); walk.set([rnd() * 6.28, 7 + rnd() * 2, 0], i * 3); });
    geo.setAttribute('aTint', new THREE.InstancedBufferAttribute(tint, 3));
    geo.setAttribute('aWalk', new THREE.InstancedBufferAttribute(walk, 3));
    const mesh = new THREE.InstancedMesh(geo, folkMaterial(time), list.length);
    mesh.castShadow = true; mesh.frustumCulled = false;
    grp.add(mesh);
    list.forEach((a, i) => agents.push(Object.assign(a, { mesh, i, walk: geo.attributes.aWalk, tx: a.x, tz: a.z, wait: rnd() * 6, yaw: rnd() * 6.28, sp: 1.35 * (0.8 + rnd() * 0.4), sc: 0.93 + rnd() * 0.14 })));
  }
  const pool = near.length ? near : [{ x: 0, z: 0 }];
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s3 = new THREE.Vector3(), p3 = new THREE.Vector3(), upv = new THREE.Vector3(0, 1, 0);
  const floor = opts.floorAt || hAt;
  grp.userData.update = (dt) => {
    time.value += dt;
    const dirty = new Set();
    for (const a of agents) {
      let moving = false;
      if (a.wait > 0) a.wait -= dt;
      else {
        const dx = a.tx - a.x, dz = a.tz - a.z, d = Math.hypot(dx, dz);
        if (d < 0.6) {
          a.wait = 1 + rnd() * 7;
          const t = pool[Math.floor(rnd() * pool.length)];
          const far = Math.hypot(t.x - a.x, t.z - a.z) > 220;
          a.tx = (far ? a.home.x : t.x) + (rnd() - 0.5) * 6; a.tz = (far ? a.home.z : t.z) + (rnd() - 0.5) * 6;
        } else {
          const nx = a.x + dx / d * a.sp * dt, nz = a.z + dz / d * a.sp * dt;
          if (floor(nx, nz) === null) { a.tx = a.x; a.tz = a.z; } else { a.x = nx; a.z = nz; moving = true; }
          a.yaw = Math.atan2(dx, dz);
        }
      }
      const amp = moving ? 0.55 : 0;
      if (a.walk.getZ(a.i) !== amp) { a.walk.setZ(a.i, amp); dirty.add(a.walk); }
      p3.set(a.x, (floor(a.x, a.z) ?? 0) - 0.02, a.z); q.setFromAxisAngle(upv, a.yaw); s3.setScalar(a.sc);
      m4.compose(p3, q, s3); a.mesh.setMatrixAt(a.i, m4);
    }
    for (const w of dirty) w.needsUpdate = true;
    grp.children.forEach(m => { m.instanceMatrix.needsUpdate = true; });
  };
  grp.userData.update(0);
  grp.userData.agents = agents;
  return grp;
}

/* ---------------- landmarks seen from afar ----------------
   A world's great landmarks drawn beyond the near patch. None in the Known World yet: the Wall is in the terrain. */
function W3far(o) {
  const grp = new THREE.Group();
  grp.userData.update = () => {};
  return grp;
}
