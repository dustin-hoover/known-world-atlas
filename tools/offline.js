// The page must load nothing from any other site (no fonts, scripts, styles, analytics or data from elsewhere).
// build.js calls assertOffline on the assembled page and refuses to write it if anything would; links people click
// (<a href>) are fine. Its headless twin is tools/app_test.py, which records every request the running page makes and
// exits 3 if any leaves its own origin.
const LOADS = [
  [/<(?:script|link|img|iframe|frame|source|video|audio|embed|object|track|image|use|input)\b[^>]{0,400}?\b(?:src|href|data|poster|srcset)\s*=\s*["']?(?:https?:)?\/\/[^"'\s>]+/gi, 'an element loads from another site'],
  [/url\(\s*["']?(?:https?:)?\/\/[^)"']+/gi, 'a stylesheet url() points to another site'],
  [/@import\s+(?:url\()?\s*["']?(?:https?:)?\/\//gi, 'a stylesheet imports from another site'],
  [/\b(?:import|importScripts|fetch|EventSource|WebSocket|Worker|SharedWorker|sendBeacon)\s*\(\s*["'`](?:https?:|wss?:)?\/\/[^"'`]+/g, 'a script loads from another site'],
  [/\bfrom\s*["'`](?:https?:)?\/\/[^"'`]+/g, 'a module imports from another site'],
  [/\.src\s*=\s*["'`](?:https?:)?\/\/[^"'`]+/g, 'a script points an element at another site'],
  [/["'`]https?:\/\/[^"'`\s]+\.(?:m?js|css|woff2?|ttf|otf|wasm)(?:\?[^"'`\s]*)?["'`]/g, 'a script names a file on another site'],
  [/goatcounter|google-analytics|googletagmanager|plausible\.io|gc\.zgo\.at/gi, 'an analytics service'],
];
function findLoads(html) {
  const hits = [];
  for (const [re, why] of LOADS) for (const m of html.matchAll(re)) {
    hits.push(`${why}: ${m[0].slice(0, 140)}`);
  }
  return hits;
}
function assertOffline(html) {
  const hits = findLoads(html);
  if (hits.length) throw new Error('the page would load from other sites:\n  ' + hits.join('\n  '));
}
module.exports = { findLoads, assertOffline };
if (require.main === module) {
  const fs = require('fs');
  const f = process.argv[2] || require('path').join(__dirname, '..', 'site', 'index.html');
  const hits = findLoads(fs.readFileSync(f, 'utf8'));
  console.log(hits.length ? hits.join('\n') : 'offline: nothing loads from another site');
  process.exit(hits.length ? 1 : 0);
}
