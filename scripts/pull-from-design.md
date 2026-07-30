# Pulling the latest from Claude Design (CMON)

Claude does this through the authenticated browser session (Claude-in-Chrome),
because the Claude Design API needs your claude.ai login. These are the steps
Claude runs — you just say **"deploy cmon"**.

## Project

- **Project ID:** `0517deb9-ca31-46e2-a79d-ecb1c8669be7`
- **Entry file:** the top-level **`CMON Website 1a Template.dc.html`** → published as `index.html`
- **API base:** `https://claude.ai/design/anthropic.omelette.api.v1alpha.OmeletteService/`
- **Auth:** claude.ai session cookies (same-origin fetch from an open claude.ai tab)

## ⚠️ Which file is the source?

`ListFiles` first, then pick by rule — do NOT hardcode a name:

- **Use** the top-level `*.dc.html` that is the current design (as of 2026-07-28:
  `CMON Website 1a Template.dc.html`, title "Homepage | CMON!").
- **Never** publish `CMON Website Redesign (ARCHIVE).dc.html` — it's explicitly
  archived. If more than one non-archive `.dc.html` exists, stop and ask which is
  canonical.
- `doc-page.js` in the project is the design-tool doc viewer, NOT a dependency of
  the entry — dynamic discovery (below) correctly skips it.

## We host the SOURCE, not an offline export

The design is hosted as its Claude Design source (client-rendered) plus its
dependencies, so it always reflects the current design without a re-export.

## ⚠️ Discover the file list DYNAMICALLY

Pull the source first, then parse **its own** references — never hardcode.

```js
const PID = '0517deb9-ca31-46e2-a79d-ecb1c8669be7';
const BASE = 'https://claude.ai/design/anthropic.omelette.api.v1alpha.OmeletteService/';
const get = async (path) => (await fetch(BASE+'GetFile',
  { method:'POST', headers:{'Content-Type':'application/json','Connect-Protocol-Version':'1'},
    credentials:'include', body: JSON.stringify({ projectId: PID, path }) })).json();

// 1. pull the source, decode it
const src = await get('CMON Website 1a Template.dc.html');
const html = new TextDecoder().decode(Uint8Array.from(atob(src.content), c => c.charCodeAt(0)));

// 2. derive the dependency list FROM the source (no hardcoding)
const refs = [...html.matchAll(/(?:src|href)="((?:sections\/|_ds\/|assets\/|uploads\/)[^"]+|(?:\.\/)?[\w.-]+\.js)"/g)]
  .map(m => m[1].replace(/^\.\//,'')).filter(p => !p.startsWith('http'));
// → currently: support.js + assets/*.jpg|png (cmon-logo, hero-lounge, g-*, portrait-*)

// 3. bundle code files into cm_code.json, images into cm_images.json,
//    download them (bytes stay out of context)
```

Note the prefix: **`cm_`** for CMON bundles — `wk_` = main site, `ak_` = Academy,
so the three never get mixed up in ~/Downloads.

## Then, locally

```bash
python3 scripts/unpack_code.py        # newest cm_code*.json -> repo (source -> index.html)
python3 scripts/unpack_images.py      # only when images changed
scripts/deploy.sh "describe what changed"   # commit + push + request Pages build
```

## Images (only when they change)

Images live under `assets/` and are committed. Re-pull only if a local render
shows broken images: bundle-fetch them as `cm_images.json`, then
`python3 scripts/unpack_images.py`.

## Post-processing applied on every deploy (deploy.sh)

The design source is missing several things a live site needs; three idempotent
scripts re-apply them after each pull (so a re-pull never loses them):

- `localize_assets.py` — rewrites the Google Fonts `<link>` in index.html to the
  locally vendored `vendor/fonts-local.css` (fonts in `assets/fonts/`), and the
  three unpkg React/Babel URLs in support.js to `vendor/*.js`. **No third-party
  request** remains (GDPR). React/ReactDOM/Babel are byte-identical to unpkg
  (match the SRI hashes support.js declares).
- `build_legal.py` — builds `legal/Impressum.html` + `legal/Datenschutz.html` +
  `legal/AGB.html` from `src/legal/*.html`, themed to CMON (terracotta + local fonts).
- `inject_head.py` — adds `<title>`, meta/OG, favicon, `lang="de"`; repoints the
  footer `#impressum`/`#datenschutz`/`#agb` links to the built pages under legal/.

**Legal entity = the WHYKINGS GmbH** (confirmed 2026-07-28), same as the main
site + Academy — Impressum reuses the GmbH data. The Datenschutz is CMON-specific
(GitHub Pages hosting, e-mail/phone/WhatsApp contact, local fonts/libs, no forms/
payment/video). Refreshing fonts (new weights/families in the design): re-run the
css2 fetch (Safari UA) into `assets/fonts/`, regenerate `vendor/fonts-local.css`.

## ⚠️ Still open before public launch

- **Legal review:** `src/legal/AGB.html` was derived from a CMON Untermietvertrag
  (Fixed-Desk terms — see below) and Datenschutz from an eRecht24 base + the
  Academy version. Both are careful drafts — have a lawyer review the AGB clauses
  (Kaution, Haftung, Kündigung fall under §§ 305 ff. BGB) before heavy promotion.
- Favicon is now the design's own square `assets/favicon.png` (128×128).

## Legal pages: source of the AGB

`legal/AGB.html` is built from `src/legal/AGB.html`, whose terms were extracted
from `~/Desktop/CMON/Untermietverträge/…/…_ENTWURF.pdf` (Fixed-Desk Untermietvertrag):
Mietgegenstand (Büroplatz + höhenverstellbarer Tisch/Stuhl, Gemeinschaftsflächen,
1 Schlüssel, keine eigenen Möbel, keine baulichen Änderungen), Zugang Mo–So 0–24 h
(Wochenende entfällt bei Veranstaltung, 24 h Vorlauf), unbefristet / 3 Monate zum
Monatsende, 320 € netto zzgl. USt all-inclusive (fällig 27. des Vormonats), Kaution
1 Nettomiete. NO personal data or IBAN from the contract is in the AGB.

## Gotchas

- The source's `<script data-omelette-injected>` harness is re-minified
  server-side on every fetch, so `index.html` can show a diff — noise, not a real
  change. It's inert when hosted standalone (self-disables when
  `window.parent === window`).
- `.nojekyll` must stay (so GitHub serves any `_ds/` underscore folder if one is
  added later).
- The Chrome extension disconnects often mid-session — reconnect and retry.
- DNS: `cmon.rocks` nameservers are at all-inkl (`ns5`/`ns6.kasserver.com`).
  `www` must CNAME to `theWHYKINGS.github.io.` and the apex A records must be the
  4 GitHub Pages IPs, or the custom domain won't serve from GitHub Pages.
