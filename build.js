// Assembles src/ into one self-contained page that loads nothing from any other site: the map engine, three.js and
// the fonts are inlined from node_modules. Writes dist/index.html (body only, for hosts that wrap the page
// themselves), dist/preview.html (a full document for local testing) and site/ (full documents plus the licence
// texts, for any static host).
const fs = require('fs');
const path = require('path');
const rd = f => fs.readFileSync(path.join(__dirname, f), 'utf8');
let html = rd('src/index.tpl.html');
const guard = (name, s) => { if (/<\/script/i.test(s)) throw new Error(name + ' contains a closing script tag'); return s; };
const put = (k, v) => { const i = html.indexOf(k); if (i < 0) throw new Error('template placeholder missing: ' + k); html = html.slice(0, i) + v + html.slice(i + k.length); };

// fonts: the faces the page and the map labels use, latin subsets, as data URIs (all under the SIL Open Font Licence)
const FONTS = [['im-fell-english', ['400', '400-italic']], ['im-fell-english-sc', ['400']],
  ['alegreya-sans', ['400', '400-italic', '500', '700']], ['ibm-plex-mono', ['400', '500']]];
let fontCss = '';
for (const [pkg, faces] of FONTS) for (const face of faces) for (const sub of ['latin', 'latin-ext']) {
  const f = `node_modules/@fontsource/${pkg}/${sub}-${face}.css`;
  if (!fs.existsSync(path.join(__dirname, f))) continue;
  fontCss += rd(f).replace(/src: url\(\.\/files\/([^)]+\.woff2)\) format\('woff2'\)[^;]*;/g, (_, file) =>
    `src: url(data:font/woff2;base64,${fs.readFileSync(path.join(__dirname, `node_modules/@fontsource/${pkg}/files/${file}`)).toString('base64')}) format('woff2');`);
}
put('/*FONTS_CSS*/', fontCss);
put('/*MAPLIBRE_CSS*/', rd('node_modules/maplibre-gl/dist/maplibre-gl.css'));
put('/*APP_CSS*/', rd('src/app.css'));
// the map engine (ES modules: the library, its worker and the code they share) and three.js, as text the page turns
// into modules of its own (see the loader in index.tpl.html and ground.js)
for (const [k, f] of [['MAPLIBRE_SHARED', 'maplibre-gl/dist/maplibre-gl-shared.mjs'], ['MAPLIBRE_MAIN', 'maplibre-gl/dist/maplibre-gl.mjs'],
  ['MAPLIBRE_WORKER', 'maplibre-gl/dist/maplibre-gl-worker.mjs'], ['THREE_JS', 'three/build/three.module.min.js']])
  put('/*' + k + '*/', guard(f, rd('node_modules/' + f).replace(/\n\/\/# sourceMappingURL=\S+\s*$/, '\n')));
// the terrain data the page builds is the same for the same sources: a hash of them names it in the browser's cache
const DATA_KEY = require('crypto').createHash('sha256').update(['geo.js', 'gen.js', 'rasters.js'].map(f => rd('src/' + f)).join('\n')).digest('hex').slice(0, 16);
put('/*DATA_KEY*/', DATA_KEY);
for (const [k, f] of [['GEN_JS', 'gen.js'], ['WX_JS', 'wx.js'], ['WORKER_JS', 'worker.js'], ['GEO_JS', 'geo.js'], ['ROUTES_JS', 'routes.js'], ['SOURCES_JS', 'sources.js'], ['AVATARS_JS', 'avatars.js'], ['RASTERS_JS', 'rasters.js'], ['AUDIO_JS', 'audio.js'], ['APP_JS', 'app.js'], ['GROUND_JS', 'ground.js']])
  put('/*' + k + '*/', guard(f, rd('src/' + f) + (f === 'ground.js' ? '\n' + rd('src/world3d.js') : '')));
require('./tools/offline.js').assertOffline(html);                    // nothing may load from another site
const ICON = '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' + encodeURIComponent(rd('src/icon.svg').trim()) + '">';
const head = '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' + ICON;
const wrap = body => '<!doctype html><html lang="en"><head>' + head + '</head><body>' + body + '</body></html>';
fs.mkdirSync(path.join(__dirname, 'dist'), { recursive: true });
fs.writeFileSync(path.join(__dirname, 'dist/index.html'), html);
fs.writeFileSync(path.join(__dirname, 'dist/preview.html'), wrap(html));
// site/: full documents ready for any static host (GitHub Pages, Netlify, Cloudflare Pages), with the licences of
// everything bundled into the page
fs.mkdirSync(path.join(__dirname, 'site/licenses'), { recursive: true });
fs.writeFileSync(path.join(__dirname, 'site/index.html'), wrap(html));
fs.writeFileSync(path.join(__dirname, 'site/favicon.svg'), rd('src/icon.svg'));
const LICENSES = [['maplibre-gl.txt', 'maplibre-gl/LICENSE.txt'], ['three.txt', 'three/LICENSE']]
  .concat(FONTS.map(([pkg]) => [`font-${pkg}.txt`, `@fontsource/${pkg}/LICENSE`]));
for (const [out, f] of LICENSES) fs.writeFileSync(path.join(__dirname, 'site/licenses', out), rd('node_modules/' + f));
fs.writeFileSync(path.join(__dirname, 'site/licenses/index.html'), wrap('<title>Licences</title><main style="font:15px/1.5 system-ui;max-width:42em;margin:2em auto;padding:0 16px">' +
  '<h1>Licences</h1><p>The atlas bundles these works, each under its own licence:</p><ul>' +
  LICENSES.map(([out, f]) => `<li><a href="${out}">${f.split('/').slice(0, -1).join('/')}</a></li>`).join('') + '</ul></main>'));
console.log('built dist/index.html', (html.length / 1024).toFixed(0) + ' KB');
