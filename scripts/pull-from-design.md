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
- `build_legal.py` — builds `legal/Impressum.html` + `legal/Datenschutz.html`
  from `src/legal/*.html`, themed to CMON (terracotta + local fonts).
- `inject_head.py` — adds `<title>`, meta/OG, favicon, `lang="de"`; repoints the
  footer `#impressum`/`#datenschutz` links to the built pages; **removes the
  `#agb` link** (see below).

**Legal entity = the WHYKINGS GmbH** (confirmed 2026-07-28), same as the main
site + Academy — Impressum reuses the GmbH data. The Datenschutz is CMON-specific
(GitHub Pages hosting, e-mail/phone/WhatsApp contact, local fonts/libs, no forms/
payment/video). Refreshing fonts (new weights/families in the design): re-run the
css2 fetch (Safari UA) into `assets/fonts/`, regenerate `vendor/fonts-local.css`.

## ⚠️ Still open before public launch

- **AGB:** the template's footer linked to `#agb` but there is no AGB text yet, so
  `inject_head.py` removes that link. If CMON needs Coworking-AGB (rental terms,
  cancellation, house rules), add `src/legal/AGB.html`, extend `build_legal.py`,
  and restore the footer link in `inject_head.py`.
- **Favicon** is the wordmark `assets/cmon-logo.png` (wide, not square) — a proper
  square icon would look better in the browser tab.
- **Datenschutz** was adapted from an eRecht24 base + the Academy version; have it
  reviewed for CMON specifics before heavy public promotion.

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
