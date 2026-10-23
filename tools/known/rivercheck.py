"""Rule 18, rivers never climb, and rivers on their valley floors: measured on the generated ground.

  python3 tools/known/rivercheck.py            # every river; exit 1 on a FAIL
  python3 tools/known/rivercheck.py --json     # the numbers, for tools/known/gate.py

Each river's drawn course (gen.js riverLine, the line the imagery draws) is walked every quarter mile on the ground
gen.js makes at full DEM detail. A rise of more than 5 m within a mile, going downstream, FAILs (rule 18); a point
of the course more than 2 m above the lower of the two banks a mile and a half to either side is off its valley
floor (WARN when more than 2% of a river's points are; a bank within 3 miles of another river, at a confluence, is
left out). Runs the terrain code headless in Chromium (tools/known/terrain.html).
"""
import os, sys, json, asyncio
HERE = os.path.dirname(os.path.abspath(__file__))
RISE, WINDOW, BANK, BANK_TOL, OFF_FLOOR = 5.0, 1.0, 1.5, 2.0, 0.02

JS = """([STEP, WINDOW, BANK, BANK_TOL]) => {
  const out = [], B = GEN.beds();
  const nearOther = (x, y, i) => {               // a bank in another river's valley (a confluence) is not a fault
    const q = B.buckets.get(Math.floor(x / 4) * 100003 + Math.floor(y / 4)) || [];
    for (const k of q) {
      if (B.rid[k] === i) continue;
      const ax = B.ax[k], ay = B.ay[k], dx = B.bx[k] - ax, dy = B.by[k] - ay, L2 = dx * dx + dy * dy || 1e-9;
      const t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / L2));
      if (Math.hypot(x - ax - t * dx, y - ay - t * dy) < 3) return true;
    }
    return false;
  };
  GEO.RIVERS.forEach((r, i) => {
    const line = GEN.riverLine(r, i);
    const P = [[line[0][0], line[0][1], 0]];
    let acc = 0;
    for (let k = 1; k < line.length; k++) {
      const a = line[k - 1], b = line[k], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
      for (let u = (P[P.length - 1][2] + STEP) - acc; u <= L; u += STEP) P.push([a[0] + (b[0] - a[0]) * u / L, a[1] + (b[1] - a[1]) * u / L, acc + u]);
      acc += L;
    }
    const h = [], land = [];
    for (const [x, y] of P) { h.push(GEN.evaluate(x, y, 0.06)); land.push(GEN.R.s > 0 && GEN.F[15] < 0.5); }
    let worst = 0, at = null, rises = 0, off = 0, n = 0, lo = [];
    const win = Math.round(WINDOW / STEP);
    for (let j = 0; j < h.length; j++) {
      if (!land[j]) continue;
      let m = Infinity;
      for (let i = Math.max(0, j - win); i < j; i++) if (land[i]) m = Math.min(m, h[i]);
      const rise = h[j] - m;
      if (rise > worst) { worst = rise; at = [Math.round(P[j][0] * 10) / 10, Math.round(P[j][1] * 10) / 10]; }
      if (rise > 5) rises++;
      if (j % 4 === 0 && j > 0 && j < h.length - 1) {          // the banks, every mile
        const dx = P[j + 1][0] - P[j - 1][0], dy = P[j + 1][1] - P[j - 1][1], L = Math.hypot(dx, dy) || 1;
        const nx = -dy / L * BANK, ny = dx / L * BANK;
        const hl = GEN.evaluate(P[j][0] + nx, P[j][1] + ny, 0.06), wl = GEN.R.s > 0;
        const hr = GEN.evaluate(P[j][0] - nx, P[j][1] - ny, 0.06), wr = GEN.R.s > 0;
        if (wl && wr && !nearOther(P[j][0] + nx, P[j][1] + ny, i) && !nearOther(P[j][0] - nx, P[j][1] - ny, i)) { n++; if (h[j] > Math.min(hl, hr) + BANK_TOL) { off++; if (lo.length < 3) lo.push([Math.round(P[j][0]), Math.round(P[j][1])]); } }
      }
    }
    out.push({ name: r.name, miles: Math.round(acc), worst: Math.round(worst * 10) / 10, at, rises, off, banks: n, offAt: lo,
               top: Math.round(Math.max(...h)), mouth: Math.round(h[h.length - 1] * 10) / 10 });
  });
  return out;
}"""


async def measure():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        import glob
        exe = os.environ.get('PW_CHROME') or next(iter(sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome'))), None)
        b = await p.chromium.launch(executable_path=exe)
        pg = await b.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + os.path.join(HERE, 'terrain.html'))
        await pg.wait_for_function('window.READY || false', timeout=300000)
        ready = await pg.evaluate('window.READY')
        rows = await pg.evaluate(JS, [0.25, WINDOW, BANK, BANK_TOL])
        await b.close()
        if errs: raise RuntimeError('; '.join(errs))
        return ready, rows


def main():
    ready, rows = asyncio.run(measure())
    if '--json' in sys.argv: print(json.dumps({'ready': ready, 'rivers': rows})); return
    print(f"terrain ready: rasters {ready['rasters']} ms, init (river beds) {ready['init']} ms")
    bad = 0
    for r in rows:
        f = r['rises'] > 0
        floor = r['banks'] and r['off'] / r['banks'] > OFF_FLOOR
        bad += f
        print(f"{'FAIL' if f else 'WARN' if floor else 'PASS'}  {r['name']:30s} {r['miles']:5d} mi  worst rise {r['worst']:7.1f} m"
              f"{' at ' + str(r['at']) if r['worst'] > RISE else ''}  off the valley floor {r['off']}/{r['banks']}"
              f"{' e.g. ' + str(r['offAt']) if r['off'] else ''}  source {r['top']} m, mouth {r['mouth']} m")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
